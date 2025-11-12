import os
import re
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.ticker import FuncFormatter
import colorsys
import matplotlib.colors as mcolors
from scipy.optimize import curve_fit
    
from matplotlib import rc, rcParams


def process_filtered_files(file_list, base_folder, output_text):
    """
    Zpracuje vyfiltrované soubory a uloží je do struktury seznamu slovníků pro další zpracování.
    
    :param file_list: Seznam relativních cest k souborům
    :param base_folder: Základní složka, odkud se soubory hledaly
    :param output_text: Tkinter textové pole pro výstup
    :return: Seznam slovníků s informacemi o souborech
    """
    output_text.configure(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)

    groups = defaultdict(list)
    pattern = re.compile(r"_(\d+\.\d+)_\d+\.txt")

    # Rozdělení souborů do skupin
    for relative_path in file_list:
        match = pattern.search(relative_path)
        if match:
            x_value = match.group(1)
            groups[x_value].append(relative_path)

    # Výstup do textového pole a zároveň ukládání do seznamu
    output_data = []

    if not groups:
        output_text.insert(tk.END, "No matching files were found.\n")
        output_data.append({"x_value": "N/A", "files": []})
    else:
        for x_value, files in groups.items():
            group_info = {"x_value": x_value, "files": []}
            output_text.insert(tk.END, f"U = {x_value} V: {len(files)} files\n")
            for file in files:
                file_path = os.path.join(base_folder, file)
                output_text.insert(tk.END, f"  - {file_path}\n")
                group_info["files"].append(file_path)
            output_data.append(group_info)

    output_text.insert(tk.END, "\nThe filter has been successfully implemented.\n")
    output_text.configure(state=tk.DISABLED)
    return output_data

def percentage(x, pos):
    """Formátování osy jako procenta."""
    return f"{x * 100:.1f}%"

import os
import matplotlib.pyplot as plt

def plot_graphs_for_group(selected_graphs, group):
    """
    Vykreslí porovnávací grafy pro zadanou skupinu souborů.
    """
    x_value = group["x_value"]
    files = group["files"]

    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['figure.autolayout'] = True

    # Předpřipravíme grafy podle výběru
    figs_axes = {}

    if 1 in selected_graphs:
        fig1, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        figs_axes[1] = (fig1, ax1, ax2)

    if 4 in selected_graphs:
        fig4, ax4 = plt.subplots()
        figs_axes[4] = (fig4, ax4)

    if 5 in selected_graphs:
        fig5, ax5 = plt.subplots()
        figs_axes[5] = (fig5, ax5)

    colors = ['b', 'r', 'g', 'm', 'c']
    color_index = 0

    for file in files:
        time1, pressure1_bar, current_density1, EC, work_eff = [], [], [], [], []

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
                except ValueError:
                    continue
        except Exception as e:
            print(f"Chyba při načítání {file}: {e}")
            continue

        color = colors[color_index % len(colors)]
        color_index += 1

        filename = os.path.basename(file)
        result = "_".join(os.path.splitext(filename)[0].split('_')[2:])

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

    # Nastavení popisků, legend atd. - pouze jednou po přidání všech křivek
    if 1 in selected_graphs:
        ax1.set_xlabel('Time [hours]')
        ax1.set_ylabel('Pressure [Bar]', color='b')
        ax2.set_ylabel('Current Density [A/cm²]', color='g')
        ax1.tick_params(axis='y', labelcolor='b')
        ax2.tick_params(axis='y', labelcolor='g')
        ax1.grid(True, linestyle='--', alpha=0.6)
        ax1.legend(loc='upper left', fontsize=9)
        ax2.legend(loc='upper right', fontsize=9)
        ax1.set_title(f'Pressure & Current Density vs Time @ U = {x_value} V')

    if 4 in selected_graphs:
        ax4.set_xlabel('Pressure [Bar]')
        ax4.set_ylabel('Energy consumption [kWh/kg]')
        ax4.legend()
        ax4.grid(True, linestyle='--', alpha=0.6)
        ax4.set_title(f'Energy Consumption vs Pressure @ U = {x_value} V')

    if 5 in selected_graphs:
        ax5.set_xlabel('Time [h]')
        ax5.set_ylabel('Efficiency [%]')
        ax5.legend()
        ax5.grid(True, linestyle='--', alpha=0.6)
        ax5.set_title(f'Efficiency vs Time @ U = {x_value} V')

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



