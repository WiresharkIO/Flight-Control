from rockit import *
from rockit import FreeTime, MultipleShooting, Ocp
import numpy as np
from numpy import pi, cos, sin, tan, square
from casadi import vertcat, horzcat, sumsqr, Function, exp, vcat
import matplotlib.pyplot as plt

dt       = 0.1              # time between steps in seconds (step_horizon)
N        = 10               # number of look ahead steps
Nsim     = 10               # simulation time
nx       = 8                # the system is composed of 8 states
nu       = 4                # the system has 4 control inputs

xf       = 1
yf       = 1
zf       = 1

#-------------------- Logging variables---------------------------------
x_hist         = np.zeros((Nsim+1, N+1))
y_hist         = np.zeros((Nsim+1, N+1))
z_hist         = np.zeros((Nsim+1, N+1))
phi_hist       = np.zeros((Nsim+1, N+1))
vx_hist        = np.zeros((Nsim+1, N+1))
vy_hist        = np.zeros((Nsim+1, N+1))
vz_hist        = np.zeros((Nsim+1, N+1))
vphi_hist      = np.zeros((Nsim+1, N+1))

ux_hist         = np.zeros((Nsim+1, N+1))
uy_hist         = np.zeros((Nsim+1, N+1))
uz_hist         = np.zeros((Nsim+1, N+1))
uphi_hist       = np.zeros((Nsim+1, N+1))

# -------------drone model from reference paper-------------
# -----------------model constants--------------------------
k_x      = 1
k_y      = 1
k_z      = 1
k_phi    = pi/180
tau_x    = 0.8355
tau_y    = 0.7701
tau_z    = 0.5013
tau_phi  = 0.5142

#------------ initialize OCP  -------------
ocp = Ocp(T = N*dt)

#Define states - a reduced state vector - x = [x y z phi vx vy vz vphi ]T
x        = ocp.state()
y        = ocp.state()
z        = ocp.state()
phi      = ocp.state()
vx       = ocp.state()
vy       = ocp.state()
vz       = ocp.state()
vphi     = ocp.state()

#Defince controls
ux       = ocp.control()
uy       = ocp.control()
uz       = ocp.control()
uphi     = ocp.control()

# Specification of the ODEs - a nonlinear model dx = f(x, u) defined by the
# set of equations:
ocp.set_der(x   ,   vx*cos(phi) - vy*sin(phi))
ocp.set_der(y   ,   vx*sin(phi) + vy*cos(phi))
ocp.set_der(z   ,   vz)
ocp.set_der(phi ,   vphi)
ocp.set_der(vx  ,   (-vx + k_x*ux)/tau_x)
ocp.set_der(vy  ,   (-vy + k_y*uy)/tau_y)
ocp.set_der(vz  ,   (-vz + k_z*uz)/tau_z)
ocp.set_der(vphi,   (-vphi + k_phi*uphi)/tau_phi)

#------------------------------- Control constraints ----------------------
ocp.subject_to(-1 <= (ux    <= 1))
ocp.subject_to(-1 <= (uy    <= 1))
ocp.subject_to(-1 <= (uz    <= 1))
ocp.subject_to(-1 <= (uphi  <= 1))

p = vertcat(x,y,z)             # a point in 3D

# Define initial parameter
X_0 = ocp.parameter(nx)
X = vertcat(x, y, z, phi, vx, vy, vz, vphi)

#initial point
ocp.subject_to(ocp.at_t0(X) == X_0 )
ocp.subject_to( 0  <=  (x    <= 1))
ocp.subject_to( 0  <=  (y    <= 1))
ocp.subject_to( 0  <=  (z    <= 1))

#----------------- reach end point (1,1,1) -------------------
pf = ocp.parameter(3)
p_final = vertcat(xf,yf,zf) # end point

"""
Set a value for a parameter
All variables must be given a value before an optimal control problem can be solved.
"""
ocp.set_value(pf, p_final) # p_final assigned to pf before solving the OCP.

# Variables are unknowns in the Optimal Control problem for which we seek
# optimal values.
slack_tf_x = ocp.variable()
slack_tf_y = ocp.variable()
slack_tf_z = ocp.variable()

ocp.subject_to(slack_tf_x >= 0)
ocp.subject_to(slack_tf_y >= 0)
ocp.subject_to(slack_tf_z >= 0)

# Evaluate a signal at the end of the horizon
ocp.subject_to((ocp.at_tf(x) - pf[0]) <= slack_tf_x)
ocp.subject_to((ocp.at_tf(y) - pf[1]) <= slack_tf_y)
ocp.subject_to((ocp.at_tf(z) - pf[2]) <= slack_tf_z)

