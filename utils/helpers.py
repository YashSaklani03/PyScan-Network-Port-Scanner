import platform

def os_guess():
    os_name = platform.system()
    return f"Basic fingerprint: {os_name}"
