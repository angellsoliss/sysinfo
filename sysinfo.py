import socket
import psutil
import time
import platform

def get_system_uptime():
    last_boot = psutil.boot_time()
    current_time = time.time()

    uptime_seconds = current_time - last_boot
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24

    return f"System Uptime: {int(uptime_days)}:{int(uptime_hours)%24}:{int(uptime_minutes)%60}:{int(uptime_seconds)%60}"

#determines if system is using windows 10 or 11 bc the version numbering convention is weird
def windows_check(name, version, release):
    if name == "Windows" and release == "10":
        build_number = int(version.split(".")[-1])
        if build_number >= 22000:
            return "Windows 11"
        else:
            return "Windows 10" 

uname_info = platform.uname()
OS_name = platform.system()
OS_release = uname_info.release
OS_version = uname_info.version
hostname = socket.gethostname()
IP = socket.gethostbyname(hostname)

print(f"System Statistics for {hostname}/{IP}")
print(f"OS: {windows_check(OS_name, OS_version, OS_release)}")
print(f"OS Version: {OS_version}")
print(get_system_uptime())
