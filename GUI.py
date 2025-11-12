import customtkinter as ctk
from PIL import Image
import sys
import os

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

gif_path = os.path.join(base_path, "ECC.gif")

class LoadingScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Loading...")
        self.root.geometry("500x400")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Main frame for all elements
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#2E2E2E")
        self.main_frame.pack(fill="both", expand=True)

        # Create a label to display the GIF
        self.gif_label = ctk.CTkLabel(self.main_frame, text="", fg_color="transparent")
        self.gif_label.pack(pady=20) 

        # Load the GIF
        self.gif_image = Image.open(gif_path)
        self.gif_frames = []

        # Desired width for the GIF (you can adjust this value)
        gif_width = 500
        gif_height = int(gif_width * (9 / 16))

        # Define the crop area (left, upper, right, lower)
        left = 30
        upper = 10
        right = gif_width + left
        lower = gif_height + upper

        try:
            for frame in range(self.gif_image.n_frames):
                self.gif_image.seek(frame)
                # Crop the GIF to the desired region
                cropped_image = self.gif_image.crop((left, upper, right, lower))
                # Convert to CTkImage with 16:9 aspect ratio size
                ct_image = ctk.CTkImage(cropped_image.copy(), size=(gif_width, gif_height))
                self.gif_frames.append(ct_image)
        except EOFError:
            pass  # End of GIF frames

        # Start the GIF animation
        self.animate_gif(0)

        # Loading text
        self.loading_text = ctk.CTkLabel(
            self.main_frame,
            text="Loading...",
            font=("Helvetica", 16, "bold"),
            text_color="white")
        self.loading_text.pack(pady=10)

        # Progress bar placed below the GIF
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, orientation="horizontal", mode="determinate", width=300)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)  # Start at 0%

        # Start the loading process
        self.progress_value = 0
        self.update_progress()

    def animate_gif(self, frame=0):
        """Animates the GIF."""
        if self.gif_frames:
            self.gif_label.configure(image=self.gif_frames[frame])
            self.root.after(50, self.animate_gif, (frame + 1) % len(self.gif_frames))  # Loop the GIF

    def update_progress(self):
        """Updates the progress bar and loading text."""
        if self.progress_value < 1.0:  # 1.0 = 100%
            self.progress_value += 0.2  # Increment progress
            self.progress_bar.set(self.progress_value)

            # Update loading text dynamically
            if self.progress_value < 0.5:
                self.loading_text.configure(text="Loading...")
            elif self.progress_value < 0.9:
                self.loading_text.configure(text="...")
            else:
                self.loading_text.configure(text="Done...")

            self.root.after(100, self.update_progress)  # Call again after 100ms
        else:
            self.load_complete()

    def load_complete(self):
        """Destroys the loading screen and starts the main application."""
        self.root.destroy()  # Close the loading window
        main_app()  # Start the main application


def main_app():
    """Main application function."""
    root = ctk.CTk()
    app = AdvancedApp(root)
    root.mainloop()

