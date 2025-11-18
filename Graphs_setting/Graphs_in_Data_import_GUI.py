import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
def graphs_plot (selected_graphs, pot,P_peak,P_interval1, P_interval2, P_end, time1, time2, pressure1, current_density1, forward_flux, back_diffusion, net, energy_per_mass_2, integration_forward_flux, integration_back_diff, integration_net, voltage_eff, flux_eff, work_eff):
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

    from matplotlib.ticker import FuncFormatter

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

    
    for graph_name in selected_graphs:
    # ------------------- Proudová hustota a tlak vs čas ------------------------
        if str(graph_name) == "1":
            fig1, ax1 = plt.subplots(figsize=(7.1, 4.3))

            pressure_in_bar = np.array(y1) * 0.01
            ax1.plot(time1/3600, pressure_in_bar, 'b-', label='Relative pressure at the cathode [bar]')
            ax1.set_xlabel('Time [hours]')
            ax1.set_ylabel('Relative pressure [bar]', color='b')
            ax1.tick_params(axis='y', labelcolor='b')

            ax2 = ax1.twinx()
            ax2.plot(np.array(time2)/3600, np.array(y2)/1e4, 'r-', label='Current density [A/cm²]')
            ax2.set_ylabel('Current density [A/cm²]', color='r')
            ax2.tick_params(axis='y', labelcolor='r')

            ax1.grid(True, linestyle='--', linewidth=0.5)
            ax1.set_title('Current density vs Relative pressure of the cathode – %.2f V' % voltage)
            plt.tight_layout()

    # ------------------- Proudová hustota vs tlak ------------------------
        elif str(graph_name) == "2":
            fig5, ax5 = plt.subplots(figsize=(7.1, 4.3))

            ax5.plot(np.array(pressure1)/100, np.array(y2)/1e4, 'b-', label='Relative pressure [Bar]')
            ax5.set_xlabel('Relative pressure [kPa]')
            ax5.set_ylabel('Current density [A/cm²]')
            ax5.tick_params(axis='y')

            ax5.legend(loc='upper right')
            ax5.grid(True, linestyle='--', linewidth=0.5)
            ax5.set_title('Current density vs Relative pressure – %.2f V' % voltage)
            plt.tight_layout()

    # --------------------- Difuze toku a přenesené moly ------------------------
        elif str(graph_name) == "3":
            fig, (ax3, ax5) = plt.subplots(1, 2, figsize=(10.2, 4.3))  # 2 grafy vedle sebe

            ax3.plot(time1/3600, y3, 'b-', label='Forward [mol/s]')
            ax3.plot(time1/3600, y4, 'r-', label='Back [mol/s]')
            ax3.plot(time1/3600, y5, 'g-', label='Total [mol/s]')
            ax3.set_xlabel('Time [hours]')
            ax3.set_ylabel('Flux [mol/s]')
            ax3.tick_params(axis='y')
            ax3.grid(True, linestyle='--', linewidth=0.5)
            ax3.legend(loc='center right')
            ax3.set_title('Flux – %.2f V' % voltage)

            ax5.plot(time1/3600, integration_forward_flux, 'b-', label='Forward')
            ax5.plot(time1/3600, integration_back_diff, 'r-', label='Back')
            ax5.plot(time1/3600, integration_net, 'g-', label='Total')
            ax5.set_xlabel('Time [hours]')
            ax5.set_ylabel('Transported hydrogen [mol]')
            ax5.tick_params(axis='y')
            ax5.grid(True, linestyle='--', linewidth=0.5)
            ax5.legend(loc='center right')
            ax5.set_title('Transported molekules – %.2f V' % voltage)

            plt.tight_layout()

    # -------------------- Spotřeba energie vs tlak -------------------
        elif str(graph_name) == "4":
            fig6, ax6 = plt.subplots(figsize=(7.1, 4.3))

            ax6.plot(np.array(pressure1)/100, np.array(y6), 'b-', label='Energy consumption [kWh/kg]')
            ax6.set_xlabel('Pressure [bar]')
            ax6.set_ylabel('Energy consumption [kWh/kg]', color= 'b' )
            ax6.tick_params(axis='y', labelcolor='b')

            ax7 = ax6.twinx()
            ax7.plot(np.array(pressure1)/100, work_eff*100, 'r-', label='Work efficiency')
            ax7.set_ylabel('Efficiency [%]', color='r')
            ax7.tick_params(axis='y', labelcolor='r')

            # ax6.legend(loc='upper left')
            ax6.grid(True, linestyle='--', linewidth=0.5)
            ax6.set_title('Energy consumption and efficiency vs Pressure')
            plt.tight_layout()

    # ------- Účinnosti vs čas při jednom napětí ----------------
        elif str(graph_name) == "5":
            fig3, ax4 = plt.subplots(figsize=(7.1, 4.3))

            ax4.plot(time1/3600, voltage_eff*100, 'b-', label='Voltage efficiency')
            ax4.plot(time1[1:]/3600, flux_eff[1:]*100, 'r-', label='Flux efficiency')
            ax4.plot(time1/3600, work_eff*100, 'g-', label='Work efficiency')

            ax4.set_xlabel('Time [hours]')
            ax4.set_ylabel('Efficiency [%]')
            ax4.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.0f} %'))

            ax4.grid(True)
            ax4.legend(loc='center right')
            ax4.set_title('Efficiency – %.2f V' % voltage)
            plt.tight_layout()

    #------------------------- Net flux vs efficiency -----------------------
        elif str(graph_name) == "6":
            fig7, (ax8, ax9) = plt.subplots(1, 2, figsize=(10.2, 4.3))
            
            ax8.plot(y5, work_eff*100, 'r-', label='Work efficiency')

            ax8.set_xlabel('Net flux [mol/s]')
            ax8.set_ylabel('Efficiency [%]')
            ax8.tick_params(axis='y')

            #ax8.legend(loc='upper right')
            ax8.grid(True, linestyle='--', linewidth=0.5)
            ax8.set_title('Work efficiency vs Net flux – %.2f V' % voltage)

            ax9.plot(np.array(pressure1)/100, y5, 'b-', label='Net flux')
            ax9.set_xlabel('Pressure [bar]')
            ax9.set_ylabel('Net flux [mol/s]', color= 'b' )
            ax9.tick_params(axis='y', labelcolor='b')

            ax10 = ax9.twinx()
            ax10.plot(np.array(pressure1)/100, work_eff*100, 'r-', label='Work efficiency')
            ax10.set_ylabel('Work efficeincy [%]', color= 'r' )
            ax10.tick_params(axis='y', labelcolor='r')
            ax9.grid(True, linestyle='--', linewidth=0.5)
            ax9.set_title('Pressure vs Net flux, efficiency – %.2f V' % voltage)

            plt.tight_layout()

    

    plt.show()
    return ()