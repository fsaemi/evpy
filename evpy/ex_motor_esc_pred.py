"""
Example file which demonstrates the following functions:
    1. set_throttle() - predict motor throttle to achieve desired speed
    2. motor_pred() - predict motor efficiency at measured speed & torque
    3. esc_pred() - predict ESC efficiency under estimated motor load
    
Data flow:
    Torque & speed measurements from experiment
    ||
    ||
    \/
    Motor model ==> motor efficiency prediction
    ||
    ||
    \/
    ESC model ==> ESC efficiency prediction
"""

#import libraries
import numpy as np
import matplotlib.pyplot as plt
import evpy as ev

#global constants
RPM2RADS = 2.0*np.pi/60.0

# Motor specs (KDE 2814XF-515)
kt = 0.0185 #[N.m/A]
Rm = 0.130 #[Ohms]
I0 = 0.3 #[A]

# ESC specs (guesstimates)
f_pwm = 12E3 #[Hz]
Rds_on = 1E-3 #[Ohms]
T_trans = 1E-6 #[s]
P_qui = 0.25 #[W]

# load experimental data
exp_data = np.loadtxt("ex_motor_esc_data.txt",delimiter='\t',skiprows=2)
Vdc = np.average(exp_data[:,0]) #[V]
w_xp = exp_data[:,1] #[rad/s]
M_xp = exp_data[:,2] #[N.m]
n_mot_xp = exp_data[:,3] #[%]
n_esc_xp = exp_data[:,4] #[%]

# plot experimental data
fig,ax = plt.subplots(nrows=1,ncols=2,sharex=True)
N_xp = w_xp/RPM2RADS #[rev/min]

# plot experiment measurements
ax[0].plot(N_xp,M_xp*1E3,'.',markersize=10)
ax[0].set_title("Propeller torque [mN.m]")
ax[1].plot(N_xp,n_mot_xp*100.0,'.',markersize=10,label="Motor exp")
ax[1].set_title("Motor efficiency [%]")
ax[1].plot(N_xp,n_esc_xp*100.0,
           'x',markersize=7,markeredgewidth=2,label="ESC exp")
ax[1].set_title("Efficiency [%]")

# predictions
d_mdl = ev.set_throttle(w_xp,Vdc,kt) #[-]
n_mot_mdl = np.zeros(d_mdl.size) #[-]
n_esc_mdl = np.zeros(d_mdl.size) #[-]
for i in range(d_mdl.shape[0]):
    _,Pac,n_mot,Iac = ev.motor_pred(
        w_xp[i],M_xp[i],d_mdl[i],Vdc,kt,Rm,I0) #[-]
    _,_,n_esc,_ = ev.esc_pred(
        Iac,Pac,d_mdl[i],Vdc,f_pwm,Rds_on,T_trans,P_qui) #[-]
    n_mot_mdl[i] = n_mot
    n_esc_mdl[i] = n_esc
    
# plot predictions
ax[1].plot(N_xp,n_mot_mdl*100.0,linewidth=2,label="Motor model") #[%]
ax[1].plot(N_xp,n_esc_mdl*100.0,'--',linewidth=2,label="ESC model") #[%]

#plot adjustments
ax[0].set_ylim([20,50])
ax[1].legend()
ax[1].set_xlim([4E3, 6.5E3])
ax[1].set_ylim([50, 100])
for axis in ax:
    axis.grid(True)
    axis.set_xlabel('Shaft speed [rev/min]')
fig.tight_layout()

plt.show()