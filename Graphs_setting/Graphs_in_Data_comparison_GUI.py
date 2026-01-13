import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

try:
    matplotlib.use('TkAgg')
except ImportError:
    matplotlib.use('Agg')

import matplotlib.colors as mcolors
from scipy.optimize import curve_fit   
from matplotlib import rc, rcParams


def plot_graphs_for_group(selected_graphs, group):
    """
    Vykreslí porovnávací grafy pro zadanou skupinu souborů.
    """
    x_value = group["x_value"]
    files = group["files"]

    # -------------- Graph parameters and size -----------------

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

    figs_axes = {}

    if 1 in selected_graphs:
        fig1, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        figs_axes[1] = (fig1, ax1, ax2)

    if 4 in selected_graphs:
        fig4, ax4 = plt.subplots(figsize=(7.1, 4.3))
        figs_axes[4] = (fig4, ax4)

    if 5 in selected_graphs:
        fig5, ax5 = plt.subplots(figsize=(7.1, 4.3))
        figs_axes[5] = (fig5, ax5)

    if 6 in selected_graphs:
        fig7, ax8 = plt.subplots(figsize=(7.1, 4.3))
        figs_axes[6] = (fig7, ax8)

    if 6 in selected_graphs:
        fig8, ax9 = plt.subplots()
        ax10 = ax9.twinx()
        figs_axes[7] = (fig8, ax9, ax10)

    colors = plt.cm.tab10.colors
    #colors = ['b', 'r', 'g', 'm', 'c']
    color_index = 0

    for file in files:
        time1, pressure1_bar, current_density1, EC, work_eff, net_flux = [], [], [], [], [], []

        try:
            with open(file, 'r') as f:
                lines = f.readlines()

            for line in lines[23:]:  # Přeskočení hlavičky
                if "--- Compression shut down ---" in line:
                    break
                try:
                    time1.append(float(line[0:12].strip()) / 3600)
                    pressure1_bar.append(float(line[27:42].strip()))
                    current_density1.append(float(line[42:67].strip()) / 10**4)
                    EC.append(float(line[227:257].strip()))
                    work_eff.append(float(line[297:317].strip()) * 100)
                    net_flux.append(float(line[117:137].strip()))
                except ValueError:
                    continue
        except Exception as e:
            print(f"Chyba při načítání {file}: {e}")
            continue

        color = colors[color_index % len(colors)]
        color_index += 1

        filename = os.path.basename(file)
        result = "_".join(os.path.splitext(filename)[0].split('_')[2:])

#------------------------------- Axes ---------------------------------

        if 1 in selected_graphs:
            fig1, ax1, ax2 = figs_axes[1]
            ax1.plot(time1, pressure1_bar, label=f'{result} - Pressure', color=color, linewidth=1.5)
            ax2.plot(time1, current_density1, label=f'{result} - Current', linestyle='dashed', color=color, linewidth=1)

        if 4 in selected_graphs:
            fig4, ax4 = figs_axes[4]
            ax4.plot(pressure1_bar, EC, label=f'{result}', color=color, linewidth=1.5)

        if 5 in selected_graphs:
            fig5, ax5 = figs_axes[5]
            ax5.plot(time1, work_eff, label=f'{result}', color=color, linewidth=1.5)

        if 6 in selected_graphs:
            fig7, ax8 = figs_axes[6]
            ax8.plot(net_flux, work_eff, color=color, label=f'{result}', linewidth=1.5)

        if 6 in selected_graphs:
            fig8, ax9, ax10 = figs_axes [7]
            ax9.plot(pressure1_bar, net_flux, color=color, label=f'{result}')
            ax10.plot(pressure1_bar, work_eff, color=color, label=f'{result}')

    # ------------------- Current density and pressure vs. time ------------------------
    if 1 in selected_graphs:
        ax1.set_xlabel('Time [hours]')
        ax1.set_ylabel('Pressure [Bar]')
        ax2.set_ylabel('Current Density [A/cm²]')
        ax1.tick_params(axis='y')
        ax2.tick_params(axis='y')
        ax1.grid(True, linestyle='--', alpha=0.6)
        ax1.legend(loc='upper left', fontsize=9)
        ax2.legend(loc='upper right', fontsize=9)
        ax1.set_title(f'Pressure & Current Density vs Time @ U = {x_value} V')
        plt.tight_layout()

    # -------------------- Energy consumption vs. pressure -------------------
    if 4 in selected_graphs:
        ax4.set_xlabel('Pressure [Bar]')
        ax4.set_ylabel('Energy consumption [kWh/kg]')
        ax4.legend()
        ax4.grid(True, linestyle='--', alpha=0.6)
        ax4.set_title(f'Energy Consumption vs Pressure @ U = {x_value} V')
        plt.tight_layout()

    # --------------------------- Efficiency vs. time------------------------    
    if 5 in selected_graphs:
        ax5.set_xlabel('Time [h]')
        ax5.set_ylabel('Efficiency [%]')
        ax5.legend(loc='lower left')
        ax5.grid(True, linestyle='--', alpha=0.6)
        ax5.set_title(f'Efficiency vs Time @ U = {x_value} V')
        plt.tight_layout()

    #------------------------- Net flux vs efficiency -----------------------
    if 6 in selected_graphs:
        ax8.set_title('Net flux vs efficiency')
        ax8.set_xlabel('Net flux [mol/s]')
        ax8.set_ylabel('Efficiency [%]')
        ax8.legend(loc='upper right')
        ax8.tick_params(axis='y')
        ax8.grid(True, linestyle='--', linewidth=0.5)
        plt.tight_layout()        
             
    if 6 in selected_graphs:
        ax9.set_xlabel('Pressure [bar]')
        ax9.set_ylabel('Net flux [mol/s]')
        ax9.legend(loc='center right')
        ax9.tick_params(axis='y')
        ax9.grid(True, linestyle='--', linewidth=0.5)
        ax9.set_title('Pressure vs Net flux, efficiency')
        ax10.set_ylabel('Work efficeincy [%]')
        ax10.tick_params(axis='y')
        plt.tight_layout()

    plt.show()

