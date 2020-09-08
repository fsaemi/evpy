import numpy as np
import matplotlib.pyplot as plt
import evpy as ev

# sample specs of KDE 2304XF-2350 motor
kv = 2350.0 #[rpm/V]
kt = 0.0041 #[N.m/A]
R = 0.091 #[Ohms]
I0 = 0.7 #[A]

# set simulation parameters
NPoints = 100 # array size for efficiency calculation
T_rated = 200e-3 # rated torque in N.m
N_rated = 20e3 # rated speed in rev/min
V_dc = 8 # [V]

# calculate motor torque/speed/efficiency contour
N_array, T_array, n_array = ev.motor_contour(N_rated,T_rated,kt,R,I0)

# plot an efficiency filled contour
plt.contourf(N_array,T_array,n_array*100,cmap='jet')
plt.colorbar()
plt.xlabel('Speed [rev/min]')
plt.ylabel('Torque [mN.m]')
plt.title("Sample torque/speed/efficiency contour")
plt.tight_layout()

plt.show()