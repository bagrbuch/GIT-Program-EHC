import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import os
from matplotlib.ticker import FuncFormatter

def graphs_plot (export_directory, selected_graphs, pot,P_peak,P_interval1, P_interval2, P_end, time1, time2, pressure1, current_density1, forward_flux, back_diffusion, net, energy_per_mass_2, integration_forward_flux, integration_back_diff, integration_net, voltage_eff, flux_eff, work_eff):
# Assignation of the data
    plt.close('all')
    x1 = time1
    x2 = time2
    y1 = pressure1
    y2 = current_density1
    y3 = forward_flux
    y4 = back_diffusion
    y5 = net
    y6 = energy_per_mass_2

    voltage = np.mean(pot)

    P_peak = P_peak +101325
    P_interval1 = P_interval1 + 101325
    P_interval2 = P_interval2 + 101325
    P_end = P_end +101325


    plt.rcParams.update({
        'font.size': 12,
        'font.family': 'sans-serif',
        'axes.titlesize': 12,
        'axes.labelsize': 12,
        'legend.fontsize': 11,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'lines.linewidth': 2,
        'figure.dpi': 300,
        'figure.autolayout': True
    })

    colors = plt.cm.tab10.colors
    color_index = 0
    color = colors[color_index % len(colors)]

    # ------------------- Current density and pressure vs. time ------------------------
    def plot_graph_1(voltage, time1, time2,  y1, y2, color, color_index):
        fig1, ax1 = plt.subplots(figsize=(7.1, 4.3))

        pressure_in_bar = np.array(y1) * 0.01
        ax1.plot(time1/3600, pressure_in_bar, color=color, label='Relative pressure at the cathode [bar]')
        ax1.set_ylabel('Relative pressure [bar]', color=color)
        ax1.tick_params(axis='y', labelcolor=color)

        color_index = color_index+1
        color = colors[color_index % len(colors)]

        ax2 = ax1.twinx()
        ax2.plot(np.array(time2)/3600, np.array(y2)/1e4, color=color, label='Current density [A/cm²]')
        ax2.set_ylabel('Current density [A/cm²]', color=color)

        ax1.set_xlabel('Time [hours]')
        ax2.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, linestyle='--', linewidth=0.5)
        ax1.set_title('Current density vs Relative pressure of the cathode – %.2f V' % voltage)

        color_index = 0
        color = colors[color_index % len(colors)]

        return fig1

# ------------------- Current density vs. pressure ------------------------
    def plot_graph_2(voltage, pressure1, y2, color):
        fig5, ax5 = plt.subplots(figsize=(7.1, 4.3))

        ax5.plot(np.array(pressure1)/100, np.array(y2)/1e4, color=color, label='Relative pressure [Bar]')

        ax5.set_xlabel('Relative pressure [Bar]')
        ax5.set_ylabel('Current density [A/cm²]')
        ax5.tick_params(axis='y')
        ax5.legend(loc='upper right')
        ax5.grid(True, linestyle='--', linewidth=0.5)
        ax5.set_title('Current density vs Relative pressure – %.2f V' % voltage)

        return fig5

