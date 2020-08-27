import numpy as np
import matplotlib.pyplot as plt
import evpy as ev


# load sample motor catalog as reference values
filename = "scorpion_catalog_2020_07_01.txt"
catalog = np.loadtxt(filename,skiprows=1,usecols=np.arange(1,16))

# parse geometric data (saved as mm)
m = 0.001*catalog[:,0] #mass [kg]
Ds = 0.001*catalog[:,4] #stator diameter [m]
Ls = 0.001*catalog[:,5] #stator length [m]
x = Ds/Ls #[-], given aspect ratio

# parse electrical data
Imax = catalog[:,6] #max current [A]
kt = catalog[:,9] #kt [N.m/A]
R = catalog[:,11] #winding resistance [Ohms]
km = catalog[:,12] #motor constant [N.m/sqrt(Ohms)]
T_rated = 0.2*kt*Imax #rated torque [N.m]

# predict motor size given rated torque and aspect ratio
m_pred,U_pred,Ds_pred,Ls_pred,km_pred = ev.motor_size(T_rated,x)

# prepare figure
fig, ax = plt.subplots(1,2)
for axis in ax:
    axis.grid(True)
    axis.set_xlabel(r'Torque [mN$\cdot$m]')
 
# prepare data for plotting
x_data = T_rated*1e3 #[mN.m]
y1_data = m*1e3 #[g]
y1_pred = m_pred*1e3 #[g]
y2_data = km*1e3 #[g]
y2_pred = km_pred*1e3 #[g]

# make first subplot
ax[0].plot(x_data,y1_data,'xr',markersize=10,mfc='none',label='Actual')
ax[0].plot(x_data,y1_pred,'.b',markersize=10,label='Prediction')
ax[0].set_ylabel('Mass [g]')
ax[0].legend()

# make second subplot
ax[1].plot(x_data,y2_data,'xr',markersize=10,label="Spec")
ax[1].plot(x_data,y2_pred,'.b',markersize=10,label="Prediction")
ax[1].set_ylabel(r"$k_m$ [mN$\cdot$m/√Ω]")

# show plots
plt.tight_layout()
plt.show()