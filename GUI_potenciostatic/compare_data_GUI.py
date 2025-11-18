import os
import sys
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from Compare_CZ import process_filtered_files
import GUI

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        if text == '\n':
            return
        self.text_widget.insert(ctk.END, text)
        self.text_widget.yview(ctk.END)

    def flush(self):
        pass

def select_folder():
    global selected_folder
    selected_folder = filedialog.askdirectory()
    if selected_folder:
        update_file_list()

def update_file_list(*args):
    """ Updates the file list based on searches """
    search_query = search_entry.get().lower()
    file_listbox.delete(0, tk.END)
    
    if not selected_folder:
        return
    
    for root_dir, _, files in os.walk(selected_folder):
        for file in files:
            if search_query in file.lower():
                relative_path = os.path.relpath(os.path.join(root_dir, file), selected_folder)
                file_listbox.insert(tk.END, relative_path)

def process_double_click(event):
    selected_item = file_listbox.curselection()
    if selected_item:
        item_name = file_listbox.get(selected_item[0])
        global selected_file
        selected_file = os.path.join(selected_folder, item_name)
        output_text.configure(state=tk.NORMAL)
        output_text.insert(ctk.END, f"Selected file: {selected_file}\n")
        output_text.configure(state=tk.DISABLED)

def run_filter_script():
    """ Starts data filtering and displays the output in the GUI """
    global output_data
    output_text.configure(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)

    filtered_files = [file_listbox.get(i) for i in range(file_listbox.size())]
    if not filtered_files:
        output_text.insert(tk.END, "No files found.\n")
        output_text.configure(state=tk.DISABLED)
        return

    try:
        output_data = process_filtered_files(filtered_files, selected_folder, output_text)  # Správný počet argumentů
    except Exception as e:
        output_text.insert(tk.END, f"Data filtering error: {e}\n")

    output_text.configure(state=tk.DISABLED)

def show_graph():
    global output_data
    output_text.configure(state=tk.NORMAL)
    sys.stdout = RedirectText(output_text)

    try:
        print("\n----------------------------------------------\n")
        from Compare_CZ import main
        
        selected_graphs = [
                int(graph) for graph, selected in {
                    "1": graph1_var.get(),
                    "4": graph4_var.get(),
                    "5": graph5_var.get(),
                    "6": graph6_var.get(),
                }.items() if selected
            ]
            
        if selected_graphs:
            main(selected_graphs, output_data)
        else:
            print("No charts were selected.")
        
    except Exception as e:
        print(f"Error when displaying the chart: {str(e)}")
    finally:
        output_text.configure(state=tk.DISABLED)

def TD_graph():
    global output_data
    from Graphs_setting.Graphs_in_Data_comparison_GUI import plot_graph, plot_2d_graph
    plot_graph(output_data)
    plot_2d_graph(output_data)
    

def export():   
    global output_data
    output_text.configure(state=tk.NORMAL)
    sys.stdout = RedirectText(output_text)

    try:
        print("\n----------------------------------------------\n")
        from Compare_CZ import start_LaTeX, export_LaTeX_1, export_LaTeX_2, export_LaTeX_3, end_LaTeX, format

        LATEX_FILE=start_LaTeX(output_data)  # Inicializace souboru
        export_LaTeX_3(output_data, LATEX_FILE)
        export_LaTeX_1(output_data, LATEX_FILE)  # Přidávání tabulek
        export_LaTeX_2(output_data, LATEX_FILE)
        end_LaTeX(LATEX_FILE)  # Ukončení souboru
        format(LATEX_FILE)
    
    except Exception as e:
        print(f"Error when exporting to LaTeX: {str(e)}")

def export_EN():   
    global output_data
    output_text.configure(state=tk.NORMAL)
    sys.stdout = RedirectText(output_text)

    try:
        print("\n----------------------------------------------\n")
        from Compare_EN import start_LaTeX, export_LaTeX_1, export_LaTeX_2, export_LaTeX_3, end_LaTeX, format

        LATEX_FILE=start_LaTeX(output_data)  # Inicializace souboru
        export_LaTeX_3(output_data, LATEX_FILE)
        export_LaTeX_1(output_data, LATEX_FILE)  # Přidávání tabulek
        export_LaTeX_2(output_data, LATEX_FILE)
        end_LaTeX(LATEX_FILE)  # Ukončení souboru
        format(LATEX_FILE)
    
    except Exception as e:
        print(f"Error when exporting to LaTeX: {str(e)}")


