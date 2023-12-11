# -*- coding: utf-8 -*-
"""
Example file for using battery prediction function.

results show how drawing more current from battery increases internal losses
"""

#%% IMPORT LIBRARIES
import numpy as np
import evpy as ev
import matplotlib.pyplot as plt

#%% SET BATTERY SPECS
Q_ampHr = 2.0 #battery capacity [A.hr]
Rcell = 30E-3 #resistance of each battery cell [Ohms]
n_series = 4 #number of cells in series [-]
disc_Crate = [1,2,3,4] #constant-current discharge C rate [1/hr]


#%% MAIN + PLOT
t = np.linspace(0,3600,num=3601) #time vector for simulation [s]  
Qrated = 3600*Q_ampHr #[C or A*s]
fig,ax = plt.subplots(1,1,figsize=(5,5))

for i,C in enumerate(disc_Crate):
    disc_I = Q_ampHr*C
    Idisc = disc_I*np.ones(t.shape) #(constant) discharge current vector
    Qdisc = np.cumsum(Idisc) #cumulative discharge vs. time [C or A*s]
    dod = Qdisc/Qrated #[-]
    dod[dod>1.0] = np.nan
    Vsoc = ev.soc_volts(1-dod) #predict per-cell ideal voltage
    Vterm = Vsoc-(Rcell*Idisc) #per-cell terminal voltage
    
    #plot total voltage (all cells) in minutes for diff rates
    ax.plot(t/60,n_series*Vterm,label="{:d}C".format(C),linewidth=1*C)

ax.grid(True)
ax.set_ylim([12,17])
ax.set_xlabel("Time [min]",fontweight='bold')
ax.set_title("Battery terminal voltage[V]",fontweight='bold')
ax.legend()
plt.subplots_adjust(top=0.929,bottom=0.117,left=0.085,
                    right=0.97, hspace=0.2, wspace=0.2)