class AdvancedApp:

    def __init__(self, root):
        self.root = root
        self.root.title("EHC menu")
        self.root.geometry("365x450")

        # Nastavení vzhledu aplikace
        ctk.set_appearance_mode("dark")  # Výchozí režim je tmavý
        ctk.set_default_color_theme("blue")

        # Hlavní rámec aplikace
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, padx=0, pady=10, sticky="nsew")
        
        # Dynamické nastavení barvy textu pro label
        self.label = ctk.CTkLabel(
            self.main_frame,
            text="Electrochemical hydrogen compression",
            font=("Helvetica", 16, "bold"),
        )
        self.label.grid(pady=10, sticky= "nsew")

        # Tlačítka aplikace
        self.create_buttons()

        # Přepínač režimu v pravém dolním rohu
        self.theme_switch = ctk.CTkSwitch(
            self.root,
            text="Mode",
            command=self.toggle_theme,
            onvalue="dark",  # Nastavení světlého režimu na hodnotu "on"
            offvalue="light",   # Nastavení tmavého režimu na hodnotu "off"
            width=80
        )
        # Umístění přepínače na správné místo
        self.theme_switch.place(relx=0.98, rely=0.98, anchor="se")
        
        # Nastavení přepínače podle aktuálního režimu
        if ctk.get_appearance_mode() == "dark":
            self.theme_switch.deselect()  # Pokud je tmavý režim, přepínač je vypnutý
        else:
            self.theme_switch.select()  # Pokud je světlý režim, přepínač je zapnutý
          

    def create_buttons(self):
        """Vytvoří tlačítka pro různé části aplikace."""
        # Nadpis nad rámečkem
        label_heading = ctk.CTkLabel( self.main_frame, text="Potentiostatic mode", font=("Helvetica", 14))
        label_heading.grid(row=1, column=0, pady=(0, 5))  # Nad rámečkem

        # Rámeček s tlačítky
        button_frame = ctk.CTkFrame(self.main_frame,corner_radius=10,fg_color="transparent",border_width=2,border_color="white")
        button_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        # Roztáhnout sloupce uvnitř rámečku
        button_frame.grid_columnconfigure((0, 1), weight=1)

        # Tlačítka
        button_1 = ctk.CTkButton(button_frame, text="Data import", command=self.start_part1)
        button_1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        button_2 = ctk.CTkButton(button_frame, text="Results", command=self.start_part2)
        button_2.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        button_3 = ctk.CTkButton(button_frame, text="Data comparison", command=self.start_part3)
        button_3.grid(row=1, column=0, padx=10, pady=10, sticky="ew")


        # Nadpis nad rámečkem 2
        label_heading = ctk.CTkLabel( self.main_frame, text="Galvanostatic mode", font=("Helvetica", 14))
        label_heading.grid(row=3, column=0, pady=(0, 5))  # Nad rámečkem

        # Rámeček s tlačítky
        button_frame = ctk.CTkFrame(self.main_frame,corner_radius=10,fg_color="transparent",border_width=2,border_color="white")
        button_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)

        # Roztáhnout sloupce uvnitř rámečku
        button_frame.grid_columnconfigure((0, 1), weight=1)

        # Tlačítka
        button_1 = ctk.CTkButton(button_frame, text="Data import", command=self.start_part4)
        button_1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        button_2 = ctk.CTkButton(button_frame, text="Results", command=self.start_part5)
        button_2.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        button_3 = ctk.CTkButton(button_frame, text="Data comparison", command=self.start_part6)
        button_3.grid(row=1, column=0, padx=10, pady=10, sticky="ew")


    def toggle_theme(self):
        """Switches between light and dark mode."""
        current_mode = ctk.get_appearance_mode()  # Získá aktuální režim
        new_mode = "light" if current_mode == "dark" else "dark"  # Přepne režim
        ctk.set_appearance_mode(new_mode)  # Nastaví nový režim

        # Změní textovou barvu labelu podle režimu
        self.update_label_text_color()

        # Režim se automaticky změní na základě aktuální hodnoty přepínače
        if self.theme_switch.get() == "light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")

    def update_label_text_color(self):
        """Dynamically changes the color of the text on the label according to the current mode."""
        current_mode = ctk.get_appearance_mode()
        if current_mode == "dark":
            self.label.configure(text_color="white")  # Pro tmavý režim text bude bílý
        
        if current_mode =="white":
            self.label.configure(text_color="black")


    def start_part1(self):
        # Zavře hlavní okno AdvancedApp
        self.root.destroy()
        
        # Otevře import_data_GUI
        from GUI_potenciostatic import import_data_GUI
        import_data_GUI.open_import_data_GUI()  # Otevře nové GUI

    def start_part4(self):
        # Zavře hlavní okno AdvancedApp
        self.root.destroy()
        
        # Otevře import_data_GUI
        from GUI_galvanostatic import import_data_GUI_I
        import_data_GUI_I.open_import_data_GUI_I()  # Otevře nové GUI

    def start_part2(self):
        # Zavře hlavní okno AdvancedApp
        self.root.destroy()
        
        # Otevře Plot_data_GUI
        from GUI_potenciostatic import Results_GUI
        Results_GUI.open_import_data_GUI()  # Otevře nové GUI

    def start_part5(self):
        # Zavře hlavní okno AdvancedApp
        self.root.destroy()
        
        # Otevře Plot_data_GUI
        from GUI_galvanostatic import Plot_data_GUI_I
        Plot_data_GUI_I.open_import_data_GUI_I()  # Otevře nové GUI

    def start_part3(self):
        self.root.destroy()

        from GUI_potenciostatic import compare_data_GUI
        compare_data_GUI.open_import_data_GUI()

    def start_part6(self):
        self.root.destroy()

        from GUI_galvanostatic import compare_data_GUI_I
        compare_data_GUI_I.open_import_data_GUI_I()


if __name__ == "__main__":
    # Main application execution
    loading_root = ctk.CTk()
    LoadingScreen(loading_root)  # Show loading screen
    loading_root.mainloop()
