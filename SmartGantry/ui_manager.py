import tkinter as tk
import subprocess

class UIManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Gantry System")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.label = tk.Label(self.root, text="", font=("Helvetica", 32), fg="white", bg="black", wraplength=800)
        self.label.pack(expand=True)

        self.hide_ui()

    def show_message(self, message, colour="white"):
        self.label.config(text=message, fg=colour)
        self.show_ui()
        self.root.update()

    def show_ui(self):
        subprocess.run(["vcgencmd", "display_power", "1"])
        self.root.deiconify()
        self.root.update()

    def hide_ui(self):
        subprocess.run(["vcgencmd", "display_power", "0"])
        self.root.withdraw()

    def run(self):
        self.root.mainloop()
