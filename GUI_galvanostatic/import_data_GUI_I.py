import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
import threading
import GUI
import Import_csv as script1
import EHC_I as script2  # Import externího skriptu pro vykreslení grafu

# Globální proměnné pro cesty k souborům
file_path = ""
ca_file_path = ""

# Funkce pro přesměrování výstupu do Text widgetu
class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        if "Chyba" in text:
            self.text_widget.insert(ctk.END, text, "error")
        elif "úspěšně" in text:
            self.text_widget.insert(ctk.END, text, "success")
        else:
            self.text_widget.insert(ctk.END, text)
        self.text_widget.yview(ctk.END)  # Scroll to the end to show new text

# Funkce pro výběr souboru
def select_file(var_name, file_type_desc, file_types):
    global file_path, ca_file_path
    selected_file = filedialog.askopenfilename(filetypes=[(file_type_desc, file_types)])
    if not selected_file:
        messagebox.showwarning("Warning", f"{file_type_desc} is not selected.")
    else:
        file_name = os.path.basename(selected_file)
        if var_name == "file_path":
            file_path = selected_file
        elif var_name == "ca_file_path":
            ca_file_path = selected_file
        print(f"File {file_type_desc} successfully selected: {file_name}")

# Funkce pro import a oříznutí souboru
def import_and_trim_file():
    def background_task():
        try:
            if not file_path or not ca_file_path:
                root.after(0, lambda: messagebox.showwarning("Warning", "Both data files must be selected."))
                return

            output_path = os.path.join(os.path.dirname(file_path), "data_trimmed.csv")
            script1.find_and_trim_csv(file_path, ca_file_path, output_path)
            root.after(0, lambda: print("\nData has been successfully imported"))
        except Exception as e:
            root.after(0, lambda: print(f"Error when importing and cropping a file: {e}"))
        finally:
            root.after(0, progress_bar.stop)  # Zastavení progress baru v hlavním vlákně

    progress_bar.start()
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()

# Funkce pro zobrazení grafu
def show_graph():
    try:
        progress_bar.start()
        
        if not thickness_var.get().strip():
            print("Membrane thickness not specified")
            return

        if not volume_var.get().strip():
            print("The compressed volume was not specified")
            return

        if not ca_file_path:
            messagebox.showwarning("Warning", "First, select the CA file and the compression file.")
            return

        compression_file_path = os.path.join(os.path.dirname(ca_file_path), "compression.csv")
        if not os.path.exists(compression_file_path):
            messagebox.showwarning("Warning", "The file 'compression.csv' was not found in the same folder as the CA file.")
            return
        
        additional_file_path = os.path.join(os.path.dirname(ca_file_path), "diffusion.csv")
        if not os.path.exists(compression_file_path):
            messagebox.showwarning("Warning", "The file 'diffusion.csv' was not found in the same folder as the CA file.")
            return

        selected_graphs = [
            int(graph) for graph, selected in {
                "1": graph1_var.get(),
                "2": graph2_var.get(),
                "3": graph3_var.get(),
                "4": graph4_var.get(),
                "5": graph5_var.get(),
            }.items() if selected
        ]

        # print(f"Vybrané grafy: {selected_graphs}")
        script2.dataplot(ca_file_path, ca_file_path, compression_file_path,additional_file_path,thickness_var, volume_var, selected_graphs=selected_graphs, export_directory=os.path.dirname(ca_file_path)) 
        print("The selected charts have been successfully displayed.")
    except Exception as e:
        print(f"Error when displaying the chart: {e}")
    finally:
        progress_bar.stop()
# Funkce pro spuštění operací na novém vlákně
def run_thread(target):
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    
# Funkce pro vymazání výstupu
def clear_output():
    output_text.delete(1.0, ctk.END)

