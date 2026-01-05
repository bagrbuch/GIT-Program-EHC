import matplotlib.pyplot as plt
import numpy as np
#import pandas as pd
from matplotlib.ticker import FuncFormatter
from scipy import optimize as o
import csv
from scipy.integrate import simpson
from scipy.stats import linregress
from scipy.optimize import leastsq
import datetime
from scipy import interpolate

#------------------- Programm to cut the datafile ------------------------------

def select_lines_between(file_path, x, y, output_path):
    with open(file_path, 'r', newline='') as infile:
        reader = csv.reader(infile, delimiter=';')
        lines = list(reader)
    
    selected_lines = lines[x:y+1]

    with open(output_path, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerows(selected_lines)

##d1 = float(input('thikness of the membranne (in µm) = ')) #thiknesss of the membrane (25.4µ nafion 211,  50.8µ nafion 212  or 20.3µ nafion hp)
d1 = 180
d=  d1*10**-6

def percentage(x, pos):
    return '{:.0f}%'.format(x * 100)

# -------------------------Function for finding linear section for dP_dt and fit to linear function-----------------------------------------------------

def detect_linear_region_and_calculate_dpdt(pressure1, window_size=30, threshold=0.8):
    start_index = 0
    linear_end_index = len(pressure1) - 1
    first_avg = np.mean(pressure1[start_index:start_index + window_size])
    last_valid_line_number = start_index

    for i in range(start_index + 1, len(pressure1) - window_size):
        current_avg = np.mean(pressure1[i:i + window_size])
        line_number = i * window_size

        if abs(current_avg - first_avg) > threshold:
            linear_end_index = i
            last_valid_line_number = line_number
            break

    if linear_end_index == len(pressure1) - 1:
        print("No point was found where the average exceeded the threshold.")

    linear_region_x = np.arange(last_valid_line_number)
    linear_region_y = pressure1[:last_valid_line_number]

    fitfunc = lambda p, x: p[0] * x + p[1]
    errfunc = lambda p, x, y: fitfunc(p, x) - y

    p_initial = [0, 0]
    optimal_params, success = leastsq(errfunc, p_initial, args=(linear_region_x, linear_region_y))

    slope = optimal_params[0]

    plt.figure(figsize=(10, 6))
    plt.scatter(linear_region_x, linear_region_y, label="Data", color="blue")
    plt.plot(linear_region_x, fitfunc(optimal_params, linear_region_x), label=f"Fit", color="red")
    plt.xlabel("Index")
    plt.ylabel("Pressure")
    plt.title("Linear Region Fit for dP/dt Calculation")
    plt.legend()
    plt.grid()
    plt.show()

    return last_valid_line_number, slope

# -------------------------Programm for export data-----------------------------------------------------

def export(chronoamp1, pressure_sensor1_txt, voltage, time1, pressure1, current_density1, forward_flux, back_diffusion, net, voltage_eff, flux_eff, work_eff, integration_forward_flux, integration_back_diff, integration_net, energy_per_mass, energy_per_mass2, Ieq, Peq, DH, VC, back_diff_eq, d1, DH_peak, DH_interval1, DH_interval2, DH_end, P_peak, P_interval1, P_interval2, P_end, additional_pressure_file=None):

    with open(pressure_sensor1_txt, 'r') as fichier:
        lines = fichier.readlines()

    times = []
    pressures = []

    for line in lines:
        if line.startswith("Time Stamp"):
            continue
        parts = line.split(';')
        if len(parts) >= 2:
            time_str = parts[0].strip()
            pressure_val = float(parts[1].strip())
            time_obj = datetime.datetime.strptime(time_str, '%d.%m.%Y %H:%M:%S')
            times.append(time_obj)
            pressures.append(pressure_val)

    output_file = 'Export_data.txt'
    with open(output_file, 'w') as file:
        first_time = times[0]

        file.write(f"Measurement started at: {first_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        file.write("-" * 100 + "\n")
        file.write(f"Voltage: {voltage:.2f} V\n")
        file.write(f"Thickness of the membrane: {d1} m*10^-6\n")  
        file.write(f"Reached pressure: {P_peak / 100000:.2f} Bar\n")
        file.write("=" * 100 + "\n")

        file.write(f"{'Energy per mass (kWh/kg)':<25}{'Energy per volume (kWh/kg)':<30}{'Jeg (mA/cm2)':<15}{'Peq (Bar)':<10}{'Vc (cm3)':<10}{'Back diffusion (mol/s)':<20}\n")
        file.write(f"{energy_per_mass:<25.4f}{energy_per_mass2:<30.4f}{(1000 * Ieq / 5):<15.4f}{(Peq * 0.00001):<10.4f}{VC:<10.4f}{back_diff_eq:<20.4e}\n")
        file.write("-" * 100 + "\n")

        file.write(f"{'Point':<15}{'DH (mol/Pa/m/s)':<25}{'Pressure (Bar)':<15}\n")
        file.write("-" * 100 + "\n")
        points = ['Peak_pressure', '1/3', '2/3', 'End_pressure']
        dh_values = [DH_peak, DH_interval1, DH_interval2, DH_end]
        pressure_values = [P_peak, P_interval1, P_interval2, P_end]

        for point, dh, pressure in zip(points, dh_values, pressure_values):
            file.write(f"{point:<15}{dh:<25.4e}{pressure / 100000:<15.4f}\n")
        file.write("-" * 100 + "\n")

        file.write(f"{'Time (s)':<12}{'Pressure (kPa)':<15}{'Pressure (Bar)':<15}{'Current Density (A/m2)':<25}{'Forward Flux (mol/s)':<25}{'Back Diffusion (mol/s)':<25}{'Net Flux (mol/s)':<20}{'Moles Transferred (Forward)':<30}{'Moles Transferred (Backward)':<30}{'Moles Transferred (Net)':<30}{'Voltage Efficiency':<20}{'Flux Efficiency':<20}{'Work Efficiency':<20}\n")

        for i in range(len(time1)):
            time_in_seconds = time1[i]
            pressure_kpa = pressure1[i]
            pressure_bar = pressure_kpa * 0.01
            file.write(
                f"{time_in_seconds:<12.2f}{pressure_kpa:<15.2f}{pressure_bar:<15.4f}{current_density1[i]:<25.4f}"
                f"{forward_flux[i]:<25.6e}{back_diffusion[i]:<25.6e}{net[i]:<20.6e}{integration_forward_flux[i]:<30.8e}"
                f"{integration_back_diff[i]:<30.8e}{integration_net[i]:<30.8e}{voltage_eff[i]:<20.4f}{flux_eff[i]:<20.4f}{work_eff[i]:<20.4f}\n"
            )

        file.write("\n--- Compression shut down ---\n")
        
        if additional_pressure_file:
            with open(additional_pressure_file, 'r') as additional_file:
                additional_lines = additional_file.readlines()

            additional_times = []
            additional_pressures = []

            for line in additional_lines:
                if line.startswith("Time Stamp"):
                    continue
                parts = line.split(';')
                if len(parts) >= 2:
                    time_str = parts[0].strip()
                    pressure_val = float(parts[1].strip())
                    time_obj = datetime.datetime.strptime(time_str, '%d.%m.%Y %H:%M:%S')
                    additional_times.append(time_obj)
                    additional_pressures.append(pressure_val)

            time_com_end = additional_times[0]  
            time_end = additional_times[-1]


            additional_time_seconds = [(t - first_time).total_seconds() for t in additional_times]
            additional_pressure_interpolator = interpolate.interp1d(additional_time_seconds, additional_pressures, kind='linear', fill_value="extrapolate")

            additional_new_time_seconds = np.arange(min(additional_time_seconds), max(additional_time_seconds) + 1, 1)
            additional_interpolated_pressures = additional_pressure_interpolator(additional_new_time_seconds)
            
            for i in range(len(additional_new_time_seconds)):
                time_in_seconds = additional_new_time_seconds[i]
                pressure_bar = additional_interpolated_pressures[i]
                time_str = (first_time + datetime.timedelta(seconds=time_in_seconds)).strftime('%d.%m.%Y %H:%M:%S')
                file.write(f"{time_str};{pressure_bar:.2f}\n")
    
    #-------------------------------------------------------------

    def modify_multiple_lines_in_file_with_time(file_name, line_numbers, first_time, second_time):
        with open(file_name, 'r') as file:
            lines = file.readlines()

        formatted_time1 = first_time.strftime('%Y-%m-%d %H:%M:%S')
        formatted_line1 = f"Compressor shut down:   {formatted_time1}"
        formatted_time2 = second_time.strftime('%Y-%m-%d %H:%M:%S')
        formatted_line2 = f"Measurement ended:      {formatted_time2}"

        for line_number in line_numbers:
            if line_number < 0 or line_number >= len(lines):
                print(f"Řádek {line_number + 1} neexistuje v souboru.")
                continue
        
            lines[line_number] = formatted_line1 + '\n' + formatted_line2 + '\n'
    
        with open(file_name, 'w') as file:
            file.writelines(lines)

    
                    
    print(f"Data exported to: {output_file}")

    modify_multiple_lines_in_file_with_time(output_file, [1], time_com_end, time_end )


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

#---------------------------------------------------------------------

    with open(pressure_sensor1_txt, 'r') as fichier:
        lignes = fichier.readlines()

        first_time = None

        for ligne in lignes[1:]:
            valeurs = ligne.strip().split(';')
    
            if len(valeurs) >= 2:
                pressure1.append(100.0 * float(valeurs[1]))
                time_str = valeurs[0]
                time_obj = datetime.datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S")
        
                if first_time is None:
                    first_time = time_obj

                time_diff = (time_obj - first_time).total_seconds()
                time1.append(time_diff)


    full_time = np.arange(time1[0], time1[-1] + 1)

    full_pressure = np.full(full_time.shape, np.nan)
    indices = np.searchsorted(full_time, time1)
    full_pressure[indices] = pressure1

    full_pressure = np.interp(full_time, time1, pressure1)

    full_times = [first_time + datetime.timedelta(seconds=int(t)) for t in full_time]
    
    time1 = np.array(full_time)
    pressure1 = np.array(full_pressure)
        
#---------------------------------------------------------------------    
#    with open(pressure_sensor1_txt, 'r') as fichier:
#        lignes = fichier.readlines()
#    for ligne in lignes[1:]:
#        valeurs = ligne.strip().split(';')  #pressures separated with ;
#        if len(valeurs) >= 2:
##            print(valeurs[1])
#            pressure1.append(100.0*float(valeurs[1]))

 #   time1 = np.linspace(0, len(pressure1)-1,len(pressure1))

    #------------------------------------------------------------------
    
    with open(chronoamp1, 'r') as fichier:
        lignes = fichier.readlines()

    for ligne in lignes[1:]:
        valeurs = ligne.strip().split()  #chronoamp separated with tab
        if len(valeurs) >= 2:
            time2.append(float(valeurs[0]))
            pot.append(float(valeurs[1]))
            current_density1.append(float(valeurs[2])/A)
            charge.append(float(valeurs[3]))
                    
# Same size

    if len(pressure1)>len(current_density1):
        dif = len(pressure1)-len(current_density1)
        print(len(current_density1))
        pressure1 = pressure1[:-dif]
        time1 = time1[:-dif]
    if len(pressure1)<len(current_density1) :
        dif = len(current_density1)-len(pressure1)
        current_density1 = current_density1[:-dif]
        time2 = time2[:-dif]
        


# forward flux

    forward_flux = (A*np.array(current_density1))/(2*F) #[mol/s]

# permeability DH and back diffusion

    max_index = np.argmax(pressure1)

    data_length = len(pressure1)

    interval1 = int(max_index + (data_length - max_index) / 3)  
    interval2 = int(max_index + 2 * (data_length - max_index) / 3)  

    I_peak = A * current_density1[max_index]
    P_peak = pressure1[max_index] * 10**3

    I_interval1 = A * current_density1[interval1]
    P_interval1 = pressure1[interval1] * 10**3

    I_interval2 = A * current_density1[interval2]
    P_interval2 = pressure1[interval2] * 10**3

    I_end = A * current_density1[-1]
    P_end = pressure1[-1] * 10**3

    DH_peak = I_peak * d / (2 * F * A * P_peak)
    DH_interval1 = I_interval1 * d / (2 * F * A * P_interval1)
    DH_interval2 = I_interval2 * d / (2 * F * A * P_interval2)
    DH_end = I_end * d / (2 * F * A * P_end)

    Ieq = A*np.mean(current_density1[-100:]) #[A]
    Peq = np.mean(pressure1[-100:])*10**3    #[Pa]

    DH = Ieq * d
    DH = DH/(2*F*A*Peq)                       #[mol/Pa/m/s]

    back_diffusion = DH*A*np.array(pressure1)*1000
    back_diffusion = back_diffusion/d          #[mol/s]

    net = np.array(forward_flux)-np.array(back_diffusion) #[mol/s]

#Volume
    
   
    linear_end_index, dP_dt = detect_linear_region_and_calculate_dpdt(pressure1)
    print(f"Rows {linear_end_index}, dP_dt: {dP_dt:.14f}")

    # dP_dt = (pressure1[20]-pressure1[1])/20
    # print(f"dP_dt: {dP_dt}")
    
    Vc = (A*np.mean(current_density1[1:15])*R*T)/(2*F*1000*dP_dt)
    VC = Vc*1000000


    back_diff_eq = np.mean(back_diffusion[-1000:])

# mole transfert
    integration_back_diff = np.zeros_like(back_diffusion)
    integration_forward_flux = np.zeros_like(back_diffusion)
    integration_net = np.zeros_like(back_diffusion)
    
    for i in range(1, len(time1)):
        integration_back_diff[i] = integration_back_diff[i-1] + np.trapezoid(back_diffusion[i-1:i+1], time1[i-1:i+1])
        integration_forward_flux[i] = integration_forward_flux[i-1] + np.trapezoid(forward_flux[i-1:i+1], time1[i-1:i+1])
        integration_forward_flux[0] = 1e-20
        integration_net[i] = integration_net[i-1] + np.trapezoid(net[i-1:i+1], time1[i-1:i+1])
        
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
    print ('\n' 'Jeq =',1000*Ieq/(A*10**4),'mA/cm2')
    print ('Peq =',Peq*0.00001,'Bar')
    print ('DH =',DH,'mol/Pa/m/s')
    print(f"DH (Peak Pressure): {DH_peak}, For pressure: {P_peak/100000:.2f} Pa")
    print(f"DH (1/3): {DH_interval1}, For pressure: {P_interval1/100000:.2f} Pa")
    print(f"DH (2/3): {DH_interval2}, For pressure: {P_interval2/100000:.2f} Pa")
    print(f"DH (End Pressure): {DH_end}, For pressure: {P_end/100000:.2f} Pa")
    print ('Vc =',VC,'cm3')
    print ('Back_diffusion =', back_diff_eq,' mol/s')
    #print ('H2 transfered forward =', integration_forward_flux[14399],'mol')
    #print ('H2 transfered backward =', integration_back_diff[14399],'mol')
    #print ('H2 transfered net =', integration_net[14399],'mol')

    
# effiency

    voltage_eff = R*T*np.log((np.array(pressure1)+100)/100)
    voltage_eff = np.array(voltage_eff)/(2*F*np.mean(pot))
    flux_eff = (np.array(integration_net))/np.array(integration_forward_flux)
    work_eff = np.array(flux_eff)*np.array(voltage_eff)

#Energy consumption
    #Same size
    if len(pressure1)>len(charge):
        dif = len(pressure1)-len(charge)
        #print(len(charge))
        pressure1 = pressure1[:-dif]
    if len(pressure1)<len(charge) :
        dif = len(charge)-len(pressure1)
        charge = charge[:-dif]       

    pressure1_a=np.array(pressure1, copy=True)
    pressure1_a[pressure1_a <= 0] = 1e-10

    work_eff_a=np.array(work_eff, copy=True)
    work_eff_a[work_eff_a <= 0] = 1e-10

    e_charge=1.602176634e-19
    number_e=np.array(charge)/e_charge
    number_H2=np.array(number_e/2)
    n_H2=np.array(number_H2)/6.022e23
    m_H2=np.array(n_H2)*MH2/1000

    m_H2[m_H2 <= 0] = 1e-10

    W_theor=np.array(integration_net)*R*T*np.log(np.array(pressure1_a)*1000)
    W_actual=np.array(W_theor)/np.array(work_eff_a)
    W_actual=np.array(W_actual)/3.6e6

    EC=np.array(W_actual)/np.array(m_H2)

# Assignation of the data

    x1 = time1
    x2 = time2
    y1 = pressure1
    y2 = current_density1
    y3 = forward_flux
    y4 = back_diffusion
    y5 = net
    y6 = EC

    voltage = np.mean(pot)

    export(chronoamp1, pressure_sensor1_txt, voltage, time1, pressure1, current_density1, forward_flux, back_diffusion, net, voltage_eff, flux_eff, work_eff, integration_forward_flux, integration_back_diff, integration_net, energy_per_mass, energy_per_mass2, Ieq, Peq, DH, VC, back_diff_eq, d1, DH_peak, DH_interval1, DH_interval2, DH_end, P_peak, P_interval1, P_interval2, P_end, additional_pressure_file="P2.csv")

# ------------------- Current density and pressure Vs time plot ------------------------

# Creation of the figure and the main axis
    fig1, ax1 = plt.subplots(figsize=(9, 5))

#Plotting the first data series on ax1

    pressure_in_bar=np.array(y1)*0.01
    
    ax1.plot(time1/3600, pressure_in_bar, 'b-', label='relative cathode pressure [Bar]')
    ax1.set_xlabel('time [hours]',fontsize=14)
    ax1.set_ylabel('relative cathode pressure [Bar]', color='b',fontsize=14)
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

    #--------------------Graph energy consumption-------------------

# Creation of the figure and the main axis
    fig6, ax6 = plt.subplots(figsize=(9, 5))

#Plotting the first data series on ax1
    ax6.plot(np.array(time1[1:])/3600, np.array(y6[1:]), 'b-', label='Energy consumption [kWh/kg]')
    ax6.set_xlabel('Time [h]', fontsize=14)
    ax6.set_ylabel('Energy consumption [kWh/kg]', color='b', fontsize=14)
    

# legends
    fig6.tight_layout()
    ax6.legend(loc='upper right', bbox_to_anchor=(1, 1))
    ax6.grid(True, which='both', axis='x', linestyle='--', linewidth=0.5)

# title and show

    ax6.set_title('Energy consumption VS  Time', fontsize=14)


# ------- Graphs all efficiencies of one potential vs time  ----------------


    fig3, ax4 = plt.subplots(figsize=(10, 6))

    ax4.plot(time1/3600, voltage_eff, 'b-', label='voltage efficiency')
    ax4.plot(time1[1:]/3600, flux_eff[1:], 'r-', label='flux efficiency')
    ax4.plot(time1/3600, work_eff, 'g-', label='work efficiency')

    ax4.set_xlabel('time [hours]', fontsize=14)
    ax4.set_ylabel('efficiency [%]', color='b',fontsize=14)
    ax4.yaxis.set_major_formatter(FuncFormatter(percentage))

    ax4.grid(True)

    ax4.legend(loc='center right')

    
    ax4.set_title('Efficiencies - %.2f V' % voltage,fontsize=14)

    plt.show()
    
    return ()



#-------------------------------------------------------------------------            
#-------------------------------------------------------------------------


def fit_data_exp(depressure_file, DH):
##    depressure_file = input("Enter the name of the data file: ")
##    DH = eval(input("Enter the DH value: "))
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
            depressure.append(float(valeurs[1]))

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
    ax1.set_ylabel('pressure [Bar]')
    ax1.plot(t/3600, data, "o", label='Sample data')
    ax1.plot(time_fit/3600, fitfunc(p1, time_fit), label='Fit')
    ax1.legend(title='0.02V', fancybox=True, loc='upper right')
    print('\n' 'The volume is', V,'cm3')
    plt.show()
    return(p1[1])

dataplot("CA", "P.csv")

#fit_data_exp("P2.csv", 1.2088e-14)

