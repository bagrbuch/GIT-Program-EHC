import matplotlib.pyplot as plt
import numpy as np
#import pandas as pd
from matplotlib.ticker import FuncFormatter
from scipy import optimize as o
import csv
from scipy.integrate import simpson

#------------------- Programm to cut the datafile ------------------------------

def select_lines_between(file_path, x, y, output_path):
    with open(file_path, 'r', newline='') as infile:
        reader = csv.reader(infile, delimiter=';')
        lines = list(reader)
    
    selected_lines = lines[x:y+1]

    with open(output_path, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerows(selected_lines)




d1 = float(input('thikness of the membranne (in µm) = ')) #thiknesss of the membrane (25.4µ nafion 211,  50.8µ nafion 212  or 20.3µ nafion hp)
d=  d1*10**-6

def percentage(x, pos):
    return '{:.0f}%'.format(x * 100)



# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

def dataplot(chronoamp1,pressure_sensor1_txt): #file names, add .txt with the pressure_sensor1 file name

# Initialisation of the constants

    A = 5*10**-4                #[m2] active area of the fuel cell
    F = 96485.3321233100184     #[C/mol]
    #d = 25.4*10**-6            #thiknesss of the membrane (25.4µ nafion 211,  50.8µ nafion 212  or 20.3µ nafion hp)
    R = 8.314                   #universal gas constant [J/mol/K]
    T= 25 +273.5                # Temperature [K]
    MH2 = 2.016                 #Molar mass of H2 [g/mol]
       
# Initialisation of the lists

    time1 = []              #time relative to the pressure  [s]
    time2 = []              #time relative to the chronoamp [s]
    pressure1 = []          #relative cathode pressure [kPa]
    current_density1 = []   #[A/m2]
    forward_flux = []       #[mol/s]
    back_diffusion = []     #[mol/s]
    net = []                #[mol/s]
    volatge_eff = []
    flux_eff = []
    work_eff = []
    pot = []                #[V]
    charge = []             #[C]
    with open(pressure_sensor1_txt, 'r') as fichier:
        lignes = fichier.readlines()

    for ligne in lignes[1:]:
        valeurs = ligne.strip().split(';')  #pressures separated with ;
        if len(valeurs) >= 2:
            pressure1.append(float(valeurs[1]))

    time1 = np.linspace(0, len(pressure1)-1,len(pressure1))
    
    with open(chronoamp1, 'r') as fichier:
        lignes = fichier.readlines()

    for ligne in lignes[1:]:
        valeurs = ligne.strip().split(';')  #chronoamp separated with tab
        if len(valeurs) >= 2:
            time2.append(float(valeurs[0]))
            pot.append(float(valeurs[1]))
            current_density1.append(float(valeurs[2])/A)
            charge.append(float(valeurs[3]))

# Same size

    if len(pressure1)>len(current_density1):
        dif = len(pressure1)-len(current_density1)
        pressure1 = pressure1[:-dif]
        time1 = time1[:-dif]
    if len(pressure1)<len(current_density1) :
        dif = len(current_density1)-len(pressure1)
        current_density1 = current_density1[:-dif]
        time2 = time2[:-dif]
        


# forward flux

    forward_flux = (A*np.array(current_density1))/(2*F) #[mol/s]

# permeability DH and back diffusion

    Ieq = A*np.mean(current_density1[-100:]) #[A]
    Peq = np.mean(pressure1[-100:])*10**3    #[Pa]

    DH = Ieq * d
    DH = DH/(2*F*A*Peq)                       #[mol/Pa/m/s]

    back_diffusion = DH*A*np.array(pressure1)*1000 
    back_diffusion = back_diffusion/d          #[mol/s]

    net = np.array(forward_flux)-np.array(back_diffusion) #[mol/s]


#Volume
    
    dP_dt = (pressure1[20]-pressure1[1])/20
    Vc = (A*np.mean(current_density1[1:20])*R*T)/(2*F*1000*dP_dt)
    VC = Vc*1000000


    back_diff_eq = np.mean(back_diffusion[-1000:])

# mole transfert
    integration_back_diff = np.zeros_like(back_diffusion)
    integration_forward_flux = np.zeros_like(back_diffusion)
    integration_net = np.zeros_like(back_diffusion)
    
    for i in range(1, len(time1)):
        integration_back_diff[i] = integration_back_diff[i-1] + np.trapz(back_diffusion[i-1:i+1], time1[i-1:i+1])
        integration_forward_flux[i] = integration_forward_flux[i-1] + np.trapz(forward_flux[i-1:i+1], time1[i-1:i+1])
        integration_net[i] = integration_net[i-1] + np.trapz(net[i-1:i+1], time1[i-1:i+1])

#Wh/g to compress H2
  
    t=0
    while A*(current_density1[t])>=Ieq:
        t = t+1
        
    energy_per_mass = np.mean(pot)*charge[t-1]/3600
    energy_per_mass = energy_per_mass/(integration_net[t]*MH2)

    energy_per_mass2 = np.mean(pot)*charge[t-1]/3600
    energy_per_mass2 = energy_per_mass2 /(MH2*(1000*np.mean(pressure1[-100:])*Vc)/(R*T))
    """
#Wh to compress H2 until 300kPa
    energy_needed = 0
    x=0
    while pressure1[x]<300:
        x = x+1
           
    energy_needed = np.mean(pot)* charge[x-1]/(3600)
    print('Energy to compress until 300 kPa : ', energy_needed, 'Wh')
    """

    #print ('time to reach the equilibrium = ' t/3600, 'hours')   
    print ('Energy_per_mass =',energy_per_mass,'kWh/kg')
    print ('Energy_per_mass 5(volume) = ',energy_per_mass2,'kWh/kg')
    print ('\n' 'Jeq =',1000*Ieq/5,'mA/cm2')
    print ('Peq =',Peq*0.001,'kPa')
    print ('DH =',DH,'mol/Pa/m/s')
    print ('Vc =',VC,'cm3')
    print ('Back_diffusion =', back_diff_eq,' mol/s')
    #print ('H2 transfered forward =', integration_forward_flux[14399],'mol')
   # print ('H2 transfered backward =', integration_back_diff[14399],'mol')
    #print ('H2 transfered net =', integration_net[14399],'mol')

    
# effiency

    voltage_eff = R*T*np.log((np.array(pressure1)+100)/100)
    voltage_eff = np.array(voltage_eff)/(2*F*np.mean(pot))
    flux_eff = (np.array(forward_flux)-np.array(back_diffusion))/np.array(forward_flux)
    work_eff = np.array(flux_eff)*np.array(voltage_eff)


# Assignation of the data

    x1 = time1
    x2 = time2
    y1 = pressure1
    y2 = current_density1
    y3 = forward_flux
    y4 = back_diffusion
    y5 = net

    voltage = np.mean(pot)

# ------------------- Current density and pressure Vs time plot ------------------------

# Creation of the figure and the main axis
    fig1, ax1 = plt.subplots(figsize=(9, 5))

#Plotting the first data series on ax1
    ax1.plot(time1/3600, y1, 'b-', label='relaive cathode pressure [kPa]')
    ax1.set_xlabel('time [hours]',fontsize=14)
    ax1.set_ylabel('relative cathode pressure [kPa]', color='b',fontsize=14)
    ax1.tick_params(axis='y', labelcolor='b')

# Creating a second y axis that shares the same x axis
    ax2 = ax1.twinx()

# Plotting the second series of data on ax2
    ax2.plot(np.array(time2)/3600, np.array(y2)/10**4, 'r-', label='current density [A/cm2]')
    ax2.set_ylabel('current density [A/cm2]', color='r', fontsize=14)
    ax2.tick_params(axis='y', labelcolor='r')

# legends
    fig1.tight_layout()
    ax1.legend(loc='center right')
    ax2.legend(loc='center right', bbox_to_anchor=(0.98,0.45))
    ax1.grid(True, which='both', axis='x', linestyle='--', linewidth=0.5)
    ax2.grid(True, which='both', axis='x', linestyle='--', linewidth=0.5)

# title and show

    ax1.set_title('current density and relative cathode pressure - %.2f V' % voltage, fontsize=14)
    #plt.show()
# ------------------- Current density vs Pressure ------------------------

# Creation of the figure and the main axis
    fig5, ax5 = plt.subplots(figsize=(9, 5))

#Plotting the first data series on ax1
    ax5.plot(pressure1, np.array(y2)/10**4, 'b-', label='relative cathode pressure [kPa]')
    ax5.set_xlabel('relative cathode pressure [kPa]', fontsize=14)
    ax5.set_ylabel('current density [A/cm2]', color='b', fontsize=14)
    ax5.tick_params(axis='y', labelcolor='b')

# legends
    fig5.tight_layout()
    ax5.legend(loc='upper right', bbox_to_anchor=(1, 1))
    ax5.grid(True, which='both', axis='x', linestyle='--', linewidth=0.5)

# title and show

    ax1.set_title('Current density VS  relative cathode pressure - %.2f V' % voltage, fontsize=14)

# --------------------- Flow diffusion plot ------------------------


    fig, (ax3, ax5) =  plt.subplots(1, 2, figsize=(16, 6))

    ax3.plot(time1/3600, y3, 'b-', label='forward flux [mol/s]')
    ax3.plot(time1/3600, y4, 'r-', label='back-diffusion [mol/s]')
    ax3.plot(time1/3600, y5, 'g-', label='net diffusion [mol/s]')

    ax3.set_xlabel('time [hours]', fontsize=14)
    ax3.set_ylabel('flux [mol/s]', color='b',fontsize=14)
    ax3.tick_params(axis='y', labelcolor='b')

    ax3.grid(True)

    ax3.legend(loc='center right')

    ax3.set_title('Flow Diffusion - %.2f V' % voltage, fontsize=14)



    ax5.plot(time1/3600, integration_forward_flux , 'b-', label='Forward')
    ax5.plot(time1/3600, integration_back_diff , 'r-', label='Backward')
    ax5.plot(time1/3600, integration_net, 'g-', label='Net')

    ax5.set_xlabel('time [hours]', fontsize=14)
    ax5.set_ylabel('hydrogen transferred [mol]', color='b', fontsize=14)

    ax5.grid(True)

    ax5.legend(loc='center right')

    
    ax5.set_title('Moles transferred - %.2f V' % voltage, fontsize=14)
    plt.tight_layout()
    #plt.show()
    

# ------- Graphs all efficiencies of one potential vs time  ----------------


    fig3, ax4 = plt.subplots(figsize=(10, 6))

    ax4.plot(time1/3600, voltage_eff, 'b-', label='voltage efficiency')
    ax4.plot(time1/3600, flux_eff, 'r-', label='flux efficiency')
    ax4.plot(time1/3600, work_eff, 'g-', label='work efficiency')

    ax4.set_xlabel('time [hours]', fontsize=14)
    ax4.set_ylabel('efficiency [%]', color='b',fontsize=14)
    ax4.yaxis.set_major_formatter(FuncFormatter(percentage))

    ax4.grid(True)

    ax4.legend(loc='center right')

    
    ax4.set_title('Efficiencies - %.2f V' % voltage,fontsize=14)

    plt.show()
    
    return()




#-------------------------------------------------------------------------            
#-------------------------------------------------------------------------


def fit_data_exp():
    depressure_file = input("Enter the name of the data file: ")
    DH = eval(input("Enter the DH value: "))
    ini = 0.000011            # Volume expected (m3)
    pp = 10

    # Initialisation of the constants
    A = 5 * 10**-4            # [m2] active area of the fuel cell
    F = 96485.3321233100184   # [C/mol]
    #d = 25 * 10**-6           # thickness of the membrane (25µ nafion 211 or 20.3µ nafion hp)
    R = 8.314                 # universal gas constant (J/mol.K)
    T = 25 + 273.5            # Temperature (K)

    #-------- Export data ----------
    depressure = []
    with open(depressure_file, 'r') as fichier:
        lignes = fichier.readlines()

    for ligne in lignes[1:]:
        valeurs = ligne.strip().split(';')  # pressures separated with ;
        if len(valeurs) >= 2:
            depressure.append(float(valeurs[1])-10)

    time = np.linspace(0, len(depressure)-1, len(depressure))

    Peq = depressure[0]

    t = time
    data = depressure

    fitfunc = lambda p, x:  Peq * np.exp(-(A* R * T * x * DH) / (d*p[0])) + p[1]
    errfunc = lambda p, x, y: fitfunc(p, x) - y

    p0 = [ini,pp]
    p1, success = o.leastsq(errfunc, p0[:], args=(t, data))
    V=p1[0]*10**6
    
    time_fit = np.linspace(t.min() - 1, t.max() + 1)
    fig, ax1 = plt.subplots()
    ax1.set_title('Depressure')
    ax1.set_xlabel('time [h]')
    ax1.set_ylabel('pressure [kPa]')
    ax1.plot(t/3600, data, "o", label='Sample data')
    ax1.plot(time_fit/3600, fitfunc(p1, time_fit), label='Fit')
    ax1.legend(title='0.02V', fancybox=True, loc='upper right')
    print('\n' 'The volume is', V,'cm3')
    plt.show()
    return(p1[1])