def start_LaTeX(output_data):

    for group in output_data:
        for file_path in group["files"]:
            # Extrahujeme název souboru
            file_name = os.path.basename(file_path)
            parent_folder = os.path.dirname(os.path.dirname(file_path))
            # Získáme první část názvu souboru před prvním podtržítkem
            base_name = file_name.split('_')[2]

    LATEX_FILE = os.path.join(parent_folder, f"LaTeX_output_{base_name}.txt")  # Uložíme výstup jako TXT soubor
    """Inicializuje LaTeX soubor, pokud ještě neexistuje."""
    with open(LATEX_FILE, "w") as latex_file:
        latex_file.write("\\documentclass{article}\n")
        latex_file.write("\\usepackage{amsmath}\n")
        latex_file.write("\\usepackage{graphicx}\n")
        latex_file.write("\\usepackage[utf8]{inputenc}\n")
        latex_file.write("\\usepackage{multirow}\n")
        latex_file.write("\\usepackage{longtable}\n")  # Podpora tabulek přes více stránek
        latex_file.write("\\usepackage{booktabs}\n")   # Lepší tabulky
        latex_file.write("\\usepackage{array}\n")      # Pro lepší formátování buněk
        latex_file.write("\\begin{document}\n\n")
        latex_file.write(f"\\title{{Vyhodnocená měření pro membránu: {base_name}}}\n")
        latex_file.write("\\author{Automatizovaný export}\n")
        latex_file.write("\\date{}\n")
        latex_file.write("\\maketitle\n\n")
        latex_file.write("Tento soubor je souhrn výsledků z měření a vše co obsahuje je tvořeno programem psaném v Pythonu.\\ \n")
        latex_file.write("\\\ \n")
    print("LaTeX soubor inicializován: latex_output.txt")
    return LATEX_FILE

def end_LaTeX(LATEX_FILE):
    """Uzavře LaTeX soubor a umožní jej později přeložit do PDF."""
    with open(LATEX_FILE, "a") as latex_file:
        latex_file.write("\\end{document}\n")
    print("Dokument uzavřen. LaTeX soubor připraven pro kompilaci.")

import re

import re

def format(latex_file_path):
    """Najde a nahradí všechny výskyty 'x.yye±z' LaTeX zápisem '$x.yy \\times 10^{±z}$' a $$ za $. """
    
    with open(latex_file_path, "r") as file:
        content = file.read()
    
    # Regulární výraz hledající čísla ve formátu 'x.yy e±z' (např. '5.90e-6')
    pattern = r'(\d+\.\d+)e(-?\d+)'

    # Náhrada za správný LaTeX formát
    def replacement(match):
        base = match.group(1)  # Číslo (např. "5.90")
        exponent = str(int(match.group(2)))  # Exponent převedený na celé číslo (odstraní úvodní nuly)
        return f"${base} \\times 10^{{{exponent}}}$"  # Správný LaTeX zápis s dolary

    formatted_content = re.sub(pattern, replacement, content)

    # Na konci nahradíme $$ za $
    formatted_content = formatted_content.replace("$$", "$")

    with open(latex_file_path, "w") as file:
        file.write(formatted_content)

    # print("Všechny výskyty vědecké notace byly nahrazeny správným LaTeX zápisem a $$ byly opraveny na $.")
    
