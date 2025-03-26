import os
import subprocess
import tkinter as tk

class UIManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Gantry System")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 64, "bold"),
            fg="white",
            bg="black",
            wraplength=1800,
            justify="center"
        )
        self.label.pack(expand=True)


        self.root.bind("q", self.quit_app)
        self.root.bind("<Escape>", self.quit_app)  # Optional: Esc key also quits

        self.display_env = os.environ.get("DISPLAY", ":0")
        self.blank = False
        self.hide_ui()

    def show_message(self, message, colour="white"):
        self.label.config(text=message, fg=colour, bg="black")
        self.root.configure(bg="black")
        self.show_ui()
        self.root.update()

    def show_ui(self):
        if self.blank:
            try:
                subprocess.run(["xset", "dpms", "force", "on"], env={"DISPLAY": self.display_env}, check=False)
            except Exception as e:
                print(f"[UI] Warning: xset on failed: {e}")
            self.root.deiconify()
            self.blank = False
        self.root.update()

    def hide_ui(self):
        # Visually blank the UI
        self.label.config(text="", fg="black", bg="black")
        self.root.configure(bg="black")
        self.root.deiconify()
        self.root.update()
        self.blank = True

        # Try to power off display
        try:
            subprocess.run(["xset", "dpms", "force", "off"], env={"DISPLAY": self.display_env}, check=False)
        except Exception as e:
            print(f"[UI] Warning: xset off failed: {e}")

    def quit_app(self, event=None):
        print("[UI] Quit signal received. Closing application...")
        self.root.destroy()
        exit(0)


    def run(self):
        self.root.mainloop()