def get_hex_color(color_name):
    """Převede barvu na HEX formát."""
    try:
        return mcolors.to_hex(color_name)
    except ValueError:
        return color_name

def linear_fit(x, a, b):
    return a * x + b

def log_fit(x, a, b):
    return a * np.log(x) + b

def plot_graph(output_data):
    """
    Vytvoří 2D scatter plot zobrazující pouze průměrné body maximální účinnosti pro každé x_value.
    """
    base_colors = list(mcolors.TABLEAU_COLORS.values())  # Použití předdefinovaných barev
    color_map = {}
    max_efficiency_points = {}
    
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['figure.figsize'] = 4,3
    plt.rcParams['figure.autolayout'] = True

    fig, ax = plt.subplots()
    for group in output_data:
        for file_path in group["files"]:
            # Extract the filename
            file_name = os.path.basename(file_path)
            parent_folder = os.path.dirname(os.path.dirname(file_path))
            # Get the first part of the filename before the first underscore
            base_name = file_name.split('_')[2]
    
    for idx, group in enumerate(output_data):
        files = group['files']
        x_value = group['x_value']
        
        if x_value not in color_map:
            color_map[x_value] = get_hex_color(base_colors[idx % len(base_colors)])
        
        base_color = color_map[x_value]
        
        max_eff_list = []
        
        for file in files:
            time1, pressure1_bar, EC, totowork_eff_vals = [], [], [], []

            try:
                with open(file, 'r') as f:
                    lines = f.readlines()

                for line in lines[23:]:
                    if "--- Compression shut down ---" in line:
                        break
                    try:
                        pressure1_bar.append(float(line[27:42].strip()))
                        EC.append(float(line[227:257].strip()))
                        totowork_eff_val = float(line[297:317].strip()) if line[297:317].strip() else None
                        totowork_eff_vals.append(totowork_eff_val)
                    except ValueError:
                        continue
            except Exception as e:
                print(f"Chyba při načítání {file}: {e}")
                continue

            if totowork_eff_vals:
                max_index = np.argmax(totowork_eff_vals)
                max_eff_list.append((pressure1_bar[max_index], EC[max_index]))
        
        # Průměr z nalezených maximálních bodů
        if max_eff_list:
            avg_pressure = np.mean([p for p, _ in max_eff_list])
            avg_EC = np.mean([e for _, e in max_eff_list])
            max_efficiency_points[x_value] = (avg_pressure, avg_EC)
            ax.scatter(avg_pressure, avg_EC, color=base_color, s=100, marker='x', label=f'U={x_value}V')
    
    # Fitování dat
    pressures = np.array([p for p, _ in max_efficiency_points.values()])
    ECs = np.array([e for _, e in max_efficiency_points.values()])
    
    if len(pressures) > 1:
        popt_linear, _ = curve_fit(linear_fit, pressures, ECs)
        popt_log, _ = curve_fit(log_fit, pressures, ECs)
        
        pressure_range = np.linspace(min(pressures) * 0.08, max(pressures) * 5, 100)  # Rozšíření rozsahu
        ax.plot(pressure_range, linear_fit(pressure_range, *popt_linear), 'r-', label='Linear approximation')
        ax.plot(pressure_range, log_fit(pressure_range, *popt_log), 'b-', label='Logarithmic approximation')


    # Popisky os
    
    ax.set_xlabel("Pressure [bar]",fontsize=10)
    ax.set_ylabel("Energy consumption [kWh/kg]",fontsize=10)
    # ax.set_title(f'Max efficiency points by voltage for membrane: {base_name} ')
    ax.legend()
    ax.set_xlim(0,100)  # Nastavení limitu osy X od 0
    ax.set_ylim(0,7)  # Nastavení limitu osy Y od 0
    ax.grid(True, linestyle='--', linewidth=0.5)
    plt.show()