ocp.add_objective(10*(slack_tf_x**2 + slack_tf_y**2 + slack_tf_z**2))

#---------------- constraints on velocity ---------------------------------

v_final = vertcat(0,0,0,0)

ocp.subject_to(ocp.at_tf(vx) == 0)
ocp.subject_to(ocp.at_tf(vy) == 0)
ocp.subject_to(ocp.at_tf(vz) == 0)
ocp.subject_to(ocp.at_tf(vphi) == 0)

#------------------------------  Objective Function ------------------------

ocp.add_objective(5*ocp.integral(sumsqr(p-pf)))
ocp.add_objective((1e-6)*ocp.integral(sumsqr(ux + uy + uz + uphi)))

#-------------------------  Pick a solution method: ipopt --------------------
options = {"ipopt": {"print_level": 0}}
# options = {'ipopt': {"max_iter": 1000, 'hessian_approximation':'limited-memory', 'limited_memory_max_history' : 5, 'tol':1e-3}}
options["expand"] = True
options["print_time"] = True
ocp.solver('ipopt', options)

#-------------------------- try other solvers here -------------------
# Multiple Shooting
ocp.method(MultipleShooting(N=N, M=2, intg='rk') )

#-------------------- Set initial-----------------

ux_init = np.ones(N)
uy_init = np.ones(N)
uz_init = np.zeros(N)
uphi_init = np.zeros(N)

vx_init = np.empty(N)
vx_init[0] = 0
vy_init = np.empty(N)
vy_init[0] = 0
vz_init = np.empty(N)
vz_init[0] = 0
vphi_init = np.empty(N)
vphi_init[0] = 0

x_init = np.empty(N)
x_init[0] = 0
y_init = np.empty(N)
y_init[0] = 0
z_init = np.empty(N)
z_init[0] = 0
phi_init = np.empty(N)
phi_init[0] = 0

for i in range(1,N):
    vx_init[i]   = vx_init[i-1] + ux_init[i-1]*dt
    vy_init[i]   = vy_init[i-1] + uy_init[i-1]*dt
    vz_init[i]   = vz_init[i-1] + uz_init[i-1]*dt
    vphi_init[i] = vphi_init[i-1] + uphi_init[i-1]*dt

    phi_init[i] = phi_init[i-1] + vphi_init[i-1]*dt
    z_init[i]   = z_init[i-1] + vz_init[i-1]*dt
    x_init[i]   = x_init[i-1] + ((vx_init[i-1]*cos(phi_init[i-1])) - (vy_init[i-1]*sin(phi_init[i-1])))*dt
    y_init[i]   = y_init[i-1] + ((vx_init[i-1]*sin(phi_init[i-1])) + (vy_init[i-1]*cos(phi_init[i-1])))*dt


ocp.set_initial(x, x_init)
ocp.set_initial(y, y_init)
ocp.set_initial(z, z_init)
ocp.set_initial(phi, phi_init)
ocp.set_initial(vx, vx_init)
ocp.set_initial(vy, vy_init)
ocp.set_initial(vz, vz_init)
ocp.set_initial(vphi, vphi_init)

ocp.set_initial(ux, ux_init)
ocp.set_initial(uy, uy_init)
ocp.set_initial(uz, uz_init)
ocp.set_initial(uphi, uphi_init)

#---------------- Solve the OCP for the first time step--------------------

# First waypoint is current position
index_closest_point = 0

current_X = vertcat(0,0,0,0,0,0,0,0)
ocp.set_value(X_0, current_X)

# Solve the optimization problem
try:
    sol = ocp.solve()
except:
    ocp.show_infeasibilities(1e-6)
    sol = ocp.non_converged_solution


# Get discretized dynamics as CasADi function to simulate the system
Sim_system_dyn = ocp._method.discrete_system(ocp)

# ----------------------- Log data for post-processing---------------------

t_sol, x_sol = sol.sample(x, grid='control')
t_sol, y_sol = sol.sample(y, grid='control')
t_sol, z_sol = sol.sample(z, grid='control')
t_sol, phi_sol = sol.sample(phi, grid='control')
t_sol, vx_sol = sol.sample(vx, grid='control')
t_sol, vy_sol = sol.sample(vy, grid='control')
t_sol, vz_sol = sol.sample(vz, grid='control')
t_sol, vphi_sol = sol.sample(vphi, grid='control')

