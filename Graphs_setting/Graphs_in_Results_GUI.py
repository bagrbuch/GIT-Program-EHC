import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

try:
    matplotlib.use('TkAgg')
except ImportError:
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
from scipy.optimize import leastsq

#------------------ Function to format percentage ------------------------------------
def percentage(x, pos):
    'The two args are the value and tick position'
    return '%1.0f' % (x * 100)

#-------------- Function to plot graphs from the export file--------------------------
def plot_graphs_from_export(export_file, selected_graphs):

    #-------------- Finding data--------------------------

    print("-------Loading data--------\n")
    
    time1, pressure1, pressure1_bar, current_density1, forward_flux, back_diffusion, net_flux, forward_moles, back_moles, net_moles,EC, voltage_eff, flux_eff, work_eff = [], [], [], [], [], [], [], [], [], [], [], [], [], []
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
                pp = float(line_data[2])  
                DH_values.append(DH_value)

            #Searching for volume (Vc)
            if 'Vc (cm3)' in line:
                try:
                    next_line = lines[i + 1].strip()  
                    line_data = next_line.split()  
                    Vc_value = float(line_data[3])  
                    Vc = Vc_value                    
                except (IndexError, ValueError) as e:
                    print(f"Error extracting Vc value: {e}")
                    continue

        # Calculate the average DH value
        if DH_values:
            DH = np.mean(DH_values)

        print(f"Average DH value: {DH:.4e}\n")
        #print(f"Thickness of the membrane: {d} m \n")
        print(f"The volume calculate from current and Dp/dt: {Vc} cm³\n")     

        for line in lines[22:]:  # Skipping the header lines
            if "--- Compression shut down ---" in line:
                break 

            try:
                time_in_seconds = float(line[0:12].strip()) if line[0:12].strip() else None  # Time in seconds
                pressure_kpa = float(line[12:27].strip()) if line[12:27].strip() else None  # Pressure in kPa
                pressure_bar = float(line[27:42].strip()) if line[27:42].strip() else None  # Pressure in Bar
                current_density = float(line[42:67].strip()) if line[42:67].strip() else None  # Current Density
                forward_flux_val = float(line[67:92].strip()) if line[67:92].strip() else None  # Forward Flux
                back_diffusion_val = float(line[92:117].strip()) if line[92:117].strip() else None  # Back Diffusion
                net_flux_val = float(line[117:137].strip()) if line[117:137].strip() else None  # Net Flux
                forward_moles_val = float(line[137:167].strip()) if line[137:167].strip() else None  # Moles Transferred (Forward)
                back_moles_val = float(line[167:197].strip()) if line[167:197].strip() else None  # Moles Transferred (Backward)
                net_moles_val = float(line[197:227].strip()) if line[197:227].strip() else None  # Moles Transferred (Net)
                EC_val = float(line[227:257].strip()) if line[227:257].strip() else None  # Energy Consumption (EC)
                voltage_eff_val = float(line[257:277].strip()) if line[257:277].strip() else None  # Voltage Efficiency
                flux_eff_val = float(line[277:297].strip()) if line[277:297].strip() else None  # Flux Efficiency
                work_eff_val = float(line[297:317].strip()) if line[297:317].strip() else None  # Work Efficiency

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
                if EC_val is not None:
                    EC.append(EC_val)
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
    EC = np.array(EC)
    voltage_eff = np.array(voltage_eff)
    flux_eff = np.array(flux_eff)
    work_eff = np.array(work_eff)
    
    #print(f"Obsah selected_graphs: {selected_graphs}")

    #-------------- Plot graphs from finded data--------------------------


    plt.rcParams.update({
        'font.size': 12,
        'font.family': 'sans-serif',
        'axes.titlesize': 12,
        'axes.labelsize': 12,
        'legend.fontsize': 11,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'lines.linewidth': 2,
    })

    colors = plt.cm.tab10.colors
    color_index = 0
    color = colors[color_index % len(colors)]

    for graph_name in selected_graphs:

        if graph_name == 1:
            # ------------------- Proudová hustota a tlak vs čas ------------------------
            fig1, ax1 = plt.subplots(figsize=(7.1, 4.3))

            ax1.plot(time1, pressure1_bar, color=color, label='Pressure [bar]')
            ax1.set_xlabel('Time [hours]')
            ax1.set_ylabel('Pressure [bar]', color=color)
            ax1.tick_params(axis='y', labelcolor=color)
            
            color_index = color_index+1
            color = colors[color_index % len(colors)]

            ax2 = ax1.twinx()
            ax2.plot(time1, current_density1, color=color, label='Current density [A/cm²]')
            ax2.set_ylabel('Current density [A/cm²]', color=color)
            ax2.tick_params(axis='y', labelcolor=color)
            
            ax1.grid(True, linestyle='--', linewidth=0.5)
            fig1.tight_layout()
            plt.show()

            color_index = 0
            color = colors[color_index % len(colors)]

        elif graph_name == 2:
            # ------------------- Proudová hustota vs tlak ------------------------
            fig5, ax5 = plt.subplots(figsize=(7.1, 4.3))

            ax5.plot(pressure1, current_density1, color=color, label='Current density vs Pressure')
            ax5.set_xlabel('Pressure [kPa]')
            ax5.set_ylabel('Current density [A/cm²]')
            ax5.tick_params(axis='y')

            ax5.legend(loc='upper right')
            ax5.grid(True, linestyle='--', linewidth=0.5)
            ax5.set_title('Current density vs Relative pressure of the cathode')
            fig5.tight_layout()
            plt.show()

        elif graph_name == 3:
            # --------------------- Difuze toku a přenesené moly ------------------------
            fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(10.2, 4.3)) 
           
            ax3.plot(time1, forward_flux, color=color, label='Forward flux [mol/s]')
            ax4.plot(time1, forward_moles, color=color, label='Forward')

            color_index = color_index+1
            color = colors[color_index % len(colors)]

            ax3.plot(time1, back_diffusion, color=color, label='Backward flux [mol/s]')
            ax4.plot(time1, back_moles, color=color, label='Back')

            color_index = color_index+1
            color = colors[color_index % len(colors)]

            ax3.plot(time1, net_flux, color=color, label='Total flux [mol/s]')
            ax4.plot(time1, net_moles, color=color, label='Total')

            ax3.set_xlabel('Time [hours]')
            ax3.set_ylabel('Flux [mol/s]')
            ax3.grid(True, linestyle='--', linewidth=0.5)
            ax3.legend(loc='center right')
            ax3.set_title('Diffusion of flux')
           
            ax4.set_xlabel('Time [hours]')
            ax4.set_ylabel('Transported molekules [mol]')
            ax4.grid(True, linestyle='--', linewidth=0.5)
            ax4.legend(loc='center right')
            ax4.set_title('Transported molekules')
            fig.tight_layout()

            plt.show()

            color_index = 0
            color = colors[color_index % len(colors)]            
            
        elif graph_name == 4:
            # ------------------- Spotřeba energie ------------------------
            fig4, ax6 = plt.subplots(figsize=(7.1, 4.3))

            ax6.plot(pressure1 / 100, EC, color=color, label='Energy consumption [kWh/kg]')
            ax6.set_xlabel('Pressure [bar]')
            ax6.set_ylabel('Energy consumption [kWh/kg]')
            #ax6.legend(loc='upper left')
            ax6.grid(True, linestyle='--', linewidth=0.5)
            #ax6.set_title('Spotřeba energie vs tlak')
            fig4.tight_layout()
            
            plt.show()

        elif graph_name == 5:
            # ------------------- Účinnosti ------------------------
            fig2, ax2 = plt.subplots(figsize=(7.1, 4.3))

            ax2.plot(time1, voltage_eff*100, color=color, label='Voltage efficiency')

            color_index = color_index+1
            color = colors[color_index % len(colors)]

            ax2.plot(time1[1:], flux_eff[1:]*100, color=color, label='Flux efficiency')

            color_index = color_index+1
            color = colors[color_index % len(colors)]

            ax2.plot(time1, work_eff*100, color=color , label='Work efficiency')
            
            ax2.set_xlabel('Time [hours]')
            ax2.set_ylabel('Efficiency [%]')
            ax2.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.0f}'))

            ax2.grid(True, linestyle='--', linewidth=0.5)
            ax2.legend(loc='lower right')
            #ax2.set_title('Účinnosti')
            fig2.tight_layout()

            plt.show()

            color_index = 0
            color = colors[color_index % len(colors)]
            
        elif graph_name == 6:
            # ------------------- Proudová hustota a tlak vs čas ------------------------
            fig1, ax1 = plt.subplots(figsize=(7.1, 4.3))

            ax1.plot(time1, pressure1_bar, color=color, label='Pressure [bar]')
            ax1.set_xlabel('Time [hours]')
            ax1.set_ylabel('Pressure [bar]', color=color)
            ax1.tick_params(axis='y', labelcolor=color)

            color_index = color_index+1
            color = colors[color_index % len(colors)]

            ax2 = ax1.twinx()
            ax2.plot(time1, work_eff*100, color=color, label='Work efficiency [%]')
            ax2.set_ylabel('efficiency [%]', color=color)
            ax2.set_ylim(-5, 105)
            ax2.tick_params(axis='y', labelcolor=color)
            
            ax1.grid(True, linestyle='--', linewidth=0.5)
            #ax1.set_title('Proudová hustota a absolutní tlak na katodycké straně kompresoru')
            fig1.tight_layout()
            
            plt.show()

            color_index = 0
            color = colors[color_index % len(colors)]

        elif graph_name == 8:
            #------------------------- Net flux vs efficiency -----------------------
            fig7, (ax8, ax9) = plt.subplots(1, 2, figsize=(10.2, 4.3))
            
            ax8.plot(net_flux, work_eff*100, color=color, label='Work efficiency')

            ax8.set_xlabel('Net flux [mol/s]')
            ax8.set_ylabel('Efficiency [%]')
            ax8.tick_params(axis='y')

            #ax8.legend(loc='upper right')
            ax8.grid(True, linestyle='--', linewidth=0.5)
            ax8.set_title('Work efficiency vs Net flux')

            ax9.plot(np.array(pressure1)/100, net_flux, color=color, label='Net flux')
            ax9.set_xlabel('Pressure [bar]')
            ax9.set_ylabel('Net flux [mol/s]', color= color )
            ax9.tick_params(axis='y', labelcolor= color)

            color_index = color_index+1
            color = colors[color_index % len(colors)]

            ax10 = ax9.twinx()
            ax10.plot(np.array(pressure1)/100, work_eff*100, color=color, label='Work efficiency')
            ax10.set_ylabel('Work efficeincy [%]', color= color )
            ax10.tick_params(axis='y', labelcolor= color)
            ax9.grid(True, linestyle='--', linewidth=0.5)
            ax9.set_title('Pressure vs Net flux, efficiency')

            plt.show()

    #----------------------------------------------
    #----------------------------------------------

        
    fit_data_exp(export_file, DH, d, Vc/1000000, pp, selected_graphs)

# -----------------------------------Function to fit the experimental data------------------------------------------------------
def fit_data_exp(depressure_file, DH, d, ini, pp, selected_graphs):
            # ini = 0.000011  # Expected volume (m3)
            # pp = 17         # Initial guess for pressure

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
            for graph_name in selected_graphs:
                if graph_name == 7:

                    # Plot results
                    fig, ax1 = plt.subplots()
                    #ax1.set_title('Depressure Fit')
                    ax1.set_xlabel('Time [hour]')
                    ax1.set_ylabel('Pressure [bar]')
                    ax1.plot(time / 3600, depressure, ".", label='Measured data')
                    ax1.plot(time_fit / 3600, fitfunc(p1, time_fit), label='Approximation')
                    ax1.legend(fancybox=True, loc='upper right')
                    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
                    fig.tight_layout()
                    # print(f"d: {d} \n")
                    
                    plt.show()

            print(f"\n The volume from exponencial fit: {V:.2f} cm³\n")

            return p1[1]

        #--------------------------------------------------------------------------------------

        #plot_graphs_from_export("Export_data.txt")