def export_LaTeX_1(output_data, LATEX_FILE):
    """Přidá dvě tabulky rozdělené ve správném místě do existujícího LaTeX TXT souboru."""

    with open(LATEX_FILE, "a") as latex_file:
        # Sekce s tabulkami
        latex_file.write("\\section*{Tabulka 2: Základní parametry měření}\n")
        latex_file.write("\\vspace{5mm}\n")
        latex_file.write("\\setlength{\LTleft}{-0.5cm} \n")
        latex_file.write("\\begin{longtable}{|c|c|c||c|c|c||c|} \n")
        latex_file.write("\\hline \n")
        latex_file.write("Napětí & \multirow{2}{*}{Měření} & Délka měření & Max. tlak & Spotřeba & Čas tlaku & Čas eq. \\\ (V) &  & (h) & (bar) & (kWh/kg) & (h) & (h) \\\\\n")
        latex_file.write("\\hline \n")
        latex_file.write("\\endfirsthead \n")
        latex_file.write("\\hline \n")
        latex_file.write("Napětí & \multirow{2}{*}{Měření} & Délka měření & Max. tlak & Spotřeba & Čas tlaku & Čas eq. \\\ (V) &  & (h) & (bar) & (kWh/kg) & (h) & (h) \\\\\n")
        latex_file.write("\\hline \n")
        latex_file.write("\\endhead \n")

        for group in output_data:
            x_value = group["x_value"]
            files = group["files"]
            num_files = len(files)

            latex_file.write("\\hline \n")

            for idx, file in enumerate(files):
                max_pressure = -float('inf')
                max_pressure_time = None
                max_pressure_1 = -float('inf')
                max_work_eff = -float('inf')
                max_work_eff_time = None
                max_EC = -float('inf')
                last_time = 0  # Inicializace last_time
                x = 0

                try:
                    with open(file, 'r') as f:
                        lines = f.readlines()

                        for line in lines[23:]:  # Přeskočení hlavičky
                            if "--- Compression shut down ---" in line:
                                break

                            pressure_bar_1 = float(line[27:42].strip()) if line[27:42].strip() else None

                            if pressure_bar_1 and pressure_bar_1 > max_pressure_1:
                                max_pressure_1 = pressure_bar_1

                        for line in lines[23:]:  # Přeskočení hlavičky
                            if "--- Compression shut down ---" in line:
                                break

                            # Načítání hodnot
                            time_in_seconds = float(line[0:12].strip()) if line[0:12].strip() else None
                            pressure_bar = float(line[27:42].strip()) if line[27:42].strip() else None
                            EC_val = float(line[227:257].strip()) if line[227:257].strip() else None
                            work_eff_val = float(line[297:317].strip()) if line[297:317].strip() else None
                            current_density = float(line[42:67].strip()) if line[42:67].strip() else None  # Current Density

                            # Uložení posledního času
                            if time_in_seconds:
                                last_time = time_in_seconds

                            # Hledání maximálních hodnot
                            if pressure_bar and pressure_bar > max_pressure:
                                max_pressure = pressure_bar
                                max_pressure_time = time_in_seconds
                                max_EC = EC_val  # Ukládání EC při maximálním tlaku

                            if work_eff_val and work_eff_val > max_work_eff:
                                max_work_eff = work_eff_val
                                max_work_eff_time = time_in_seconds
                                eff_pressure = pressure_bar
                                eff_EC = EC_val
                                eff_current_density = current_density
                            
                            if pressure_bar and pressure_bar < (max_pressure_1 - 0.01*max_pressure_1) and x < 1 :
                                eq_time = time_in_seconds
                            else:
                                x = 2

                except Exception as e:
                    print(f"Chyba při čtení souboru {file}: {e}")

                filename = os.path.basename(file)
                filename_without_extension = os.path.splitext(filename)[0]
                result = "_".join(filename_without_extension.split('_')[4:])

                if max_pressure != -float('inf'):
                    if idx == 0:
                        latex_file.write(f"\\hline\n")
                        latex_file.write(f"\\multirow{{{num_files}}}{{*}}{{{x_value}}} & {result} & {last_time/3600:.2f} & {max_pressure:.2f} & {max_EC:.2f} & {max_pressure_time/3600:.2f} & {eq_time/3600:.2f} \\\\\n")
                    else:
                        latex_file.write(f"& {result} & {last_time/3600:.2f} & {max_pressure:.2f} & {max_EC:.2f} & {max_pressure_time/3600:.2f} & {eq_time/3600:.2f} \\\\\n")
                    if idx != num_files - 1:
                        latex_file.write("\\cline{2-7}\n")

        latex_file.write("\\hline \n")
        latex_file.write("\\end{longtable}\n")
        latex_file.write("Tato tabulka obsahuje pro každé měření hodnotu maximálního dosaženého tlaku. Pro tento tlak je zjištěna doba kdy nastal a pro daný časový okamžik je napsána i hodnota spotřeby. Dále tabulka obsahuje údaj o čase kdy měření nabylo equilibria, tato hodnota odpovídá dosažení tlaku, který je roven 99% z maximálního tlaku. \\ \n")
        latex_file.write("\\vspace{10mm}\n")

        # Druhá tabulka
        latex_file.write("\\section*{Tabulka 3: Účinnost a  zbylá data}\n")
        latex_file.write("\\vspace{5mm}\n")
        latex_file.write("\\setlength{\LTleft}{-3cm} \n")
        latex_file.write("\\begin{longtable}{|c|c|c|c||c|c|c|c|c|} \n")
        latex_file.write("\\hline \n")
        latex_file.write("Napětí & \multirow{2}{*}{Měření} & Max. účinnost & Čas účinnosti & Tlak & Rel. tlak & Spotřeba & Hmot. & Proud. hustota \\\ (V) &  & \% & (h) & (bar) & \% & (kWh/kg) & (mg/(d·$cm^2$)) & (mA/$cm^2$) \\\\\n")
        latex_file.write("\\hline \n")
        latex_file.write("\\endfirsthead \n")
        latex_file.write("\\hline \n")
        latex_file.write("Napětí & \multirow{2}{*}{Měření} & Max. účinnost & Čas účinnosti & Tlak & Rel. tlak & Spotřeba & Hmot. & Proud. hustota \\\ (V) &  & \% & (h) & (bar) & \% & (kWh/kg) & (mg/(d·$cm^2$)) & (mA/$cm^2$) \\\\\n")
        latex_file.write("\\hline \n")
        latex_file.write("\\endhead \n")

        for group in output_data:
            x_value = group["x_value"]
            files = group["files"]
            num_files = len(files)

            latex_file.write("\\hline \n")

            for idx, file in enumerate(files):
                max_pressure = -float('inf')
                max_pressure_time = None
                max_work_eff = -float('inf')
                max_work_eff_time = None
                max_EC = -float('inf')
                last_time = 0  # Inicializace last_time

                try:
                    with open(file, 'r') as f:
                        lines = f.readlines()
                        for line in lines[23:]:  # Přeskočení hlavičky
                            if "--- Compression shut down ---" in line:
                                break

                            # Načítání hodnot
                            time_in_seconds = float(line[0:12].strip()) if line[0:12].strip() else None
                            pressure_bar = float(line[27:42].strip()) if line[27:42].strip() else None
                            EC_val = float(line[227:257].strip()) if line[227:257].strip() else None
                            work_eff_val = float(line[297:317].strip()) if line[297:317].strip() else None
                            current_density = float(line[42:67].strip()) if line[42:67].strip() else None  # Current Density
                            net_flux_val = float(line[117:137].strip()) if line[117:137].strip() else None  # Net Flux

                            # Uložení posledního času
                            if time_in_seconds:
                                last_time = time_in_seconds

                            # Hledání maximálních hodnot
                            if pressure_bar and pressure_bar > max_pressure:
                                max_pressure = pressure_bar
                                max_pressure_time = time_in_seconds
                                max_EC = EC_val  # Ukládání EC při maximálním tlaku

                            if work_eff_val and work_eff_val > max_work_eff:
                                max_work_eff = work_eff_val
                                max_work_eff_time = time_in_seconds
                                eff_pressure = pressure_bar
                                eff_EC = EC_val
                                eff_current_density = current_density
                                eff_net_flux = net_flux_val
                                eff_net_g = eff_net_flux*2.016*3600*1000*(24/5) #mg/(day·cm^2)

                except Exception as e:
                    print(f"Chyba při čtení souboru {file}: {e}")

                filename = os.path.basename(file)
                filename_without_extension = os.path.splitext(filename)[0]
                result = "_".join(filename_without_extension.split('_')[4:])

                if max_work_eff != -float('inf'):
                    if idx == 0:
                        latex_file.write(f"\\hline\n")
                        latex_file.write(f"\\multirow{{{num_files}}}{{*}}{{{x_value}}} & {result} & {max_work_eff*100:.1f} & {max_work_eff_time/3600:.2f} & {eff_pressure:.2f} & {(eff_pressure)/(max_pressure)*100:.0f} & {eff_EC:.2f} & {eff_net_g:.2f} & {eff_current_density/10:.2f} \\\\\n")
                    else:
                        latex_file.write(f"& {result} & {max_work_eff*100:.1f} & {max_work_eff_time/3600:.2f} & {eff_pressure:.2f} & {(eff_pressure)/(max_pressure)*100:.0f} & {eff_EC:.2f} & {eff_net_g:.2f} & {eff_current_density/10:.2f} \\\\\n")
                    if idx != num_files - 1:
                        latex_file.write("\\cline{2-9}\n")

        latex_file.write("\\hline \n")
        latex_file.write("\\end{longtable}\n")
        latex_file.write("Tato tabulka je postavena na hodnotě maximální celkové účinnosti pro každé měření. Této účinsoti byl zjištěn čas, kdy nastala. Pro tento čas jsou dále vypsané tyto data: tlak a jeho procentuální zastoupení v maximálním tlaku daného měření (Rel. tlak), spotřebu a proudovou hustotu. \\ \n")
        latex_file.write("\\newpage \n")

    print(f"Tabulky přidány do LaTeX TXT souboru.")

