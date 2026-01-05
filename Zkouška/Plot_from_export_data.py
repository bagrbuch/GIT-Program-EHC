import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from scipy.optimize import leastsq
from datetime import datetime

#------------------ Function to format percentage ------------------------------------
def percentage(x, pos):
    'The two args are the value and tick position'
    return '%1.0f' % (x * 100)

#-------------- Function to plot graphs from the export file--------------------------
def plot_graphs_from_export(export_file):
    print("Loading data\n")
    
    time1, pressure1, pressure1_bar, current_density1, forward_flux, back_diffusion, net_flux, forward_moles, back_moles, net_moles, voltage_eff, flux_eff, work_eff = [], [], [], [], [], [], [], [], [], [], [], [], []
    DH, d = None, None  
    DH_values = [] 

    with open(export_file, 'r') as file:
        lines = file.readlines()

        for i, line in enumerate(lines):

            #Searching for the thickness of membrane (d)
            if 'Thickness of the membrane' in line:    
                d_value = line.split(":")[1].strip()

                import re
                match = re.search(r"[-+]?\d*\.?\d+", d_value)  
                if match:
                    d_numeric = float(match.group(0))  
                    d = d_numeric * 10**-6
                    d = round(d, 10)
                else:
                    raise ValueError("Could not extract a valid thickness value from the line.")

            #Searching for the DH values
            if 'Point' in line:
                continue
            if 'Peak pressure' in line or '1/3' in line or '2/3' in line or 'End pressure' in line:
                line_data = line.split()
                DH_value = float(line_data[1])  
                DH_values.append(DH_value)
            
            #Searching for volume (Vc)
            if 'Vc (cm3)' in line:
                try:
                    next_line = lines[i + 1].strip()  
                    line_data = next_line.split()  
                    Vc_value = float(line_data[4])  
                    Vc = Vc_value                    
                except (IndexError, ValueError) as e:
                    print(f"Error extracting Vc value: {e}")
                    continue

        # Calculate the average DH value
        if DH_values:
            DH = np.mean(DH_values)

        print(f"Average DH value: {DH:.4e}")
        print(f"Thickness of the membrane: {d} m \n")
        print(f"The volume calculate from current and Dp/dt: {Vc} cm³")

        

            

        for line in lines[16:]:  # Skipping the header lines
            if "--- Compression shut down ---" in line:
                break 

            try:
                time_in_seconds = float(line[0:12].strip()) if line[0:12].strip() != '' else None  # Time in seconds
                pressure_kpa = float(line[12:27].strip()) if line[12:27].strip() != '' else None  # Pressure in kPa
                pressure_bar = float(line[27:42].strip()) if line[27:42].strip() != '' else None  # Pressure in Bar
                current_density = float(line[42:67].strip()) if line[42:67].strip() != '' else None  # Current Density
                forward_flux_val = float(line[67:92].strip()) if line[67:92].strip() != '' else None  # Forward Flux
                back_diffusion_val = float(line[92:117].strip()) if line[92:117].strip() != '' else None  # Back Diffusion
                net_flux_val = float(line[117:137].strip()) if line[117:137].strip() != '' else None  # Net Flux
                forward_moles_val = float(line[137:167].strip()) if line[137:167].strip() != '' else None  # Moles Transferred (Forward)
                back_moles_val = float(line[167:197].strip()) if line[167:197].strip() != '' else None  # Moles Transferred (Backward)
                net_moles_val = float(line[197:227].strip()) if line[197:227].strip() != '' else None  # Moles Transferred (Net)
                voltage_eff_val = float(line[227:247].strip()) if line[227:247].strip() != '' else None  # Voltage Efficiency
                flux_eff_val = float(line[247:267].strip()) if line[247:267].strip() != '' else None  # Flux Efficiency
                work_eff_val = float(line[267:287].strip()) if line[267:287].strip() != '' else None  # Work Efficiency

                if time_in_seconds is not None:
                    time1.append(time_in_seconds)
                if pressure_kpa is not None:
                    pressure1.append(pressure_kpa)
                if pressure_bar is not None:
                    pressure1_bar.append(pressure_bar)
                if current_density is not None:
                    current_density1.append(current_density)
                if forward_flux_val is not None:
                    forward_flux.append(forward_flux_val)
                if back_diffusion_val is not None:
                    back_diffusion.append(back_diffusion_val)
                if net_flux_val is not None:
                    net_flux.append(net_flux_val)
                if forward_moles_val is not None:
                    forward_moles.append(forward_moles_val)
                if back_moles_val is not None:
                    back_moles.append(back_moles_val)
                if net_moles_val is not None:
                    net_moles.append(net_moles_val)
                if voltage_eff_val is not None:
                    voltage_eff.append(voltage_eff_val)
                if flux_eff_val is not None:
                    flux_eff.append(flux_eff_val)
                if work_eff_val is not None:
                    work_eff.append(work_eff_val)

            except ValueError:
                print("Error in loading data")
                continue

    time1 = np.array(time1) / 3600  # Convert time to hours
    pressure1 = np.array(pressure1)
    current_density1 = np.array(current_density1) / 10**4  # Scale current density to cm2
    forward_flux = np.array(forward_flux)
    back_diffusion = np.array(back_diffusion)
    net_flux = np.array(net_flux)
    forward_moles = np.array(forward_moles)
    back_moles = np.array(back_moles)
    net_moles = np.array(net_moles)
    voltage_eff = np.array(voltage_eff)
    flux_eff = np.array(flux_eff)
    work_eff = np.array(work_eff)
    
    
    # ------------------- Current density and pressure Vs time plot ------------------------
    fig1, ax1 = plt.subplots(figsize=(9, 5))

    # Plotting pressure data on ax1
    ax1.plot(time1, pressure1_bar, 'b-', label='Relative cathode pressure [Bar]')
    ax1.set_xlabel('Time [hours]', fontsize=14)
    ax1.set_ylabel('Pressure [Bar]', color='b', fontsize=14)
    ax1.tick_params(axis='y', labelcolor='b')

    # Creating a second y-axis for current density plot
    ax2 = ax1.twinx()
    ax2.plot(time1, current_density1, 'r-', label='Current Density [A/cm²]')
    ax2.set_ylabel('Current Density [A/cm²]', color='r', fontsize=14)
    ax2.tick_params(axis='y', labelcolor='r')

    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    fig1.tight_layout()
    ax1.set_title('Current Density and Relative Cathode Pressure')

    # ------------------- Current density vs Pressure ------------------------
    fig5, ax5 = plt.subplots(figsize=(9, 5))

    ax5.plot(pressure1, current_density1, 'b-', label='Current Density vs Pressure')
    ax5.set_xlabel('Pressure [kPa]', fontsize=14)
    ax5.set_ylabel('Current Density [A/cm²]', color='b', fontsize=14)
    ax5.tick_params(axis='y', labelcolor='b')

    ax5.legend(loc='upper right')
    ax5.grid(True, which='both', linestyle='--', linewidth=0.5)
    fig5.tight_layout()
    ax5.set_title('Current Density vs Relative Cathode Pressure')

    # --------------------- Flow Diffusion plot ------------------------
    fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 6))

    ax3.plot(time1, forward_flux, 'b-', label='Forward Flux [mol/s]')
    ax3.plot(time1, back_diffusion, 'r-', label='Back Diffusion [mol/s]')
    ax3.plot(time1, net_flux, 'g-', label='Net Flux [mol/s]')
    ax3.set_xlabel('Time [hours]', fontsize=14)
    ax3.set_ylabel('Flux [mol/s]', fontsize=14)
    ax3.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax3.legend(loc='center right')
    ax3.set_title('Flux Diffusion')

    ax4.plot(time1, forward_moles, 'b-', label='Moles Transferred (Forward)')
    ax4.plot(time1, back_moles, 'r-', label='Moles Transferred (Backward)')
    ax4.plot(time1, net_moles, 'g-', label='Moles Transferred (Net)')
    ax4.set_xlabel('Time [hours]', fontsize=14)
    ax4.set_ylabel('Moles Transferred [mol]', fontsize=14)
    ax4.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax4.legend(loc='center right')
    ax4.set_title('Moles Transferred')

    # ------------------- Efficiency plot ------------------------
    fig2, ax2 = plt.subplots(figsize=(10, 6))

    ax2.plot(time1, voltage_eff, 'b-', label='Voltage Efficiency')
    ax2.plot(time1[1:], flux_eff[1:], 'r-', label='Flux Efficiency')
    ax2.plot(time1, work_eff, 'g-', label='Work Efficiency')
    ax2.set_xlabel('Time [hours]', fontsize=14)
    ax2.set_ylabel('Efficiency', fontsize=14)
    ax2.yaxis.set_major_formatter(FuncFormatter(percentage))
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax2.legend(loc='center right')
    ax2.set_title('Efficiencies')

    plt.tight_layout()
    plt.show()

    #----------------------------------------------

    fit_data_exp(export_file, DH, d)

