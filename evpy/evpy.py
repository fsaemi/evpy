########################
#### library imports ###
########################

import numpy as np

##########################
#### Library functions ###
##########################

def motor_pred(V,d,Rm,kt,I0,w):
    """
    predict motor performance for given specs
    
    predict torque, power, current, and efficiency over a range of speed 
    uses 3 high-level component parameters (Rm, kt, I0) and throttle
    applicable to sensorless, six-step commutation brushless DC motors 
    
    Note: kt = kv with SI units
    
    INPUTS
    ------
    V : float, Volts
        voltage of the DC bus
    d : float, non-dim
        non-dimensional throttle setting (duty ratio)
    Rm : float, Ohms
        motor resistance (phase to phase)
    kt : float, Newton-meter per Amp
        torque constant of motor
    I0 : float, Amps
        no-load current of motor 
    w : ndarray (float), rads/sec
        range of motor speed
    
    OUTPUTS
    -------
    T : ndarray (float), Newton-meter
        output torque of motor
    P_out : ndarray (float), Watts
        output power (mechanical)
    I : ndarray (float), Amps
        input current to motor
    P_in : ndarray (float), Watts
        input power (AC)
    n : ndarray (float), non-dim
        non-dimensional motor efficiency        
    """
    # compute the torque-speed curve
    T = (V*d*kt - w*(kt**2))/Rm #[N*m]
    P_out = T*w #[W]
    
    # compute the input current, check for non-real data
    I = T/kt + I0 #[A]
    I[I<0.0] = np.nan
    
    # compute losses
    P_L_co = Rm*I**2 #[W], copper losses in windings
    P_L_ir = w*kt*I0 #[W], iron losses in windings
    
    # compute efficiency with throttle-harmonics
    P_in = P_out*1.1 + (P_L_co+P_L_ir)/d #[W]
    n = P_out/P_in #[-]
    n[n>1.0] = np.nan
    n[n<0.0] = np.nan
    
    return T,P_out,I,P_in,n

def motor_size(T,x,shear=5500):
    """
    Size a motor for a given torque, aspect ratio
    
    Predict the mass, diameter, length, and figure of merit rated for given torque, D/L
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

def esc_pred(V,d,f_pwm,Ron,Ton,Im,Pm):
    """
    predict ESC losses given specs and motor performance
    """
    # compute copper losses
    P_L_co = 2*Ron*Im**2 #[W]
    P_L_sw = V*Im*f_pwm*Ton #[W]
    P_dc = Pm + (P_L_co+P_L_sw)/d #[W]
    n = Pm/P_dc #[-]
    n[n>1.0] = np.nan
    n[n<0.0] = np.nan
    
    I_dc = P_dc/V #[A]
    I_dc[I_dc>1.0] = np.nan
    I_dc[I_dc<0.0] = np.nan
    
    return I_dc,P_dc,n