# -*- coding: utf-8 -*-
"""
Example file for integrated models (motor + controller + battery)
Uses experimental data measured on flying vehicle

Inputs: torque, exp_rpm vectors
Outputs: battery voltage prediction

"""

#%% IMPORT libraries & global constants
import numpy as np
import scipy.signal as signal
import evpy as ev
import matplotlib.pyplot as plt
# import matplotlib.ticker as ticker

loadcell_cnst = 0.03529 #V/(lb.in)
LBIN2NM = 0.113
RPM2RADS = np.pi/30.0

#%% SPECIFY INPUT FILE W/ TORQUE+exp_rpm DATA MEASURED IN-FLIGHT
folder = "./exp_data/"
fsample = 2.0 #[Hz]
file = "fwd_flight_data.txt"
soc_init = 1.0 #[-]
xInMinutes = True #plot x-axis in minutes
#limits for plot window
i1 = 10
i2 = -1

#%% POWERTRAIN SPECS

#vehicle (quadrotor with 4 prop-rotors)
num_rotors = 4.0 #[-]

#motor params
kv = 380.0 #[V/exp_rpm]
kt = 0.0251 #[N.m/A]
Rm = 0.075 #[Ohms]
I0 = 0.5 #[A]
num_polePairs = 12.0

#battery params
QAh = 6.0 #[A.hr]
n_ser = 6.0 #[-]
Rcell = 0.013 #[Ohms]
Qrated = QAh*3600.0 #[C]

#%% LOAD + FILTER EXPERIMENTAL DATA
data = np.loadtxt(folder+file,delimiter='\t',skiprows=1)

#create low-pass filter
fnyq = 0.5*fsample #[Hz]
fcut = fnyq/5.0 #[Hz]
filtOrder = 2 #[-]
b, a = signal.butter(filtOrder, fcut, fs=fsample)

#apply filter to all data columns except time
for i in range(1,data.shape[1]):
    data[:,i] = signal.filtfilt(b,a,data[:,i])

#%% ASSIGN EXPERIMENTAL DATA
t = data[:,0] #[s]
exp_Vbatt_term = data[:,2] #[V]
exp_Ibatt = data[:,3] #[A]
exp_Vtorq = data[:,7] #hardware-filtered torque sensor voltage [V]
exp_rpm = data[:,9]/num_polePairs #[rev/min]

#SI unit conversions
exp_w = exp_rpm*RPM2RADS
exp_M = LBIN2NM*np.abs(exp_Vtorq-exp_Vtorq[0])/loadcell_cnst

#%% PRE-ALLOCACTE SIMULATION PARAMS
#pre-allocate time history arrays
sim_t = t #sim time vector [s]
sim_duty = np.ones(sim_t.shape)*np.nan # sim throttle vector [-]
sim_Ictrl = np.ones(sim_t.shape)*np.nan # sim controller current vector [A]
sim_soc = np.ones(sim_t.shape)*np.nan # sim SOC vector [-]
sim_Vsoc_cell = np.ones(sim_t.shape)*np.nan # sim SOC voltage vec (per-cell)[V]
sim_Vbatt_term = np.ones(sim_t.shape)*np.nan #sim terminal volt vec (total)[V]

#%% INITIALIZE SIM
sim_dt = 1.0/fsample #[s]
sim_Qdisc = 0.0 #[Coulomb or A.s] battery capacity discharged
sim_Vbatt_lcl = n_ser*ev.soc_volts(soc_init) #[V]
sim_Vbatt_term[0] = sim_Vbatt_lcl
sim_Ictrl[0] = 0.0

#SPECIFY cutoffs
soc_cutoff = 0.1 #[-]
Vcutoff = 3.3 #[-]

