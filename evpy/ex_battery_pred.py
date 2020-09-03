import numpy as np
import matplotlib.pyplot as plt
import evpy as ev

# battery specs
Q_cell = 0.61 #[A*hr], 610 mA*hr
R_cell = 70e-3 #[Ohms]

# create discharge test
t = np.linspace(0,1.0,100) #[s], 1 hour sim
I_amp = 1.22 #[A] amplitude of constant current draw from battery
I_cmd = I_amp*np.ones(t.shape) #[A] commanded current vector

# compute only the voltage drop (ignoring DOD, SOC returned values)
V_pred = ev.batt_pred(I_cmd,t,Q_cell,R_cell)[0] #capture only first output

# extract only time+data above 3.3 V
y = V_pred[V_pred>3.3] #[V]
x = t[V_pred>3.3]*60.0 #[min]

batt_fig,batt_ax = plt.subplots(1,1)
batt_ax.plot(x,y)
batt_ax.set_xlabel("Time [min]")
batt_ax.set_ylabel("Terminal voltage [V]")
batt_fig.suptitle("Battery performance at 2X rated current for 1 hr")
batt_ax.grid(True)