# Funkce pro resetování aplikace a návrat do hlavní smyčky
def reset_app():
    global file_path, ca_file_path

    # Reset všech globálních proměnných
    file_path = ""
    ca_file_path = ""

    # Reset checkboxů
    graph1_var.set(False)
    graph2_var.set(False)
    graph3_var.set(False)
    graph4_var.set(False)
    graph5_var.set(False)

    # Reset progress baru
    progress_bar.stop()
    
    # Obnovení GUI na výchozí stavy
    print("The application has been reset. You can start again.")
    root.quit()  # Ukončení aktuální smyčky
    root.deiconify()  # Zobrazení hlavního okna znovu
    root.mainloop()  # Spuštění nové smyčky

# Funkce pro zobrazení popisu funkce
def show_help(frame_name):
    help_text = ""
    if frame_name == "import":
        help_text = "Functions for importing and processing data files. First you need to select the pressure data file (from the database) and the potentiostat data file. The function processes both files and modifies them for further data processing."
    elif frame_name == "graphs":
        help_text = "Data processing functions. At a minimum, it needs to select a data file from the potentiostat. The data is then used to calculate all variables. The function allows to display selected graphs. Finally, the data are exported."
    elif frame_name == "export":
        help_text = "Function for exporting data to a file. You can set the output file and export path."
    else:
        help_text = "Neznámá funkce."
    
    output_text.delete(1.0, ctk.END)  # Vymazání textového pole před zobrazením nového textu
    output_text.insert(ctk.END, help_text)

# Návrat zpět do hlavního menu
def go_back_to_main():
    root.destroy()
    GUI.main_app()

# Vytvoření hlavního okna
root = ctk.CTk()
root.title("Data import")
root.geometry("800x750")
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)

# Globální proměnné pro widgety
graph1_var = ctk.BooleanVar()
graph2_var = ctk.BooleanVar()
graph3_var = ctk.BooleanVar()
graph4_var = ctk.BooleanVar()
graph5_var = ctk.BooleanVar()

# Levý rámeček - Funkce na importování dat
frame_left = ctk.CTkFrame(root, corner_radius=10)
frame_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Popisek pro levý rámeček
label_left = ctk.CTkLabel(frame_left, text="Function for trimming data", font=("Helvetica", 12, "bold"))
label_left.grid(row=0, column=0, padx=10, pady=5)

frame_file_upload = ctk.CTkFrame(frame_left)
frame_file_upload.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

buttons = [
    ("Data from the database", lambda: select_file("file_path", "CSV Files", "*.csv")),
    ("Data from potenciostat", lambda: select_file("ca_file_path", "All Files", "*.*")),
    ("Process input files", lambda: run_thread(import_and_trim_file))
]
for idx, (text, cmd) in enumerate(buttons):
    ctk.CTkButton(frame_file_upload, text=text, command=cmd,text_color="black" if idx < 2 else "white" , fg_color="white" if idx < 2 else "#1E90FF", font=("Helvetica", 12)).grid(row=idx+1, column=0, padx=10, pady=5, ipadx=10, ipady=5, sticky="nsew")

# Tlačítko s otazníkem pro levý rámeček (menší velikost tlačítka)
help_button_left = ctk.CTkButton(frame_left, text="?", command=lambda: show_help("import"), font=("Helvetica", 12, "bold"), width=30, height=30)
help_button_left.grid(row=2, column=0, padx=10, pady=10, sticky="sw")

# Pravý rámeček - Funkce na zpracování dat
frame_right = ctk.CTkFrame(root, corner_radius=10)
frame_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Popisek pro pravý rámeček
label_right = ctk.CTkLabel(frame_right, text="Function for calculating all variables", font=("Helvetica", 12, "bold"))
label_right.grid(row=0, column=0, padx=10, pady=5)

# Přidání pole pro zadání tloušťky v mikrometrech
thickness_var = ctk.StringVar()  # Proměnná pro tloušťku
volume_var = ctk.StringVar()

thickness_label = ctk.CTkLabel(frame_right, text="Thickness [µm]:", font=("Helvetica", 12, "bold"))
thickness_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

volume_label = ctk.CTkLabel(frame_right, text="Volume [cm³]:", font=("Helvetica", 12, "bold"))
volume_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

thickness_entry = ctk.CTkEntry(frame_right, textvariable=thickness_var, font=("Helvetica", 12), width=50)
thickness_entry.grid(row=1, column=0, padx=0, pady=5)

