"""
Example file which demonstrates the following functions:
    1. size_motor() - predict motor size for desired torque
    2. wind_motor() - predict electrical constants for desired Vdc & speed
    
Data flow:
    Torque ratings from independent motor catalog
    ||
    ||
    \/
    size_motor ==> motor mass, figure of merit (motor constant, km)
    ||
    ||
    \/
    wind_motor ==> motor resistance
"""

#import libraries
import numpy as np
import matplotlib.pyplot as plt
import evpy as ev

# load sample motor catalog as reference values
filename = "scorpion_catalog_2020_07_01.txt"
catalog = np.loadtxt(filename,skiprows=1,usecols=np.arange(1,16))

# parse geometric data (saved as grams and mm)
m = 0.001*catalog[:,0] #mass [kg]
Ds = 0.001*catalog[:,4] #stator diameter [m]
Ls = 0.001*catalog[:,5] #stator length [m]
x = Ds/Ls #[-], given aspect ratio

# parse electrical data
Imax = catalog[:,6] #max current [A]
kt = catalog[:,9] #kt [N.m/A]
R = catalog[:,11] #winding resistance [Ohms]
km = catalog[:,12] #motor constant [N.m/sqrt(Ohms)]
M_rated = 0.2*kt*Imax #rated torque [N.m]

# predict motor mass & km for desired torque
_,_,_,m_pred,km_pred = ev.size_motor(M_rated,AR=x)

#Catalog doesn't have Vdc and speed ratings, 
#Instead, I extract an estimated Rm from predicted km and catalog kt
R_pred = (kt/km_pred)**2.0
#If I had Vdc and speed ratings, I would feed that in as such:
#kt_pred,R_pred = (km_pred,Vdc,w_nom,nom_throt=0.5)

# prepare figure
fig, ax = plt.subplots(1,2,sharex=True)
for axis in ax:
    axis.grid(True)
    axis.set_xlabel(r'Torque [mN$\cdot$m]')
 
# plot mass predictions
ax[0].plot(M_rated*1e3,m*1E3,'.',markersize=10,label='Catalog')
ax[0].plot(M_rated*1e3,m_pred*1E3,
           'x',markeredgewidth=2,markersize=10,label='Model')
ax[0].set_title('Mass [g]')

# make second subplot
ax[1].plot(M_rated*1E3,R*1E3,'.',markersize=10,label="Catalog")
ax[1].plot(M_rated*1E3,R_pred*1E3,
           'x',markeredgewidth=2,markersize=10,label='Model')
ax[1].set_title(r"$R_m$ [$\Omega$]")

# show plots
for axis in ax:
    axis.set_xlabel('Rated torque [mN.m]')
    axis.legend()
    axis.grid(True)

plt.tight_layout()
plt.show()