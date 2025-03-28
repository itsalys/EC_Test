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

        self.display_env = os.environ.get("DISPLAY", ":0")
        self.blank = False
        self.hdmi_connected = self.detect_hdmi()
        self.hide_ui()

    def detect_hdmi(self):
        try:
            drm_dir = "/sys/class/drm/"
            for root, dirs, files in os.walk(drm_dir):
                for name in files:
                    if name == "status" and "HDMI" in root:
                        with open(os.path.join(root, name), "r") as f:
                            if f.read().strip() == "connected":
                                print(f"[UI] HDMI connected at {root}")
                                return True
            print("[UI] No HDMI connection found in DRM paths.")
            return False
        except Exception as e:
            print(f"[UI] HDMI detection failed: {e}")
            return False

    def show_message(self, message, colour="white"):
        self.label.config(text=message, fg=colour, bg="black")
        self.root.configure(bg="black")
        self.show_ui()
        self.root.update()

    def show_ui(self):
        if self.blank:
            if self.hdmi_connected:
                try:
                    subprocess.run(["vcgencmd", "display_power", "1"], check=False)
                except Exception as e:
                    print(f"[UI] Warning: vcgencmd display_power 1 failed: {e}")
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

        # Try to power off HDMI if connected
        if self.hdmi_connected:
            try:
                subprocess.run(["vcgencmd", "display_power", "0"], check=False)
            except Exception as e:
                print(f"[UI] Warning: vcgencmd display_power 0 failed: {e}")

    def run(self):
        self.root.mainloop()
