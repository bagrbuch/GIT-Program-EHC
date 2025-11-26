import os
import argparse
from Calculation_files_potenciostatic import Import_csv as script1
from Calculation_files_potenciostatic import EHC as script2 

#---------------------------Processing all folders of measurement in base folder---------------------

def process_all_folders(base_directory, thickness_var, volume_var):
    for folder in os.listdir(base_directory):
        folder_path = os.path.join(base_directory, folder)

        if not os.path.isdir(folder_path):
            continue

        print(f"\n=== Processing measurement: {folder} ===")

        # Primární hledání pevně pojmenovaných souborů
        csv_file_name = "pressures.csv"
        txt_file_name = "potenciostat.txt"

        csv_path = os.path.join(folder_path, csv_file_name)
        txt_path = os.path.join(folder_path, txt_file_name)

        # Fallback: pokud soubor neexistuje, hledej první soubor daného typu
        if not os.path.exists(csv_path):
            csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]
            if csv_files:
                csv_path = os.path.join(folder_path, csv_files[0])
            else:
                print("  -> Nenalezen žádný CSV soubor, přeskočeno.")
                continue

        if not os.path.exists(txt_path):
            txt_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".txt")]
            if txt_files:
                txt_path = os.path.join(folder_path, txt_files[0])
            else:
                print("  -> Nenalezen žádný TXT soubor (CA file), přeskočeno.")
                continue

        # Přesun nebo přejmenování souborů na standardní názvy
        target_csv_path = os.path.join(folder_path, "pressures.csv")
        target_txt_path = os.path.join(folder_path, "potenciostat.txt")

        if csv_path != target_csv_path:
            os.rename(csv_path, target_csv_path)
            csv_path = target_csv_path

        if txt_path != target_txt_path:
            os.rename(txt_path, target_txt_path)
            txt_path = target_txt_path

        # 1) trim
        import_and_trim_file(csv_path, txt_path, csv_path)
        print(f" Measurement trimmed \n ")
        
        # 2) graphs
        process_graph(txt_path, thickness_var, volume_var)

#--------------------Process input files (pressures and data from potenciostat)---------------------------------

def import_and_trim_file(file_path, ca_file_path, output_path):
    if not output_path:
        output_path = os.path.join(os.path.dirname(file_path), "data_trimmed.csv")

    script1.find_and_trim_csv(file_path, ca_file_path, output_path)
    return output_path

#-------------------Process data and plot/save graphs and create export_data file--------------------------------

def process_graph(ca_file_path, thickness_var, volume_var):

    selected_graphs = []

    compression_file_path = os.path.join(os.path.dirname(ca_file_path), "compression.csv")
    additional_file_path = os.path.join(os.path.dirname(ca_file_path), "diffusion.csv")

    script2.dataplot(ca_file_path, ca_file_path, compression_file_path,additional_file_path,thickness_var, volume_var, selected_graphs=selected_graphs, export_directory=os.path.dirname(ca_file_path)) 

#----------------------------------------------------------------------------------------------------------------
#---------------------------------Part for CLI ------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def ask_for_float(prompt, default=None):

    while True:
        value= input(f"{prompt} [{default}]: ") or str(default)
        try:
            return float(value)
        except ValueError:
            print("Enter value")

def ask_for_path(prompt):

    while True:
        value = input(f"{prompt}: ")
        if os.path.exists(value):
            return value
        print("Path doesn't exist")

def main():
    # Global path for files
    file_path = ""
    ca_file_path = ""
        
    parser = argparse.ArgumentParser(description= "Run data processing")
    
    parser.add_argument("--folder_path")

    parser.add_argument("--ca_file_path")

    parser.add_argument("--thickness", type=float)

    parser.add_argument("--volume", type=float)

    args = parser.parse_args()

    folder_path = args.folder_path or ask_for_path("Enter folder path")
    thickness_var = args.thickness or ask_for_float("Enter thickness of membrane [µm]\n\n Fumapem FS-715  |  15 µm \n Nafion HP  |  20.3 µm \n Nafion 211  |  25.4 µm \n Nafion 212  |  50.8 µm\n Nafion 115  |  127 µm\n Nafion 117  |  183 µm\n\n")
    volume_var = args.volume or ask_for_float("enter volume [cm³] \n\nVolume since 2024 = 8.5 cm³; Volume from 2025 = 11 cm³\n\n ")
    args = parser.parse_args()


    process_all_folders(folder_path, thickness_var, volume_var)

if __name__=="__main__":
    main()