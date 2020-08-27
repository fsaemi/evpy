# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 12:44:17 2020

@author: fsaem
"""
import numpy as np
import matplotlib.pyplot as plt
plt.close("all")

import evpy as ev

filename = "scorpion_catalog_2020_07_01.txt"
# filename = "axi_catalog_2020_07_01.txt"
# filename = "kde_catalog_2020_06_18_AR4_FILTERED.txt"
catalog = np.loadtxt(filename,skiprows=1,usecols=np.arange(1,16))

# geometric data (saved as mm)
m = 0.001*catalog[:,0] #mass [kg]
Ds = 0.001*catalog[:,4] #stator diameter [m]
Ls = 0.001*catalog[:,5] #stator length [m]
x = Ds/Ls #[-], given aspect ratio

Imax = catalog[:,6] #max current [A]
kt = catalog[:,9] #kt [N.m/A]
R = catalog[:,11] #winding resistance [Ohms]
km = catalog[:,12] #motor const$ant [N.m/sqrt(Ohms)]
T_rated = 0.2*kt*Imax #rated torque [N.m]

# z = ev.motor_size(T_rated,x)
# plt.scatter(m*1e3,z*1e3)
# plt.grid(True)

m_pred = ev.motor_size(T_rated,x)

fig1, ax1 = plt.subplots(1,1)
y_data = T_rated*1e3 #[mN.m]
ax1.plot(m*1e3,y_data,'xr',markersize=10,mfc='none',label='Actual')
ax1.plot(m_pred*1e3,y_data,'ob',markersize=10,label='Prediction')
ax1.grid(True)
ax1.set_xlabel('Mass [g]')
ax1.set_ylabel(r'Torque [mN$\cdot$m]')
ax1.legend(fontsize=18)
plt.tight_layout()

# fig2, ax2 = plt.subplots(1,1)
# x_data = m*1e3 #[g]
# ax2.plot(x_data,km,'xr',markersize=10,label="Spec")
# ax2.plot(x_data,km_pred,'.b',markersize=10,label="Prediction")
# ax2.grid(True)
# ax2.legend()
# ax2.set_xlabel(r'Mass [g]')
# ax2.set_ylabel(r"$k_m$ [mN$\cdot$m/√Ω]")
# plt.tight_layout()

"""Test of the performance model"""
# =============================================================================
# #sample specs of KDE 2304XF-2350 motor
# kv = 2350.0 #[rpm/V]
# kt = 0.0041 #[N.m/A]
# Rm = 0.091 #[Ohms]
# I0 = 0.7 #[A]
# 
# #sample voltage from a 2S battery, 50% throttle
# V_batt = 2*4.2 #[V]
# d = 50.0/100.0 #[-]
# 
# #generate speed range based on applied voltage
# V_app = V_batt*d #[V]
# N_max = kv*V_app #[rpm]
# N_range = np.linspace(0,N_max,num=1000) #[rpm]
# w_range = N_range*(np.pi/30.0) #[rad/s]
# 
# #generate and plot predictions
# T,P_out,I,P_in,n = ev.motor_pred(V_batt,d,Rm,kt,I0,w_range)
# 
# fig,ax = plt.subplots(1,3,sharex=True)
# for axis in ax:
#     axis.set_xlabel("Rotational speed [rev/min]")
#     axis.grid()
# 
# ax[0].plot(N_range,T*1e3)
# ax[0].set_ylabel("Torque [N.m]")
# 
# ax[1].plot(N_range,P_out,label="Output")
# ax[1].set_ylabel("Power [W]")
# 
# ax[2].plot(N_range,n*100)
# ax[2].set_ylabel("Efficiency [%]")
# =============================================================================
