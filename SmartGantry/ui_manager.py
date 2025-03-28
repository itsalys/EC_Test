import os
import subprocess
import tkinter as tk
import time

class UIManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Gantry System")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 32, "bold"),
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

    def get_hdmi_status_path(self):
        drm_dir = "/sys/class/drm/"
        for entry in os.listdir(drm_dir):
            if "HDMI" in entry:
                status_path = os.path.join(drm_dir, entry, "status")
                return status_path
        return None


    def detect_hdmi(self):
        try:
            drm_dir = "/sys/class/drm/"
            found_any = False

            print("[UI] Scanning HDMI entries in /sys/class/drm/")

            for entry in os.listdir(drm_dir):
                full_path = os.path.join(drm_dir, entry)
                if not os.path.isdir(full_path):
                    continue

                # Follow symlinks manually
                if "HDMI" in entry:
                    status_path = os.path.join(full_path, "status")
                    print(f"[UI] Checking: {status_path}")
                    if os.path.isfile(status_path):
                        try:
                            with open(status_path, "r") as f:
                                status = f.read().strip()
                                print(f"[UI] {status_path}: {status}")
                                if status == "connected":
                                    print(f"[UI] HDMI is connected at {entry}")
                                    return True
                        except Exception as e:
                            print(f"[UI] Failed to read {status_path}: {e}")
                        found_any = True

            if not found_any:
                print("[UI] No HDMI entries found in DRM paths.")
            else:
                print("[UI] No HDMI display is currently connected.")

        except Exception as e:
            print(f"[UI] HDMI detection failed: {e}")

        print("[UI] Falling back: assuming HDMI is connected")
        return True  # fallback for reliability

    def show_message(self, message, colour="white"):
        self.label.config(text=message, fg=colour, bg="black")
        self.root.configure(bg="black")
        self.show_ui()
        self.root.update()

    def show_ui(self):
        if self.blank:
            if self.hdmi_connected:
                try:
                    path_check = subprocess.run(["which", "vcgencmd"], capture_output=True, text=True)
                    vcgencmd_path = path_check.stdout.strip()

                    if not vcgencmd_path:
                        print("[UI] Error: 'vcgencmd' not found in PATH.")
                        return

                    print("[UI] Turning on HDMI display...")
                    subprocess.run([vcgencmd_path, "display_power", "1"], check=True)

                    # Fixed 1 second wait to allow screen to power on
                    time.sleep(2)

                except subprocess.CalledProcessError as e:
                    print(f"[UI] vcgencmd failed: {e.stderr.strip()}")
                except Exception as e:
                    print(f"[UI] Unexpected error during display power on: {e}")

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
                # Dynamically locate vcgencmd
                path_check = subprocess.run(["which", "vcgencmd"], capture_output=True, text=True)
                vcgencmd_path = path_check.stdout.strip()

                if not vcgencmd_path:
                    print("[UI] Error: 'vcgencmd' not found in PATH.")
                    return

                result = subprocess.run(
                    [vcgencmd_path, "display_power", "0"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"[UI] vcgencmd output: {result.stdout.strip()}")

            except subprocess.CalledProcessError as e:
                print(f"[UI] vcgencmd failed: {e.stderr.strip()}")
            except Exception as e:
                print(f"[UI] Unexpected error during display power off: {e}")

    def run(self):
        self.root.mainloop()