# -----------------------------------Function to fit the experimental data------------------------------------------------------
def fit_data_exp(depressure_file, DH, d):
    ini = 0.000011  # Expected volume (m3)
    pp = 17         # Initial guess for pressure

    A = 5 * 10**-4  # [m2] Active area of the fuel cell
    F = 96485.3321233100184  # [C/mol]
    R = 8.314      # (J/mol.K)
    T = 25 + 273.5  # (25°C)

    depressure = []
    with open(depressure_file, 'r') as fichier:
        lignes = fichier.readlines()

    start_index = None
    for i, ligne in enumerate(lignes):
        if "--- Compression shut down ---" in ligne:
            start_index = i + 1
            break

    if start_index is None:
        print("Error: Incorrect file format or missing shutdown section.")
        return

    for ligne in lignes[start_index:]:
        valeurs = ligne.strip().split(';')  # Data separated by ';'
        if len(valeurs) >= 2:
            depressure.append(float(valeurs[1]))

    if not depressure:
        print("Error: No data found after the shutdown section.")
        return

    time = np.arange(len(depressure))

    Peq = depressure[0]

    fitfunc = lambda p, x: Peq * np.exp(-(A * R * T * x * DH) / (d * p[0])) + p[1]
    errfunc = lambda p, x, y: fitfunc(p, x) - y

    p0 = [ini, pp]
    p1, success = leastsq(errfunc, p0[:], args=(time, depressure))
    
    # Convert volume to cm³
    V = p1[0] * 1e6
    
    # Generate fitted data
    time_fit = np.linspace(time.min() - 1, time.max() + 1, 100)
    
    # Plot results
    fig, ax1 = plt.subplots()
    ax1.set_title('Depressure Fit')
    ax1.set_xlabel('Time [h]')
    ax1.set_ylabel('Pressure [Bar]')
    ax1.plot(time / 3600, depressure, "o", label='Sample Data')
    ax1.plot(time_fit / 3600, fitfunc(p1, time_fit), label='Fit')
    ax1.legend(title='Fit Legend', fancybox=True, loc='upper right')
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

    print(f"The volume from exponencial fit: {V:.4f} cm³\n")
    plt.show()

    return p1[1]

#--------------------------------------------------------------------------------------

plot_graphs_from_export("Export_data.txt")