volume_entry = ctk.CTkEntry(frame_right, textvariable=volume_var, font=("Helvetica", 12), width=50)
volume_entry.grid(row=1, column=2, padx=10, pady=5, sticky="e")

checkbuttons = [
    ("Current density and Pressure vs Time", graph1_var),
    ("Current density vs Pressure", graph2_var),
    ("Flow diffusion", graph3_var),
    ("Graph energy consumption", graph4_var),
    ("Graphs all efficiencies vs time", graph5_var)
]
for idx, (text, var) in enumerate(checkbuttons):
    ctk.CTkCheckBox(frame_right, text=text, variable=var).grid(row=idx+2, column=0, padx=10, pady=5, sticky="w")

ctk.CTkButton(frame_right, text="Process measurement data", command=show_graph, fg_color="#1E90FF", font=("Helvetica", 12)).grid(row=len(checkbuttons)+2, column=0, padx=10, pady=5, sticky="e")

def thickness():
    membranes = [
    {"Membrane": "\n\nMembrane", "Thickness (µm)": "Thickness [µm]"}, 
    {"Membrane": "\nFumapem FS-715", "Thickness (µm)": 15},
    {"Membrane": "Nafion HP", "Thickness (µm)": 20.3},
    {"Membrane": "Nafion 211", "Thickness (µm)": 25.4},
    {"Membrane": "Nafion 212", "Thickness (µm)": 50.8},
    {"Membrane": "Nafion 115", "Thickness (µm)": 127},
    {"Membrane": "Nafion 117", "Thickness (µm)": 183}
    ]

    # Tisk tabulky
    for row in membranes:
        print(f"{row['Membrane']:15} | {row['Thickness (µm)']:6}")
    print("\n\nVolume since 2024 = 8.5 cm³; Volume from 2025 = 11 cm³\n\n")

ctk.CTkButton(frame_right, text="?", command=thickness, font=("Helvetica", 12, "bold"),width=30, height=30).grid(row=1, column=0, padx=10, pady=5, sticky="e")

# Tlačítko s otazníkem pro pravý rámeček (menší velikost tlačítka)
help_button_right = ctk.CTkButton(frame_right, text="?", command=lambda: show_help("graphs"), font=("Helvetica", 12, "bold"), width=30, height=30)
help_button_right.grid(row=len(checkbuttons)+2, column=0, padx=10, pady=10, sticky="sw")

# Spodní rámeček pro výstup
frame_bottom = ctk.CTkFrame(root, corner_radius=10)
frame_bottom.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
frame_bottom.grid_rowconfigure(0, weight=1)
frame_bottom.grid_columnconfigure(0, weight=1)

output_text = ctk.CTkTextbox(frame_bottom, height=15, wrap="word", font=("Helvetica", 12))
output_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
output_text.tag_config("error", foreground="red")
output_text.tag_config("success", foreground="green")
sys.stdout = RedirectText(output_text)

#Tlačítko zpět
back_button = ctk.CTkButton(frame_bottom, text="Back to menu", command=go_back_to_main, font=("Helvetica", 12, "bold"))
back_button.grid(row=3, column=0, padx=10, pady=10, ipadx=10, ipady=5, sticky="w")

# Tlačítko pro vymazání textového pole
clear_button = ctk.CTkButton(frame_bottom, text="Clear", command=clear_output, fg_color="green", font=("Helvetica", 12, "bold"))
clear_button.grid(row=1, column=0, padx=10, pady=10, ipadx=10, ipady=5, sticky="e")

# Tlačítko pro restart aplikace
#reset_button = ctk.CTkButton(frame_bottom, text="Resetovat", command=reset_app, fg_color="green", font=("Helvetica", 12, "bold"))
#reset_button.grid(row=1, column=0, padx=10, pady=10, ipadx=10, ipady=5, sticky="w")

# Pokrokový panel
progress_bar = ctk.CTkProgressBar(root, width=200, mode="indeterminate")
progress_bar.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Spuštění GUI
root.mainloop()
