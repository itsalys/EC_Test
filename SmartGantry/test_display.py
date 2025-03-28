import subprocess

def test_display_power_off():
    print("[TEST] Checking if 'vcgencmd' is available...")

    # Optional: Print full path to vcgencmd
    path_check = subprocess.run(["which", "vcgencmd"], capture_output=True, text=True)
    vcgencmd_path = path_check.stdout.strip()

    if not vcgencmd_path:
        print("[ERROR] 'vcgencmd' not found in PATH.")
        return

    print(f"[TEST] Using vcgencmd at: {vcgencmd_path}")
    print("[TEST] Turning off HDMI display...")

    try:
        result = subprocess.run(
            [vcgencmd_path, "display_power", "0"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"[SUCCESS] vcgencmd output: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed with error: {e.stderr.strip()}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    test_display_power_off()