# --------------------- Diffusion of flow and transferred moles ------------------------
    def plot_graph_3_1(voltage, time1, y3, color, integration_forward_flux, integration_back_diff, y5, integration_net, color_index):
        fig, ax3 = plt.subplots(figsize=(7.1, 4.3))

        ax3.plot(time1/3600, y3, color=color, label='Forward [mol/s]')

        color_index = color_index+1
        color = colors[color_index % len(colors)]

        ax3.plot(time1/3600, y4, color=color, label='Back [mol/s]')

        color_index = color_index+1
        color = colors[color_index % len(colors)]

        ax3.plot(time1/3600, y5, color=color, label='Total [mol/s]')

        ax3.set_xlabel('Time [hours]')
        ax3.set_ylabel('Flux [mol/s]')
        ax3.tick_params(axis='y')
        ax3.grid(True, linestyle='--', linewidth=0.5)
        ax3.legend(loc='center right')
        ax3.set_title('Flux – %.2f V' % voltage)

        color_index = 0
        color = colors[color_index % len(colors)]

        return fig
    
    def plot_graph_3_2(voltage, time1, y3, color, integration_forward_flux, integration_back_diff, y5, integration_net, color_index):
        fig, ax5 = plt.subplots(figsize=(7.1, 4.3))

        ax5.plot(time1/3600, integration_forward_flux, color=color, label='Forward')

        color_index = color_index+1
        color = colors[color_index % len(colors)]

        ax5.plot(time1/3600, integration_back_diff, color=color, label='Back')

        color_index = color_index+1
        color = colors[color_index % len(colors)]

        ax5.plot(time1/3600, integration_net, 'g-', label='Total')
        
        ax5.set_xlabel('Time [hours]')
        ax5.set_ylabel('Transported hydrogen [mol]')
        ax5.tick_params(axis='y')
        ax5.grid(True, linestyle='--', linewidth=0.5)
        ax5.legend(loc='center right')
        ax5.set_title('Transported molekules – %.2f V' % voltage)


        color_index = 0
        color = colors[color_index % len(colors)]

        return fig

# -------------------- Energy consumption vs. pressure -------------------
    def plot_graph_4(voltage, pressure1, y6, color, work_eff, color_index):
        fig6, ax6 = plt.subplots(figsize=(7.1, 4.3))

        ax6.plot(np.array(pressure1)/100, np.array(y6), color=color, label='Energy consumption [kWh/kg]')
        ax6.set_ylabel('Energy consumption [kWh/kg]', color=color )
        ax6.tick_params(axis='y', labelcolor=color)

        color_index = color_index+1
        color = colors[color_index % len(colors)]

        ax7 = ax6.twinx()
        ax7.plot(np.array(pressure1)/100, work_eff*100, color=color, label='Work efficiency')
        ax7.set_ylabel('Efficiency [%]', color=color)

        ax6.set_xlabel('Pressure [bar]')
        # ax6.legend(loc='upper left')
        ax6.grid(True, linestyle='--', linewidth=0.5)
        ax6.set_title('Energy consumption and efficiency vs Pressure – %.2f V' % voltage)
        ax7.tick_params(axis='y', labelcolor=color)

        color_index = 0
        color = colors[color_index % len(colors)]

        return fig6

# ------- Efficiency vs. time at a single voltage ----------------
    def plot_graph_5(voltage, time1, voltage_eff, color, flux_eff, work_eff, color_index):
        fig3, ax4 = plt.subplots(figsize=(7.1, 4.3))

        ax4.plot(time1/3600, voltage_eff*100, color=color, label='Voltage efficiency')

        color_index = color_index+1
        color = colors[color_index % len(colors)]

        ax4.plot(time1[1:]/3600, flux_eff[1:]*100, color=color, label='Flux efficiency')

        color_index = color_index+1
        color = colors[color_index % len(colors)]

        ax4.plot(time1/3600, work_eff*100, color=color, label='Work efficiency')

        ax4.set_xlabel('Time [hours]')
        ax4.set_ylabel('Efficiency [%]')
        ax4.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.0f} %'))
        ax4.grid(True, linestyle='--', linewidth=0.5)
        ax4.legend(loc='center right')
        ax4.set_title('Efficiency – %.2f V' % voltage)

        color_index = 0
        color = colors[color_index % len(colors)]

        return fig3