#%% MAIN LOOP
i = 1 #skip zero-th case
print("==============")
print("Simulating...")
while i<sim_t.shape[0]:

    #calculate  throttle
    sim_duty_lcl = ev.throttle_calc(exp_w[i],sim_Vbatt_lcl,kt)
    
    #stop if over-load applied
    if sim_duty_lcl >1.0 or exp_M[i]>2.0 or exp_w[i]>1E3:
        print("BREAK: Throttle required exceeds 100%")
        break
    
    #pass-through values if no (or weird) load applied
    if sim_duty_lcl <0.3 or exp_M[i]<0.0 or exp_w[i]<0.0:
        sim_Vbatt_term[i] = sim_Vbatt_term[i-1]
        sim_Ictrl[i] = sim_Ictrl[i-1]
        i += 1
        continue
    
    #mot, ctrl efficiency predictions
    Iac,Pac,_,_ = ev.mot_eff(exp_w[i],exp_M[i],sim_duty_lcl,
                                        sim_Vbatt_lcl,kt,Rm,I0)
    Idc,Pdc,_,_ = ev.ctrl_eff(Iac,Pac,sim_duty_lcl,sim_Vbatt_lcl)
    
    #deduct total current from battery
    Idc_tot = num_rotors*Idc #[A]
    sim_Qdisc += Idc_tot*sim_dt
    soc_lcl = soc_init-(sim_Qdisc/Qrated) #[-] state of charge
    Vsoc_cell = ev.soc_volts(soc_lcl) #[V] SOC voltage
    sim_Vbatt_lcl = n_ser*(Vsoc_cell - Idc_tot*Rcell) #[V] TOTAL voltage
    
    if soc_lcl <= soc_cutoff:
        print("BREAK: cutoff SOC reached: {:.0f}%".format(100.0*soc_cutoff))
        break
    
    if Vsoc_cell <= Vcutoff:
        print("BREAK: cutoff cell SOC voltage reached: {:.1f} V".format(Vcutoff))
        break
    
    #record data and increment
    sim_soc[i] = soc_lcl
    sim_Vbatt_term[i] = sim_Vbatt_lcl
    sim_Vsoc_cell[i] = Vsoc_cell
    sim_duty[i] = sim_duty_lcl
    sim_Ictrl[i] = Idc
    i += 1

print("SIMULATION COMPLETE")

#%% PLOT WINDOW ADJUSTMENTS
x = t[i1:i2]-t[i1]
x_label = "Time [s]"
if xInMinutes is True:
    x = x/60.0#
    x_label = "Time [min]"
expLinestyle='dashed'
expMrkrSize=2

#%% TORQUE PLOT
torqFig, torqAx = plt.subplots(1,1,figsize=(5,5))
y = exp_M[i1:i2]*1E3
torqAx.plot(x,y,linestyle=expLinestyle)
torqAx.set_title('Propeller torque [N.mm] (measured)',fontweight='bold')
torqAx.set_xlabel(x_label,fontweight='bold')
if xInMinutes is True:
    torqAx.set_xlim([0,6])
torqAx.set_ylim([0,350])
torqAx.grid(True)

plt.subplots_adjust(top=0.943, bottom=0.102, left=0.094, 
                    right=0.973, hspace=0.2, wspace=0.2)

#%% PLOT exp_rpm
rpmFig, rpmAx = plt.subplots(1,1,figsize=(5,5))
y = exp_w[i1:i2]/RPM2RADS
rpmAx.plot(x,y,linestyle=expLinestyle)
rpmAx.set_title('Propeller speed [rev/min] (measured)',fontweight='bold')
rpmAx.set_xlabel(x_label,fontweight='bold')
if xInMinutes is True:
    rpmAx.set_xlim([0,6])
rpmAx.set_ylim([0,5E3])
rpmAx.grid(True)

plt.subplots_adjust(top=0.942, bottom=0.097, left=0.115,
                    right=0.979, hspace=0.2, wspace=0.2)

#%% PLOT  VOLTAGE
voltFig, voltAx = plt.subplots(1,1,figsize=(5,5))
y = exp_Vbatt_term[i1:i2]
y_sim = sim_Vbatt_term[i1:i2]

voltAx.plot(x,y,label="Flight data",
         linestyle=expLinestyle,linewidth=expMrkrSize)
voltAx.plot(x,y_sim,label="Model")
voltAx.set_title("Battery voltage [V]",fontweight='bold')
voltAx.set_xlabel(x_label,fontweight='bold')
if xInMinutes is True:
    voltAx.set_xlim([0,6])
voltAx.set_ylim([20.0,26.0])
voltAx.grid(True)
voltAx.legend()

plt.subplots_adjust(top=0.942, bottom=0.102, left=0.088,
                    right=0.978, hspace=0.2, wspace=0.2)