t_sol, ux_sol = sol.sample(ux, grid='control')
t_sol, uy_sol = sol.sample(uy, grid='control')
t_sol, uz_sol = sol.sample(uz, grid='control')
t_sol, uphi_sol = sol.sample(uphi, grid='control')

t_sol, sx_sol = sol.sample(slack_tf_x, grid='control')
t_sol, sy_sol = sol.sample(slack_tf_y, grid='control')
t_sol, sz_sol = sol.sample(slack_tf_z, grid='control')

x_hist[0, :] = x_sol
y_hist[0, :] = y_sol
z_hist[0, :] = z_sol
phi_hist[0, :] = phi_sol
vx_hist[0, :] = vx_sol
vy_hist[0, :] = vy_sol
vz_hist[0, :] = vz_sol
vphi_hist[0, :] = vphi_sol

print(current_X[0])
print(current_X[1])
print(current_X[2])

# ------------------ plot function-------------------
def plotxy( x_hist_1, y_hist_1, opt, x_sol, y_sol):
    # x-y plot
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(111)

    plt.xlabel('x pos [m]')
    plt.ylabel('y pos [m]')
    plt.xlim(0, 1.1)
    plt.ylim(0, 1.1)
    plt.title('solution in x,y')
    ax.set_aspect('equal', adjustable='box')

    ts = np.linspace(0, 2 * pi, 1000)
    plt.plot(xf, yf, 'ro', markersize=10)

    if opt == 1:
        plt.plot(x_sol, y_sol, 'go')
        plt.plot(x_hist[:, 0], y_hist[:, 0], 'bo', markersize=3)

    else:
        plt.plot(x_hist[:, 0], y_hist[:, 0], 'bo', markersize=3)

    plt.show(block=True)


# ----------------- Simulate the MPC solving the OCP ----------------------

clearance_v = 1e-5  # should become lower if possible
clearance = 1e-3
local_min_clearance = 1e-1
i = 0

intermediate_points = []
intermediate_points_required = False
new_path_not_needed = False
intermediate_points_index = 0
is_stuck = False

trajectory_x = np.zeros((Nsim + 1, 10))
trajectory_y = np.zeros((Nsim + 1, 10))

obj = 10 * (sx_sol[0] + sy_sol[0] + sz_sol[0]) + 10 * (sumsqr(current_X[0:3] - p_final)) + (1e-6) * (
    sumsqr(ux_sol[0] + uy_sol[0] + uz_sol[0] + uphi_sol[0]))

t_tot = 0

