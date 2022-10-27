# -*- coding: utf-8 -*-
import numpy as np
import scipy.integrate

def motor_size(T,x,shear=5500.0):
    """
    Size a motor for a given torque, aspect ratio
    
    Predict mass, diameter, length, figure of merit for given torque, D/L
    Default shear stress is for sub-500 gram BLDC motors
        
    INPUTS
    ------
    T : float, N.m
        continuous torque required of motor
    x : float, non-dim
        stator aspect ratio (D/L)
    shear : float, Pa (N/m^2) - OPTIONAL
        shear stress used to size the initial volume
        default value of 5.5 kPa is a conservative est.
        
    OUTPUTS
    -------
    m_tot : float, kg
        total mass of the motor
    U_tot : float, m^3
        total volume of the motor
    Do : float, m
        outer motor diameter 
    Lo : float, m
        outer motor length
    km : float, N.m/sqrt(Ohms)
        figure of merit (motor constant) of the motor
    """
    # predict the stator volume
    U_airgap = T/(2*shear) #[m^3], core volume prediction
    Ds = np.cbrt(4*x*U_airgap/np.pi) #[m]
    Ls = np.cbrt(4*U_airgap/(np.pi*x**2)) #[m]

    # predict outer dims
    xD = 0.0608*np.log(x) + 0.775 #[-]
    xL = -0.165*np.log(x) + 0.5708 #[-]
    
    Do = Ds/xD #[-]
    Lo = Ls/xL #[-]
    U_tot = 0.25*np.pi*Lo*Do**2 #[m^3]
    
    # predict rotor, support volumes
    U_stat = 0.25*np.pi*Ls*Ds**2 #[m^3]
    U_rot = 0.25*np.pi*Ls*(Do**2 - Ds**2) #[m]
    U_supp = 0.25*np.pi*(0.5*(Lo-Ls))*Ds**2 #[m]
    
    # predict masses
    m_stat = U_stat*4757.149 #[kg]
    m_rot = U_rot*9066.827 #[kg]
    m_supp = U_supp*855.149 #[kg]
    m_tot = 2*m_supp + m_rot + m_stat #[kg]
    
    # predict Km
    km = 616*(Ds**0.88)*(U_stat**0.54) #[N.m/sqrt(Ohms)]
    
    return m_tot,U_tot,Do,Lo,km

def esc_size(P_req,sf=2.0):
    """
    predict esc size, mass given cont. power
    
    predict the esc volume and mass using a purely empirical fit
    empirical data collected from 3 KDE, Castle, and HobbyWing data
    nearly uniform trends among all three datasets    
    
    P = 36.203m where [P] = Watts, [m] = grams
    P = 52.280U where [P] = Watts, [U] = cm^3
    
    INPUTS
    ------
    P_req : float, Watts
        the required continuous power output of the ESC
    sf : float, non-dim (optional)
        a safety factor for the prediction
        hobby rule of thumb is 2.0
    
    OUTPUTS
    -------
    m : float, kg
        the mass of the ESC
    U : float, m^3
        the volume of the ESC
    """
    m = sf*(2.762e-5)*P_req #[kg]
    U = sf*(1.913e-8)*P_req #[m^3]
    
    return m,U