def export_LaTeX_2(output_data, LATEX_FILE):
    """Přidá tabulku pro Vc a všechny hodnoty DH a Pressure do existujícího LaTeX TXT souboru."""
    with open(LATEX_FILE, "a") as latex_file:

        # Začátek tabulky
        latex_file.write("\\section*{Tabulka 4: Hodnoty objemů a difuzivity}\n")
        latex_file.write("\\vspace{5mm}\n")
        latex_file.write("\\setlength{\LTleft}{-3cm} \n")
        latex_file.write("\\begin{longtable}{|c|c|c|c|c|c|c|c|c|} \n")
        latex_file.write("\\hline \n")
        latex_file.write("Napětí & \multirow{2}{*}{Měření} & $V_c com$ & $V_c dif$ & $DH_m$ & $$DH_{dep}$$ & \multirow{2}{*}{Bod} & $DH$ & Tlak \\\\ \n")
        latex_file.write("(V) &  & (cm$^{3}$) & (cm$^{3}$) & (mol/Pa/m/s) & (mol/Pa/m/s) &  & (mol/Pa/m/s) & (Bar) \\\\ \n")
        latex_file.write("\\hline \n")
        latex_file.write("\\endfirsthead \n")  # Konec první hlavičky
        latex_file.write("\\hline \n")
        latex_file.write("Napětí & \multirow{2}{*}{Měření} & $V_c com$ & $V_c dif$ & $DH_m$ & $$DH_{dep}$$ & \multirow{2}{*}{Bod} & $DH$ & Tlak \\\\ \n")
        latex_file.write("(V) &  & (cm$^{3}$) & (cm$^{3}$) & (mol/Pa/m/s) & (mol/Pa/m/s) &  & (mol/Pa/m/s) & (Bar) \\\\ \n")
        latex_file.write("\\hline \n")
        latex_file.write("\\endhead \n")  # Konec hlavičky pro ostatní řádky
        
        for group in output_data:
            x_value = group["x_value"]
            files = group["files"]

            # Přidáme čáru nad hodnotu napětí
            latex_file.write("\\hline \n")

            num_folders = len(files)
            latex_file.write("\\hline\n")
            latex_file.write(f"\\multirow{{{num_folders}}}{{*}}{{{x_value}}}\n")

            for file in files:
                try:
                    with open(file, 'r') as f:
                        lines = f.readlines()

                        # Inicializace hodnot
                        Vc_value = "N/A"
                        volume_fit = "N/A"
                        DH_pressure_data = []

                        # Extrahování Vc
                        for i, line in enumerate(lines):
                            if 'Vc (cm3)' in line:
                                try:
                                    next_line = lines[i + 1].strip()  
                                    line_data = next_line.split()  
                                    Vc_value = float(line_data[3])  
                                except (ValueError, IndexError):
                                    Vc_value = "N/A"
                                
                        for line in lines:
                            if "Volume from exponential fit" in line:
                                try:
                                    volume_fit = float(line.split(":")[1].strip().split()[0])
                                except (ValueError, IndexError):
                                    volume_fit = "N/A"

                        for line in lines:
                            if "DH value from depression (mol/Pa/m/s)" in line:
                                try:
                                    DH_from_depression = float(line.split(":")[1].strip().split()[0])
                                except (ValueError, IndexError):
                                    DH_from_depression = "N/A"

                        # Extrahování DH a Pressure
                        DH_start = False
                        for line in lines:
                            parts = line.split()
                            if "Point" in line and "DH" in line and "Pressure" in line:
                                DH_start = True
                                continue
                            if DH_start and len(parts) == 3:
                                DH_pressure_data.append(parts)  # [Bod, DH, Pressure]

                        dh_mean_line = lines[18].strip()  # Odebíráme přebytečné mezery

                        # Regex pro extrakci hodnoty DH_mean a její chyby
                        dh_mean_pattern = r"DH mean:\s*([0-9e\.\+-]+)\s*\+\-\s*([0-9e\.\+-]+)"

                        # Hledání shody v konkrétním řádku
                        match = re.search(dh_mean_pattern, dh_mean_line)

                        if match:
                            # Extrahování hodnoty a chyby
                            DH_mean_value = float(match.group(1))
                            #print(f"DH_mean: {DH_mean_value}")
                        else:
                            print("Žádná shoda v řádku:", dh_mean_line)


                        # Název souboru bez cesty a přípony
                        filename = os.path.basename(file)
                        filename_without_extension = os.path.splitext(filename)[0]
                        result = "_".join(filename_without_extension.split('_')[4:])

                        # Počet řádků pro multirow
                        num_rows = len(DH_pressure_data)

                        # Pokud existují hodnoty DH a Pressure
                        if num_rows > 0:
                            
                            latex_file.write(f"\\ & \\multirow{{{num_rows}}}{{*}}{{{result}}} & \\multirow{{{num_rows}}}{{*}}{{{Vc_value}}} & \\multirow{{{num_rows}}}{{*}}{{{volume_fit}}} & \\multirow{{{num_rows}}}{{*}}{{{DH_mean_value:.2e}}} & \\multirow{{{num_rows}}}{{*}}{{{DH_from_depression:.2e}}} \n")

                            for i, (point, dh_value, pressure) in enumerate(DH_pressure_data):
                                if "_" in point:
                                    point = point.replace("_", " ")

                                if i == 0:  # První řádek s daty
                                    latex_file.write(f"& {point} & ${dh_value}$ & {pressure} \\\\\n")
                                    latex_file.write("\\cline{7-9} \n")
                                else:  # Další řádky bez opakování nadpisů
                                    latex_file.write(f"& & & & & & {point} & ${dh_value}$ & {pressure} \\\\\n")
                                    latex_file.write("\\cline{7-9} \n")
                            latex_file.write("\\cline{2-9}\n")
                        else:
                            latex_file.write(f"{x_value} & {result} & ${Vc_value}$ & N/A & N/A & N/A \\\\ \n")

                except Exception as e:
                    print(f"Chyba při čtení souboru {file}: {e}")

        # Ukončení tabulky
        latex_file.write("\\hline \n\\end{longtable}\n")
        latex_file.write("Tato tabulka obsahuje hodnoty spočítaného objemu ztlakovaného vodíku. Dále obsahuje hodnoty difuzivity, které jsou získané vždy pro maximální dosažený tlak a pak pro tři další body od tohoto bodu až do konce měření, pro srovnání je uveden i tlak v tomto bodě.\\ \n")

