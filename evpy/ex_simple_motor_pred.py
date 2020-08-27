import numpy as np
import matplotlib.pyplot as plt
import evpy as ev

# sample specs of KDE 2304XF-2350 motor
kv = 2350.0 #[rpm/V]
kt = 0.0041 #[N.m/A]
Rm = 0.091 #[Ohms]
I0 = 0.7 #[A]

# sample voltage from a 2S battery, 50% throttle
V_batt = 2*4.2 #[V]
d = 50.0/100.0 #[-]

# generate speed range based on applied voltage
V_app = V_batt*d #[V]
N_max = kv*V_app #[rpm]
N_range = np.linspace(0,N_max,num=1000) #[rpm]
w_range = N_range*(np.pi/30.0) #[rad/s]

# generate and plot predictions
T,P_out,I,P_in,n = ev.motor_pred(V_batt,d,Rm,kt,I0,w_range)

# plot results versus speed
fig,ax = plt.subplots(1,3,sharex=True)
for axis in ax:
    axis.set_xlabel("Rotational speed [rev/min]")
    axis.grid()

ax[0].plot(N_range,T*1e3)
ax[0].set_ylabel("Torque [N.m]")
ax[1].plot(N_range,P_out,label="Output")
ax[1].set_ylabel("Power [W]")
ax[2].plot(N_range,n*100)
ax[2].set_ylabel("Efficiency [%]")

plt.tight_layout()
plt.show()