while True:

    print("timestep", i + 1, "of", Nsim)

    plotxy( x_hist[0:i, 0], y_hist[0:i, 0], 1, x_sol, y_sol)

    ux_hist[i, :] = ux_sol
    uy_hist[i, :] = uy_sol
    uz_hist[i, :] = uz_sol
    uphi_hist[i, :] = uphi_sol

    # Combine first control inputs
    current_U = vertcat(ux_sol[0], uy_sol[0], uz_sol[0], uphi_sol[0])

    # Simulate dynamics (applying the first control input) and update the current state
    current_X = Sim_system_dyn(x0=current_X, u=current_U, T=dt)["xf"]

    t_tot = t_tot + dt

    print(f' x: {current_X[0]}')
    print(f' y: {current_X[1]}')
    print(f' z: {current_X[2]}')


    error_v = sumsqr(current_X[4:8] - v_final)

    if intermediate_points_required:
        error = sumsqr(current_X[0:3] - intermediate_points[intermediate_points_index - 1])
    else:
        error = sumsqr(current_X[0:3] - p_final)

    if is_stuck or i == Nsim:
        break

    if intermediate_points_index == len(intermediate_points):  # going to end goal
        clearance = 1e-3
    else:
        clearance = 1e-2

    if error < clearance:
        if intermediate_points_index == len(intermediate_points):
            print('Location reached, now reducing veolcity to zero')

            if error_v < clearance_v:
                print('Desired goal reached!')
                break

        else:
            print('Intermediate point reached! Diverting to next point.')
            intermediate_points_index = intermediate_points_index + 1
            ocp.set_value(pf, vcat(intermediate_points[intermediate_points_index - 1]))

    # Set the parameter X0 to the new current_X
    ocp.set_value(X_0, current_X)

    # Solve the optimization problem
    try:
        sol = ocp.solve()
    except:
        ocp.show_infeasibilities(1e-6)
        sol = ocp.non_converged_solution
        break

    # Log data for post-processing
    t_sol, x_sol = sol.sample(x, grid='control')
    t_sol, y_sol = sol.sample(y, grid='control')
    t_sol, z_sol = sol.sample(z, grid='control')
    t_sol, phi_sol = sol.sample(phi, grid='control')
    t_sol, vx_sol = sol.sample(vx, grid='control')
    t_sol, vy_sol = sol.sample(vy, grid='control')
    t_sol, vz_sol = sol.sample(vz, grid='control')
    t_sol, vphi_sol = sol.sample(vphi, grid='control')

    t_sol, ux_sol = sol.sample(ux, grid='control')
    t_sol, uy_sol = sol.sample(uy, grid='control')
    t_sol, uz_sol = sol.sample(uz, grid='control')
    t_sol, uphi_sol = sol.sample(uphi, grid='control')

    t_sol, sx_sol = sol.sample(slack_tf_x, grid='control')
    t_sol, sy_sol = sol.sample(slack_tf_y, grid='control')
    t_sol, sz_sol = sol.sample(slack_tf_z, grid='control')

    x_hist[i + 1, :] = x_sol
    y_hist[i + 1, :] = y_sol
    z_hist[i + 1, :] = z_sol
    phi_hist[i + 1, :] = phi_sol
    vx_hist[i + 1, :] = vx_sol
    vy_hist[i + 1, :] = vy_sol
    vz_hist[i + 1, :] = vz_sol
    vphi_hist[i + 1, :] = vphi_sol

    # --------------------- Initial guess
    ocp.set_initial(x, x_sol)
    ocp.set_initial(y, y_sol)
    ocp.set_initial(z, z_sol)
    ocp.set_initial(phi, phi_sol)
    ocp.set_initial(vx, vx_sol)
    ocp.set_initial(vy, vy_sol)
    ocp.set_initial(vz, vz_sol)
    ocp.set_initial(vphi, vphi_sol)

    i = i + 1

    obj_old = obj
    obj = 10 * (sx_sol[0] + sy_sol[0] + sz_sol[0]) + 10 * (sumsqr(current_X[0:3] - p_final)) + (1e-6) * (
        sumsqr(ux_sol[0] + uy_sol[0] + uz_sol[0] + uphi_sol[0]))

    print("This is obj", obj)

    trajectory_x[i, :] = np.zeros(10)
    trajectory_y[i, :] = np.zeros(10)
# ------------------- Results

print(f'Total execution time is: {t_tot}')

plotxy( x_hist[0:i, 0], y_hist[0:i, 0], 0, x_sol, y_sol)

timestep = np.linspace(0, t_tot, len(ux_hist[0:i, 0]))

fig2 = plt.figure(dpi=300, figsize=(4, 2))
plt.plot(timestep, ux_hist[0:i, 0], "-b", label="ux")
plt.plot(timestep, uy_hist[0:i, 0], "-r", label="uy")
plt.plot(timestep, uz_hist[0:i, 0], "-g", label="uz")
plt.plot(timestep, uphi_hist[0:i, 0], "-k", label="uphi")
plt.title("Control Inputs")
plt.ylim(-1.02, 1.02)
plt.xlabel("Time (s)")
plt.ylabel("Control Inputs (m/s^2)")
# plt.legend(loc="upper right")
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show(block=True)

fig3 = plt.figure(dpi=300, figsize=(4, 2))
plt.plot(timestep, vx_hist[0:i, 0], "-b", label="vx")
plt.plot(timestep, vy_hist[0:i, 0], "-r", label="vy")
plt.plot(timestep, vz_hist[0:i, 0], "-g", label="vz")
plt.plot(timestep, vphi_hist[0:i, 0], "-k", label="vphi")
plt.title("Velocity")
plt.xlabel("Time (s)")
plt.ylabel("Velocity (m/s)")
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show(block=True)

fig4 = plt.figure(dpi=300, figsize=(4, 2))
plt.plot(timestep, x_hist[0:i, 0], "b.", label="x")
plt.plot(timestep, y_hist[0:i, 0], "r.", label="y")
plt.plot(timestep, z_hist[0:i, 0], "g.", label="z")
plt.plot(timestep, phi_hist[0:i, 0], "k.", label="phi")
plt.plot(timestep, yf * np.ones(i), 'r--', linewidth=0.5, label='y goal')
plt.plot(timestep, zf * np.ones(i), 'g--', linewidth=0.5, label='x and z goal')
plt.title("Position")
plt.xlabel("Time (s)")
plt.ylabel("Positon (m)")
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show(block=True)