#------------------------- Net flux vs efficiency -----------------------
    def plot_graph_6_1(voltage, y5, work_eff, color, pressure1, color_index):
        fig7, ax8 = plt.subplots(figsize=(7.1, 4.3))
        
        ax8.plot(y5, work_eff*100, color=color, label='Work efficiency')

        ax8.set_xlabel('Net flux [mol/s]')
        ax8.set_ylabel('Efficiency [%]')
        ax8.tick_params(axis='y')
        #ax8.legend(loc='upper right')
        ax8.grid(True, linestyle='--', linewidth=0.5)
        ax8.set_title('Work efficiency vs Net flux – %.2f V' % voltage)

        color_index = color_index+1
        color = colors[color_index % len(colors)]

        color_index = 0
        color = colors[color_index % len(colors)]

        return fig7
    
    def plot_graph_6_2(voltage, y5, work_eff, color, pressure1, color_index):
        fig7, ax9 = plt.subplots(figsize=(7.1, 4.3))
        
        ax9.plot(np.array(pressure1)/100, y5, color=color, label='Net flux')
        ax9.set_ylabel('Net flux [mol/s]', color=color )
        ax9.tick_params(axis='y', labelcolor=color)

        color_index = color_index+1
        color = colors[color_index % len(colors)]

        ax10 = ax9.twinx()
        ax10.plot(np.array(pressure1)/100, work_eff*100, color=color, label='Work efficiency')

        ax9.set_xlabel('Pressure [bar]')
        ax10.set_ylabel('Work efficeincy [%]', color=color )
        ax10.tick_params(axis='y', labelcolor=color)
        ax9.grid(True, linestyle='--', linewidth=0.5)
        ax9.set_title('Pressure vs Net flux, efficiency – %.2f V' % voltage)

        color_index = 0
        color = colors[color_index % len(colors)]

        return fig7
    

    for graph_name in selected_graphs:
        if str(graph_name) == "1":
            plot_graph_1(voltage, time1, time2, y1, y2, color, color_index)

        elif str(graph_name) == "2":
            plot_graph_2(voltage, pressure1, y2, color)

        elif str(graph_name) == "3":
            plot_graph_3_1(voltage, time1, y3, color, integration_forward_flux, integration_back_diff, y5, integration_net, color_index)
            plot_graph_3_2(voltage, time1, y3, color, integration_forward_flux, integration_back_diff, y5, integration_net, color_index)

        elif str(graph_name) == "4":
            plot_graph_4(voltage, pressure1, y6, color, work_eff, color_index)
        
        elif str(graph_name) == "5":
            plot_graph_5(voltage, time1, voltage_eff, color, flux_eff, work_eff, color_index)

        elif str(graph_name) == "6":
            plot_graph_6_1(voltage, y5, work_eff, color, pressure1, color_index)
            plot_graph_6_2(voltage, y5, work_eff, color, pressure1, color_index)
    
    plt.show()
        
    all_figs = [
        ("Current_vs_pressure",       plot_graph_1(voltage, time1, time2, y1, y2, color, color_index)),
        ("Current_vs_relative_press", plot_graph_2(voltage, pressure1, y2, color)),
        ("Transport_moles_vs_time",   plot_graph_3_2(voltage, time1, y3, color, integration_forward_flux, integration_back_diff, y5, integration_net, color_index)),
        ("Flux_vs_time",              plot_graph_3_1(voltage, time1, y3, color, integration_forward_flux, integration_back_diff, y5, integration_net, color_index)),
        ("Consumption_vs_pressure",   plot_graph_4(voltage, pressure1, y6, color, work_eff, color_index)),
        ("Efficiency_vs_time",        plot_graph_5(voltage, time1, voltage_eff, color, flux_eff, work_eff, color_index)),
        ("Net_vs_efficiency",         plot_graph_6_1(voltage, y5, work_eff, color, pressure1, color_index)),
        ("Net_and_eff_vs_pressure",   plot_graph_6_2(voltage, y5, work_eff, color, pressure1, color_index))
    ]

    for name, fig in all_figs:
        filepath = os.path.join(export_directory, f"{name}.pdf")
        fig.savefig(filepath, format="pdf", bbox_inches="tight")
            

    return ()