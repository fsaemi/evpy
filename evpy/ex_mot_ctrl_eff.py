# -*- coding: utf-8 -*-
"""
Example file for using mot_eff and ctrl_eff functions.
to predict motor and controller losses (efficiency) respectively.

NOTE: I symbolize torque with M rather than T.
I reserve T to symbolize temperature in future models.

Resulting plots show motor efficiency tends to increase with torque and speed
(especially speed) while controller efficiency is most sensitive to speed
"""

#%% IMPORT LIBRARIES
import evpy as ev
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

#%% CUSTOM CONSTANTS AND FUNCTIONS
RPM2RADS = np.pi/30.0

def cust_fmt(x):
    s = f"{x:.1f}"
    if s.endswith("0"):
        s = f"{x:.0f}"
    return rf"{s} \%" if plt.rcParams["text.usetex"] else f"{s} %"

#%% SET UP MODEL

#sample specs of KDE 5215-330 motor
kt = 0.0289 #[N.m/A]
kv = 330 #[rpm/V]
I0 = 0.7 #[A]
Rm = 0.044 #[Ohms]
Vdc = 24.0 #[V]

#set upper limits for speed (N) and torque (M)
Nrated = 5e3 # rated speed in rev/min
Mrated = 300e-3 # rated torque in N.m

# set simulation parameters
numPts = 50 # array size for efficiency calculation

#%% MAIN CALCS
#create evenly-spaced vectors
Nvec = np.linspace(0,Nrated,num=numPts)
Mvec = np.linspace(0,Mrated,num=numPts)

#convert salient speed-params to SI
w_vec = Nvec*RPM2RADS
w_rated = Nrated*RPM2RADS

#create grid over desired torque-speed range
w_grid,M_grid = np.meshgrid(w_vec+w_rated/1000,Mvec+Mrated/1000);

#get throttle settings for each point
d_grid = ev.throttle_calc(w_grid, Vdc, kt)

#predict efficiency at each grid point
#return only the third output (efficiency)
Iac,Pac,n_mot,_ = ev.mot_eff(w_grid, M_grid, d_grid, Vdc, kt, Rm, I0)
n_ctrl = ev.ctrl_eff(Iac, Pac, d_grid, Vdc)[2]

#%% MOTOR PLOT

#plot motor efficiency contour
figMotEff,axMotEff = plt.subplots(1,1,figsize=(5,5))
axMotEff.contourf(w_grid/RPM2RADS,M_grid*1E3,n_mot*100,
                  cmap='Blues',alpha=0.5)
motCont = axMotEff.contour(w_grid/RPM2RADS,M_grid*1E3,n_mot*100,
                       colors='black')

#label motor plot
axMotEff.set_title("Motor efficiency",fontweight='bold')
axMotEff.clabel(motCont, inline=True,fmt=cust_fmt)
axMotEff.set_xlabel('Rotational speed [rev/min]',fontweight='bold')
axMotEff.set_ylabel('Torque [N.mm]',fontweight='bold')
plt.subplots_adjust(top=0.929, bottom=0.117, left=0.142,
                    right=0.935, hspace=0.2, wspace=0.2)

#%% CONTROLLER PLOT

#plot controller efficiency contour
figCtrlEff,axCtrlEff = plt.subplots(1,1,figsize=(5,5))
axCtrlEff.contourf(w_grid/RPM2RADS,M_grid*1E3,n_ctrl*100,
                  cmap='Blues',alpha=0.5)
ctrlCont = axCtrlEff.contour(w_grid/RPM2RADS,M_grid*1E3,n_ctrl*100,
                        colors='black')

#label contour plot
axCtrlEff.set_title("Controller efficiency",fontweight='bold')
axCtrlEff.clabel(ctrlCont, inline=True,fmt=cust_fmt)
axCtrlEff.set_xlabel('Rotational speed [rev/min]',fontweight='bold')
axCtrlEff.set_ylabel('Torque [N.mm]',fontweight='bold')
plt.subplots_adjust(top=0.929, bottom=0.117, left=0.142,
                    right=0.935, hspace=0.2, wspace=0.2)