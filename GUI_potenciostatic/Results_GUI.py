import os
import sys
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
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
    folder_path = filedialog.askdirectory()
    if folder_path:
        show_folder_contents(folder_path)

def show_folder_contents(folder_path):
    try:
        folder_label.configure(text=f"Content of folder: {folder_path}")
        file_listbox.delete(0, tk.END)
        parent_folder = os.path.dirname(folder_path)
        if folder_path != parent_folder:
            file_listbox.insert(tk.END, "[..] Go to parent folder")
        for file_name in os.listdir(folder_path):
            full_path = os.path.join(folder_path, file_name)
            if os.path.isdir(full_path):
                file_listbox.insert(tk.END, f"[Folder] {file_name}")
            else:
                file_listbox.insert(tk.END, file_name)
    except Exception as e:
        output_text.configure(state=tk.NORMAL)
        output_text.insert(tk.END, f"Chyba: {str(e)}\n")
        output_text.configure(state=tk.DISABLED)

def process_double_click(event):
    selected_item = file_listbox.curselection()
    if selected_item:
        item_name = file_listbox.get(selected_item[0])
        folder_path = folder_label.cget("text").replace("Content of folder: ", "")
        if item_name.startswith("[Folder]"):
            new_folder_path = os.path.join(folder_path, item_name.replace("[Folder] ", ""))
            show_folder_contents(new_folder_path)
        elif item_name.startswith("[..]"):
            parent_folder = os.path.dirname(folder_path)
            show_folder_contents(parent_folder)
        else:
            global selected_file
            selected_file = os.path.join(folder_path, item_name)
            output_text.configure(state=tk.NORMAL)
            output_text.insert(ctk.END, f"Selected file: {selected_file}\n")
            output_text.configure(state=tk.DISABLED)

def show_graph():
    output_text.configure(state=tk.NORMAL)
    sys.stdout = RedirectText(output_text)

    try:
        print("\n----------------------------------------------\n")
        from Graphs_setting.Graphs_in_Results_GUI import plot_graphs_from_export

        if selected_file:
            # Získání seznamu vybraných grafů
            selected_graphs = [
                int(graph) for graph, selected in {
                    "1": graph1_var.get(),
                    "2": graph2_var.get(),
                    "3": graph3_var.get(),
                    "4": graph4_var.get(),
                    "5": graph5_var.get(),
                    "6": graph6_var.get(),
                    "7": graph7_var.get()
                }.items() if selected
            ]

            if selected_graphs:
                plot_graphs_from_export(selected_file, selected_graphs)
                # print(f"Zobrazeny grafy: {selected_graphs}")
            else:
                print("No charts were selected.")
        else:
            print("Error: No file selected.")
    except Exception as e:
        print(f"Error when displaying the chart: {str(e)}")
    finally:
        output_text.configure(state=tk.DISABLED)

def clear_text():
    output_text.configure(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.configure(state=tk.DISABLED)

# Návrat zpět do hlavního menu
def go_back_to_main():
    root.destroy()
    GUI.main_app()

# Hlavní GUI
root = ctk.CTk()
root.title("File selection in the GUI")
root.geometry("850x750")

# Horní část (levý a pravý panel vedle sebe)
frame_top = ctk.CTkFrame(root, corner_radius=10)
frame_top.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)

# Levý panel: seznam souborů
frame_left = ctk.CTkFrame(frame_top, corner_radius=10)
frame_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

select_button = ctk.CTkButton(frame_left, text="Select folder", command=select_folder, fg_color="#1E90FF")
select_button.grid(row=0, column=0, padx=10, pady=10)

folder_label = ctk.CTkLabel(frame_left, text="Enter the path to the folder:")
folder_label.grid(row=1, column=0, padx=10, pady=10)

file_listbox = tk.Listbox(frame_left, height=15, width=50)
file_listbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew", rowspan=2)
file_listbox.bind("<Double-1>", process_double_click)

# Pravý panel: zaškrtávací políčka a tlačítko
frame_right = ctk.CTkFrame(frame_top, corner_radius=10)
frame_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Proměnné pro zaškrtávací políčka
graph1_var = tk.IntVar()
graph2_var = tk.IntVar()
graph3_var = tk.IntVar()
graph4_var = tk.IntVar()
graph5_var = tk.IntVar()
graph6_var = tk.IntVar()
graph7_var = tk.IntVar()

checkbuttons = [
    ("Current density and pressure vs Time", graph1_var),
    ("Current density vs Pressure", graph2_var),
    ("Flow diffusion", graph3_var),
    ("Eenrgy consumption", graph4_var),
    ("Graphs all efficiencies vs Time", graph5_var),
    ("Graph pressure vs Work eff", graph6_var),
    ("Fit from decompression", graph7_var)
]

for idx, (text, var) in enumerate(checkbuttons):
    ctk.CTkCheckBox(frame_right, text=text, variable=var).grid(row=idx, column=0, padx=10, pady=5, sticky="w")

graph_button = ctk.CTkButton(frame_right, text="Show graph", fg_color="#1E90FF", command=show_graph)
graph_button.grid(row=len(checkbuttons), column=0, padx=10, pady=10, sticky="nsew")

# Spodní část: textové pole a tlačítko
frame_bottom = ctk.CTkFrame(root, corner_radius=10)
frame_bottom.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)

output_text = ctk.CTkTextbox(frame_bottom, width=400, height=300, wrap="word")
output_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

clear_button = ctk.CTkButton(frame_bottom, text="Clear", command=clear_text, fg_color="green")
clear_button.grid(row=1, column=0, padx=10, pady=10, sticky="e")

#Tlačítko zpět
back_button = ctk.CTkButton(frame_bottom, text="Back to menu", command=go_back_to_main, font=("Helvetica", 12, "bold"))
back_button.grid(row=3, column=0, padx=10, pady=10, ipadx=10, ipady=5, sticky="w")

# Nastavení roztažnosti jednotlivých částí
root.grid_rowconfigure(0, weight=2)  # Horní část (seznam + checkboxy)
root.grid_rowconfigure(1, weight=1)  # Spodní část (textové pole)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

frame_top.grid_rowconfigure(0, weight=1)
frame_top.grid_columnconfigure(0, weight=1)
frame_top.grid_columnconfigure(1, weight=1)

frame_bottom.grid_rowconfigure(0, weight=1)
frame_bottom.grid_columnconfigure(0, weight=1)

root.mainloop()