def export_LaTeX_3(output_data, LATEX_FILE):
    """Přidá tabulku s průměrnými hodnotami pro dané napětí do existujícího LaTeX TXT souboru."""

    with open(LATEX_FILE, "a") as latex_file:
        # Začátek tabulky
        latex_file.write("\\section*{Tabulka 1: Průměrné hodnoty pro dané napětí}\n")
        latex_file.write("\\vspace{5mm}\n")
        latex_file.write("\\setlength{\LTleft}{-4.5cm} \n")
        latex_file.write("\\begin{longtable}{|c|c|c|c|c|c|c|c|c|c|} \n")
        latex_file.write("\\hline \n")
        latex_file.write("Napětí & Max. tlak & Spotřeba & Čas eq. & Max. účinnost & Čas účinosti & $V_c com$ & $V_c dif$ & DH & $DH_{dep}$\\\ (V) & (bar) & (kWh/kg) & (h) & (\%) & (h) & (cm$^{3}$) & (cm$^{3}$) & (mol/Pa/m/s) & (mol/Pa/m/s)\\\ \n")
        latex_file.write("\\hline \n")
        latex_file.write("\\endfirsthead \n")
        latex_file.write("\\hline \n")
        latex_file.write("Napětí & Max. tlak & Spotřeba & Čas eq. & Max. účinnost & Čas účinosti & $V_c com$ & $V_c dif$ & DH & $DH_{dep}$\\\ (V) & (bar) & (kWh/kg) & (h) & (\%) & (h) & (cm$^{3}$) & (cm$^{3}$) & (mol/Pa/m/s) & (mol/Pa/m/s)\\\ \n")
        latex_file.write("\\hline \n")
        latex_file.write("\\endhead \n")

        for group in output_data:
            x_value = group["x_value"]
            files = group["files"]

            # Sčítání hodnot pro výpočet průměrů
            total_pressure = 0
            total_EC = 0
            total_work_eff = 0
            total_eq_time = 0
            total_work_eff_time = 0
            total_vc_value = 0
            total_vc_fit = 0
            total_DH = 0
            total_DH_depression = 0
            count = 0
            x = 0

            for file in files:
                max_pressure = -float('inf')
                max_pressure_1 = -float('inf')
                max_work_eff = -float('inf')
                max_work_eff_time = None
                max_EC = -float('inf')

                try:
                    with open(file, 'r') as f:
                        lines = f.readlines()

                        for line in lines[23:]:  # Přeskočení hlavičky
                            if "--- Compression shut down ---" in line:
                                break

                            pressure_bar_1 = float(line[27:42].strip()) if line[27:42].strip() else None

                            if pressure_bar_1 and pressure_bar_1 > max_pressure_1:
                                max_pressure_1 = pressure_bar_1


                        for line in lines[23:]:  # Přeskočení hlavičky
                            if "--- Compression shut down ---" in line:
                                break

                            # Načítání hodnot
                            time_in_seconds = float(line[0:12].strip()) if line[0:12].strip() else None
                            pressure_bar = float(line[27:42].strip()) if line[27:42].strip() else None
                            EC_val = float(line[227:257].strip()) if line[227:257].strip() else None
                            work_eff_val = float(line[297:317].strip()) if line[297:317].strip() else None


                            # Hledání maximálních hodnot
                            if pressure_bar and pressure_bar > max_pressure:
                                max_pressure = pressure_bar
                                max_EC = EC_val  # Ukládání EC při maximálním tlaku

                            if work_eff_val and work_eff_val > max_work_eff:
                                max_work_eff = work_eff_val
                                max_work_eff_time = time_in_seconds

                            if pressure_bar and pressure_bar < (max_pressure_1 - 0.01*max_pressure_1) and x < 1 :
                                eq_time = time_in_seconds
                            else:
                                x = 2

                        # Extrahování Vc
                        for i, line in enumerate(lines):
                            if 'Vc (cm3)' in line:
                                try:
                                    next_line = lines[i + 1].strip()  
                                    line_data = next_line.split()  
                                    Vc_value = float(line_data[3])  
                                except (ValueError, IndexError):
                                    Vc_value = "N/A"
                                    
                        # Extrahování Volume fit
                        for line in lines:
                            if "Volume from exponential fit" in line:
                                try:
                                    volume_fit = float(line.split(":")[1].strip().split()[0])
                                except (ValueError, IndexError):
                                    volume_fit = "N/A"
                        
                        for line in lines:
                            if "DH value from depression (mol/Pa/m/s)" in line:
                                try:
                                    DH_from_depression = float(line.split(":")[1].strip().split()[0])
                                except (ValueError, IndexError):
                                    DH_from_depression = "N/A"

                        dh_mean_line = lines[18].strip()  # Odebíráme přebytečné mezery

                        # Regex pro extrakci hodnoty DH_mean a její chyby
                        dh_mean_pattern = r"DH mean:\s*([0-9e\.\+-]+)\s*\+\-\s*([0-9e\.\+-]+)"

                        # Hledání shody v konkrétním řádku
                        match = re.search(dh_mean_pattern, dh_mean_line)

                        if match:
                            # Extrahování hodnoty a chyby
                            DH_mean_value = float(match.group(1))
                            #print(f"DH_mean: {DH_mean_value}")
                        else:
                            print("Žádná shoda v řádku:", dh_mean_line)


                except Exception as e:
                    print(f"Chyba při čtení souboru {file}: {e}")

                if max_pressure != -float('inf'):
                    total_pressure += max_pressure
                    total_EC += max_EC
                    total_work_eff += max_work_eff * 100  # Účinnost v %
                    total_eq_time += eq_time / 3600  # Čas pro max. tlak v hodinách
                    total_work_eff_time += max_work_eff_time / 3600  # Čas pro max. účinnost v hodinách
                    total_vc_value += Vc_value
                    total_vc_fit += volume_fit
                    total_DH += DH_mean_value
                    total_DH_depression += DH_from_depression
                    count += 1

                    
            if count > 0:  # Pokud máme nějaké hodnoty pro dané napětí
                # Výpočet průměrů
                avg_pressure = total_pressure / count
                avg_EC = total_EC / count
                avg_work_eff = total_work_eff / count
                avg_pressure_time = total_eq_time / count
                avg_work_eff_time = total_work_eff_time / count
                avg_vc_value = total_vc_value / count
                avg_vc_fit = total_vc_fit / count
                avg_DH = total_DH / count
                avg_DH_depression = total_DH_depression / count

                # Přidání průměrných hodnot do tabulky
                latex_file.write(f"\\hline\n")
                latex_file.write(f"{x_value} & {avg_pressure:.2f} & {avg_EC:.2f} & {avg_pressure_time:.2f} & {avg_work_eff:.1f} & {avg_work_eff_time:.2f} & {avg_vc_value:.2f} & {avg_vc_fit:.2f} & {avg_DH:.2e} & {avg_DH_depression:.2e} \\\\ \n")

        latex_file.write("\\hline \n")
        latex_file.write("\\end{longtable}\n")
        latex_file.write("Tato tabulka obsahuje průměrné hodnoty pro dané napětí získané ze všech měření pro dané napětí. Zahrnuje maximální tlak, spotřebu, čas dosáhnutí equilibria (tlaku odpovídající 99% maximálního tlaku), účinnost a čas jejího dosáhnutí.\\ \n")

def main(selected_graphs, output_data):
    """
    Hlavní funkce, která spojuje načtení souborů a vykreslování grafů.
    """
    
    for group in output_data:
        plot_graphs_for_group(selected_graphs, group)

if __name__ == "__main__":
    main()