def plot_2d_graph(output_data):
    """
    Vytvoří 2D graf průměrného Compression rate a tlaku v závislosti na čase.
    """
    base_colors = list(mcolors.TABLEAU_COLORS.values())  # Předdefinované barvy
    color_map = {}
    max_points = []
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()  # Druhá osa Y pro tlak

    for idx, group in enumerate(output_data):
        files = group['files']
        x_value = group['x_value']
        
        if x_value not in color_map:
            color_map[x_value] = base_colors[idx % len(base_colors)]
        
        base_color = color_map[x_value]
        all_time_values = []
        all_net_flux_values = []
        all_efficiency_values = []
        all_pressure_bar_values = []
        
        for file in files:
            time1, net_flux_vals, totowork_eff_vals, pressure_bars = [], [], [], []
            
            try:
                with open(file, 'r') as f:
                    lines = f.readlines()
                
                for line in lines[23:]:
                    if "--- Compression shut down ---" in line:
                        break
                    try:
                        time1.append(float(line[0:12].strip()) / 3600)
                        net_flux_val = float(line[117:137].strip()) * 2.016 * 3600 * 24 / 5 * 1000 if line[117:137].strip() else None
                        net_flux_vals.append(net_flux_val)
                        totowork_eff_val = float(line[297:317].strip()) if line[297:317].strip() else None
                        totowork_eff_vals.append(totowork_eff_val)
                        pressure_bar = float(line[27:42].strip()) if line[27:42].strip() else None  # Pressure in Bar
                        pressure_bars.append(pressure_bar)
                    except ValueError:
                        continue
            except Exception as e:
                print(f"Chyba při načítání {file}: {e}")
                continue
            
            all_time_values.append(np.array(time1))
            all_net_flux_values.append(np.array(net_flux_vals))
            all_efficiency_values.append(np.array(totowork_eff_vals))
            all_pressure_bar_values.append(np.array(pressure_bars))
        
        if all_time_values:
            max_length_index = np.argmax([len(arr) for arr in all_time_values])
            common_time = all_time_values[max_length_index]
            
            interpolated_flux_values = [
                np.interp(common_time, time, flux, left=np.nan, right=np.nan) 
                for time, flux in zip(all_time_values, all_net_flux_values)
            ]
            interpolated_eff_values = [
                np.interp(common_time, time, eff, left=np.nan, right=np.nan) 
                for time, eff in zip(all_time_values, all_efficiency_values)
            ]
            interpolated_pressure_values = [
                np.interp(common_time, time, press, left=np.nan, right=np.nan) 
                for time, press in zip(all_time_values, all_pressure_bar_values)
            ]

            avg_net_flux = np.nanmean(interpolated_flux_values, axis=0)
            avg_efficiency = np.nanmean(interpolated_eff_values, axis=0)
            avg_pressure = np.nanmean(interpolated_pressure_values, axis=0)
            
            ax1.plot(common_time, avg_net_flux, color=base_color, label=f'U={x_value}V')
            ax2.plot(common_time, avg_pressure, color=base_color, linestyle="dashed", alpha=0.7)

            if avg_efficiency.size > 0:
                max_index = np.nanargmax(avg_efficiency)  # Opraveno: hledáme správné maximum účinnosti
                max_time = common_time[max_index]
                max_net_flux = avg_net_flux[max_index]
                max_point = ax1.scatter(max_time, max_net_flux, color=base_color, s=100, marker='x', label="_nolegend_")
                max_points.append(max_point)
            if max_points:
                max_x_value = max(pt.get_offsets()[0, 0] for pt in max_points)
                ax1.set_xlim(left=0, right=max_x_value * 1.2)
                ax2.set_xlim(left=0, right=max_x_value * 1.2)

            for file_path in group["files"]:
                file_name = os.path.basename(file_path)
                base_name = file_name.split('_')[2]

   
    ax1.set_ylabel('Compression rate [mg/d·cm²]', color='tab:blue')
    ax2.set_ylabel('Pressure [bar]', color='tab:red')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    ax1.set_title(f'Average compression rate and pressure vs. time for membrane: {base_name}')
    ax1.legend()

    plt.show()