def clear_text():
    output_text.configure(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.configure(state=tk.DISABLED)

def go_back_to_main():
    root.destroy()
    GUI.main_app()

def filter_data():
    """ Filters and prints all .txt files to a text box"""
    output_text.configure(state=tk.NORMAL)  # Umožní úpravu textového pole
    output_text.delete(1.0, tk.END)  # Vymaže předchozí text
    
    txt_files = []
    
    # Projde všechny položky v listboxu a vyfiltruje .txt soubory
    for index in range(file_listbox.size()):
        file_path = file_listbox.get(index)
        if file_path.lower().endswith('.txt'):
            txt_files.append(file_path)
    
    # Vypíše seznam do textového pole
    if txt_files:
        output_text.insert(tk.END, "List of .txt files:\n")
        for file in txt_files:
            output_text.insert(tk.END, file + "\n")
    else:
        output_text.insert(tk.END, "No .txt files were found.\n")
    
    output_text.configure(state=tk.DISABLED)  # Uzamkne textové pole pro editaci

def show_help(frame_name):
    help_text = ""
    if frame_name == "graphs":
        help_text = "You need to select the folder for the measurement, then filter “export_data”. Then the graphs can be plotted for comparison. \n A text file in LaTex format can be created at the bottom of the page, which can for example be inserted into Overleaf. The button for graph (pressure/energy consumption will display a comparison graph of the consumption."
    output_text.delete(1.0, ctk.END)  # Vymazání textového pole před zobrazením nového textu
    output_text.insert(ctk.END, help_text)
# GUI Setup
root = ctk.CTk()
root.title("Compare")
root.geometry("675x700")
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)

frame_top = ctk.CTkFrame(root, corner_radius=10)
frame_top.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)

frame_left = ctk.CTkFrame(frame_top, corner_radius=10)
frame_left.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

select_button = ctk.CTkButton(frame_left, text="Select folder", fg_color="#1E90FF", command=select_folder)
select_button.grid(row=0, column=0, padx=5, pady=5)

search_entry = ctk.CTkEntry(frame_left, placeholder_text="Export_data...")
search_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
search_entry.bind("<KeyRelease>", update_file_list)

file_listbox = tk.Listbox(frame_left, height=15, width=50)
file_listbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
file_listbox.bind("<Double-1>", process_double_click)

# Filter button
filter_button = ctk.CTkButton(frame_left, text="Filter data", fg_color="#1E90FF", command=run_filter_script)
filter_button.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

frame_right = ctk.CTkFrame(frame_top, corner_radius=10)
frame_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")


graph1_var, graph2_var, graph3_var, graph4_var, graph5_var, graph6_var = tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()

# Remove the "Current density vs Pressure" and "Flow diffusion plot" options
checkbuttons = [
    ("Current density and pressure Vs time plot", graph1_var),
    ("Energy consumption", graph4_var),
    ("Graphs all efficiencies vs time", graph5_var),
    ("Graphs of net flux vs efficiency", graph6_var)]

# Re-create the checkboxes with the updated list
for idx, (text, var) in enumerate(checkbuttons):
    ctk.CTkCheckBox(frame_right, text=text, variable=var).grid(row=idx, column=0, padx=10, pady=5, sticky="w")

help_button_right = ctk.CTkButton(frame_right, text="?", command=lambda: show_help("graphs"), font=("Helvetica", 12, "bold"), width=30, height=30)
help_button_right.grid(row=len(checkbuttons)+2, column=0, padx=10, pady=10, sticky="sw")

graph_button = ctk.CTkButton(frame_right, text="Show graph", fg_color="#1E90FF", command=show_graph)
graph_button.grid(row=len(checkbuttons), column=0, padx=10, pady=10, sticky="nsew")

frame_bottom = ctk.CTkFrame(root, corner_radius=10)
frame_bottom.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)
frame_bottom.grid_rowconfigure(0, weight=1)
frame_bottom.grid_columnconfigure(0, weight=1)

output_text = ctk.CTkTextbox(frame_bottom, width=600, height=200, wrap="word")
output_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

clear_button = ctk.CTkButton(frame_bottom, text="Clear", command=clear_text, fg_color="green")
clear_button.grid(row=2, column=0, padx=10, pady=10, sticky="e")

back_button = ctk.CTkButton(frame_bottom, text="Back to menu", command=go_back_to_main)
back_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")

export_button = ctk.CTkButton(frame_bottom, text="LaTeX-CZ", fg_color="#1E90FF", command=export,)
export_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")

export_button = ctk.CTkButton(frame_bottom, text="LaTeX-EN", fg_color="#1E90FF", command=export_EN,)
export_button.grid(row=1, column=0, padx=200, pady=10, sticky="w")

TD_button = ctk.CTkButton(frame_bottom, text="Graph (pressure/energy consumption)", fg_color="#1E90FF", command=TD_graph,)
TD_button.grid(row=1, column=0, padx=10, pady=10, sticky="e")

root.mainloop()
 