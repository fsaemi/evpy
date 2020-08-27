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
       
    EXAMPLE
    -------
    
    #sample specs of KDE 2304XF-2350 motor
    kv = 2350.0 #[rpm/V]
    kt = 0.0041 #[N.m/A]
    Rm = 0.091 #[Ohms]
    I0 = 0.7 #[A]
    
    #sample voltage from a 2S battery, 50% throttle
    V_batt = 2*4.2 #[V]
    d = 50.0/100.0 #[-]
    
    #generate speed range based on applied voltage
    V_app = V_batt*d #[V]
    N_max = kv*V_app #[rpm]
    N_range = np.linspace(0,N_max,num=1000) #[rpm]
    w_range = N_range*(np.pi/30.0) #[rad/s]
    
    #generate and plot predictions
    T,P_out,I,P_in,n = ev.motor_pred(V_batt,d,Rm,kt,I0,w_range)
    
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
        
    """
    # compute the torque-speed curve
    T = (V*d*kt - w*(kt**2))/Rm #[N*m]
    P_out = T*w #[W]
    
    #compute the input current, check for non-real data
    I = T/kt + I0 #[A]
    I[I<0.0] = np.nan
    
    #compute losses
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
    m : float, kg
        total mass of the motor
    Vol : float, m^3
        total volume of the motor
    D : float, m
        outer motor diameter 
    L : float, m
        outer motor length
    km : float, N.m/sqrt(Ohms)
        figure of merit (motor constant) of the motor
    
    EXAMPLE
    -------
    
    """
    #predict the stator volume
    U_airgap = T/(2*shear) #[m^3], core volume prediction
    Ds = np.cbrt(4*x*U_airgap/np.pi) #[m]
    Ls = np.cbrt(4*U_airgap/(np.pi*x**2)) #[m]

    #predict outer dims
    xD = 0.0608*np.log(x) + 0.775 #[-]
    xL = -0.165*np.log(x) + 0.5708 #[-]
    
    Do = Ds/xD #[-]
    Lo = Ls/xL #[-]
    U_tot = 0.25*np.pi*Lo*Do**2 #[m^3]
    
    #predict rotor, support volumes
    U_stat = 0.25*np.pi*Ls*Ds**2 #[m^3]
    U_rot = 0.25*np.pi*Ls*(Do**2 - Ds**2) #[m]
    U_supp = 0.25*np.pi*(0.5*(Lo-Ls))*Ds**2 #[m]
    
    #predict masses
    m_stat = U_stat*4757.149 #[kg]
    m_rot = U_rot*9066.827 #[kg]
    m_supp = U_supp*855.149 #[kg]
    m_tot = 2*m_supp + m_rot + m_stat #[kg]
    
    #predict Km
    km = 616*(Ds**0.88)*(U_stat**0.54) #[N.m/sqrt(Ohms)]
    
    return m_tot