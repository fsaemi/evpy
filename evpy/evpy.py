###############
#### README ###
###############

"""
    NOTES    

    FUTURE FUNCTIONS
        I0 calc for motor size & speed
        some load profile (momentum theory rotor?)
        integrated rotor/motor/ESC/battery model with hover-hold throttling
        torque/speed/efficiency contour for motor+ESC including harmonics
"""

################
#### IMPORTS ###
################

import numpy as np
# import scipy.integrate

##########################
#### Library functions ###
##########################

def set_throttle(w,Vdc,kt):
    """
    Predict minimum throttle required to achieve desired shaft speed
    
    INPUTS
        w   := shaft speed [rad/s]
        Vdc := DC voltage [V]
        kt  := torque constant [N.m/A]
        
    OUTPUTS
        d   := non-dimensional throttle [-]
        
    EXAMPLE
        See "ex_motor_esc.py"
    """
    
    d = kt*w/Vdc #[-]
    
    return d

def motor_pred(w,M,d,Vdc,kt,Rm,I0):
    """
    Predict motor efficiency at given shaft speed and shaft torque
    
    INPUTS
        w   := shaft speed [rad/s]
        M   := shaft torque [N.m]
        d   := non-dimensional throttle [-]
        Vdc := DC voltage [V]
        kt  := torque constant [N.m/A]
        Rm  := motor resistance (phase-to-phase) [Ohms]
        I0  := no-load current [A]
        
    OUTPUTS
        Qmot    := motor losses [W]
        Pac     := motor power draw [W] 
        n_mot   := efficiency [-]
        Iac     := motor current [A]
    
    EXAMPLE
        See "ex_motor_esc.py"
    """
    
    #derive internal parms
    E = kt*w #[V] back-EMF
    I = M/kt #[A] nominal motor current
    Pmech = M*w #[W] applied mechanical load power

    #calculate losses
    Qcopper = Rm*I**2.0 #[W] copper losses
    Qiron = kt*I0*w #[W] iron losses
    Qmisc = 0.1*Pmech #[W] miscellaneous losses
    Qharm = (Qcopper+Qiron)/d #[W] increase in losses from harmonics
    Qmot = Qmisc + Qharm #[W] losses including harmonic distortion
    
    #calc efficiency, final current and power draw
    Pac = Pmech + Qmot #[W] elec power consumed by motor
    n_mot = Pmech/Pac #[W] motor efficiency
    Iac = Pac/E #[A] actual current draw
    
    return Qmot,Pac,n_mot,Iac

def esc_pred(Iac,Pac,d,Vdc,f_pwm=12E3,Rds_on=1E-3,T_trans=1E-6,P_qui=0.25):
    """
    Predict ESC efficiency at desired motor current
    
    INPUTS
        Iac     := motor current [A]
        Pac     := motor power [W]
        d       := throttle setting [-]
        Vdc     := DC voltage [V]
        f_pwm   := PWM frequency [Hz]
        Rds_on  := switch resistance when turned on [Ohms]
        T_trans := switch transition period (on/off) [s]
        P_qui   := ESC's quiescent ("vampire") power draw [W]
        
    OUTPUTS
        Qesc    := ESC losses [W]
        Pdc     := ESC power draw [W] 
        n_esc   := ESC efficiency [-]
        Idc     := ESC current [A]
        
    EXAMPLE
        See "ex_motor_esc.py"
        
    NOTES
        f_pwm ranges from 8 to 32 kHz
        Rds_on ~ 1 miliohm
        T_trans ~ 1 microsecond
        P_qui ~ 0.25 W
    """

    #calculate losses for desired load
    Qcopper = 2*Rds_on*Iac**2.0 #[W] copper losses
    Qswitch = f_pwm*T_trans*Vdc*Iac #[W] switching losses
    Qharm = (Qcopper+Qswitch)/d #[W] increase in losses from harmonics
    Qesc = P_qui + Qharm #[W] losses including harmonic distortion
    
    #calculate efficiency, DC power, DC current draw
    Pdc = Pac + Qesc #[W] elec power consumed by ESC
    n_esc = Pac/Pdc #[W] ESC efficiency
    Idc = Pdc/Vdc #[A] actual current draw
    
    return Qesc,Pdc,n_esc,Idc
    
def size_motor(M,shear=5.5E3,AR=2.0):
    """
    Size a motor to required torque + optional geometric & thermal constraints
    
    INPUTS
        M       := shaft torque [N.m]
        shear   := shear stress [Pa]
        AR      := aspect ratio (stator diameter/stator length)
        
    OUTPUTS
        m   := mass [kg]
        U   := volume [m^3]
        D   := diameter [m]
        L   := length [m]
        km  := motor constant [N.m/sqrt(W)]
        
    NOTES
        Cooling is the key limit to shear stress. 
        If the motor will have clean axial airflow into its windings, *then*
        you can prescribe higher shear.
        
        High aspect ratio motors are more 'torque-y' (direct drive)
        Low aspect ratio motors are more 'speed-y' (gearing)
    """
    
    #predict stator volume
    Ustat = M/(2.0*shear) #[m^3] stator volume
    Ds = np.cbrt(4.0*AR*Ustat/np.pi) #[m]
    Ls = np.cbrt(4.0*Ustat/(np.pi*AR**2)) #[m]
    
     # predict outer dims
    DR = 0.0608*np.log(AR) + 0.775 #[-] diameter ratio (outer/stator)
    LR = -0.165*np.log(AR) + 0.5708 #[-] length ratio (outer/stator)
    D = Ds/DR #[-]
    L = Ls/LR #[-]
    U = 0.25*np.pi*L*D**2 #[m^3]
    
    # predict rotor, support volumes
    Urot = 0.25*np.pi*Ls*(D**2.0 - Ds**2.0) #[m]
    Usupp = 0.25*np.pi*(0.5*(L-Ls))*Ds**2.0 #[m]
    
    # predict masses
    m_stat = Ustat*4757.149 #[kg]
    m_rot = Urot*9066.827 #[kg]
    m_supp = Usupp*855.149 #[kg]
    m = 2*m_supp + m_rot + m_stat #[kg]
    
    # predict Km
    km = 616*(Ds**0.88)*(Ustat**0.54) #[N.m/sqrt(Ohms)]
    
    return D,L,U,m,km

def wind_motor(km,Vdc,w_nom,nom_throt=0.5):
    """
    Winds a motor to given DC voltage, speed, and throttle margin
    
    INPUTS
        km          := motor constant [N.m/sqrt(W)]
        Vdc         := DC bus voltage [V]
        w_nom       := nominal shaft speed [rad/s]
        nom_throt   := nominal throttle trim [-]
        
    OUTPUTS
        kt  := torque constant [N.m/A]
        Rm  := winding resistance [Ohms]
        
    NOTES
        This fuction winds the motor such that the controller
        has some voltage margin at nominal shaft speed
        The predicted constants are IDEAL (best-case) values 
        The predictions may be impractical to build
    """
    
    E_nom = nom_throt*Vdc #[V] back-EMF at nominal throttle
    kt = E_nom/w_nom
    Rm = (kt/km)**2.0
    
    return kt,Rm
    