import socket

# get hostname
hostname = socket.gethostname()

# Get actual local IP address (excluding loopback)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 80))  # External IP to trigger route discovery
    ip_address = s.getsockname()[0]
except Exception:
    ip_address = "Unable to detect IP"
finally:
    s.close()

print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")