def batt_pred(I_load,t_hr,Q_Ah,R_int,n_ser=1,n_prll=1,pkrt=1.2):
    """
    predict voltage at a given time under a given load
    
    predict the entire pack's instantaneous terminal voltage under load
    uses empirical state-of-charge curve fit obtained from Chen and Mora
    https://doi.org/10.1109/TEC.2006.874229
      
    INPUTS
    ------
    I_load : float, Amps
        the current draw at the battery terminals
    t : float, hours
        the instant in time
    Q_Ah : float, Amp*hr
        the rated capacity of the battery unit
    R_int : float, Ohms
        the internal resistance of the battery unit
        in the tens of mili-Ohms range
    n_ser : int, non-dim (optional)
        the number of battery units in series
    n_prll : int, non-dim (optional)
        the number of battery units in parallel
    pkrt : float, non-dim (optional)
        the Peukert constant of the battery
    
    OUTPUTS
    -------
    V_term : float, Volts
        the output voltage of the battery
    dod : float, non-dim
        the depth of discharge of the battery (percent depleted)
    soc : float, non-dim
        the state of charge of the battery (percent remaining)
            
    SPECIAL NOTES
    -------------
    
    1.---  
    The applied current (I_load) and the time (t) can be vectors (ndarrays)
    to calculate the entire discharge curve of the battery. However, 
    BOTH inputs must be vectors of the same length!
    
    2.---
    Ensure that the inputs have the correct units! 
    Hobby batteries are rated in mili-Amp*hr
    This code requires you to enter the capacity in Amp*hr
    
    3.--- 
    Battery terminology is imprecise. A "pack" and "module" may mean
    different things to different people.

    For example, the Thunder Power TP7700-6SR70 is a 7.7 Ah (Amp*hr) unit 
    which consists of 6 cells in series.
    To model this battery unit, input 7.7 for Q_Ah and set n_ser = 6
    If you had 4 of these units wired in series, set n_ser = 4*6
    If you had 4 of these units wired in parallel, set n_prll = 4
    
    4.---
    Normally, you should not deplete a lithium-ion battery below 3.5 V
    In extreme circumstances, you can delpete a li-ion battery down to 3.3 V 
    *NEVER* deplete a battery below 3 V
    """
    
    # convert variables to SI units
    Q_tot = n_prll*Q_Ah #[Amp*hr], total capacity of *pack*
    I_rated = n_prll*Q_Ah #[Amps], rated current of *pack*
    
    # compute Peukert effect of load (sort of safety factor)
    pkrt_exp = np.ones(I_load.shape)
    pkrt_exp[I_load/I_rated>1.0] = pkrt
    I_pkrt = I_load**pkrt_exp #[A] 

    # compute depth of discharge, state of charge
    Q_out = scipy.integrate.cumtrapz(I_pkrt,t_hr,initial=0) #[A*hr]
    Q_out[Q_out>Q_tot] = np.nan #throw out time steps where battery is overloaded
    dod = Q_out/Q_tot #[-]
    soc = 1-dod #[-]
    
    # compute SOC voltage for 1 cell, then pack
    V_soc = (-1.031*np.exp(-35*soc) + 3.685 +
              0.2156*soc - 0.1178*soc**2 + 0.3201*soc**3) #[V]
    V_pack = V_soc*n_ser #[V]

    # compute pack's internal resistance
    R_eq = R_int*(n_ser/n_prll) #[Ohms], equivalent resistance of pack
    
    # compute terminal voltage of pack
    V_term = V_pack - I_pkrt*R_eq #[V]

    return V_term,dod,soc
    
def batt_size(t_hr,e,rho=2.037e3):
    """
    predict battery mass, size for a given duration, specific energy
    
    INPUTS
    ------
    t : float, hours
        time duration of mission or mission phase
    e : float, Wh/kg
        specific energy (energy/mass) of mission or mission phase
    rho : float, kg/m^3 (optional)
        the mass density (mass/volume) of a lipo battery
       
    OUTPUTS
    -------
    m : float, kg
        mass of required battery pack
    U : float, m^3
        volume of required battery pack
        
    SPECIAL NOTES
    -------------
    mass density (mass/volume) of typical lipo is ~2000 kg/m^3 or 2 g/cm^3
    
    reasonable usable energy densities:
        200 Wh/kg for an *extremely* well-optimized low-current application
        170 Wh/kg for a low-current (fixed-wing) application
        140 Wh/kg for a high-current (VTOL) application
    """
    
    m = t_hr/e #[kg]
    U = m/rho #[m^3]

    return m,U