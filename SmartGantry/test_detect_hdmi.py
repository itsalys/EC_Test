import os

def detect_hdmi():
    try:
        drm_dir = "/sys/class/drm/"
        found_any = False

        print(f"[DEBUG] Walking through {drm_dir}...\n")

        for entry in os.listdir(drm_dir):
            full_path = os.path.join(drm_dir, entry)
            if not os.path.isdir(full_path):
                continue

            # Follow symlinks manually
            if "HDMI" in entry:
                status_path = os.path.join(full_path, "status")
                print(f"[DEBUG] Checking: {status_path}")
                if os.path.isfile(status_path):
                    try:
                        with open(status_path, "r") as f:
                            status = f.read().strip()
                            print(f"[INFO] {status_path}: {status}")
                            if status == "connected":
                                print("[RESULT] HDMI is connected.")
                                return True
                    except Exception as e:
                        print(f"[ERROR] Could not read {status_path}: {e}")
                    found_any = True

        if not found_any:
            print("[INFO] No HDMI entries found in DRM paths.")
        else:
            print("[RESULT] No HDMI display is connected.")
        return False

    except Exception as e:
        print(f"[ERROR] HDMI detection failed: {e}")
        return False
    
def get_hdmi_status_path():
    drm_dir = "/sys/class/drm/"
    for entry in os.listdir(drm_dir):
        if "HDMI" in entry:
            status_path = os.path.join(drm_dir, entry, "status")
            return status_path
    return None


if __name__ == "__main__":
    detect_hdmi()
    print(get_hdmi_status_path())