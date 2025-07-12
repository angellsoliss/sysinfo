import socket
import psutil
import time
import platform
import psutil
import ipaddress
import pathlib
from rich.console import Console
from rich.table import Table

def get_primary_ip():
    for interface_name, interface_addrs in psutil.net_if_addrs().items():
        #iterate through addresses in each individual dictionary entry
        for addr in interface_addrs:
            #check if address is ipv4
            if addr.family == socket.AF_INET:
                ip = addr.address #get ip address as string from addr object
                ip_obj = ipaddress.ip_address(ip) #convert string into ip address object, allows for the use of .is_loopback/.is_link_local methods
                
                if ip_obj.is_loopback or ip_obj.is_link_local:
                    continue
                if 'tailscale' in interface_name.lower() or 'docker' in interface_name.lower() or 'virtual' in interface_name.lower():
                    continue

                return ip, interface_name
    return None, None
                
def get_system_uptime() -> str:
    last_boot = psutil.boot_time()
    current_time = time.time()

    uptime_seconds = current_time - last_boot
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24

    return f"{int(uptime_days)}:{int(uptime_hours)%24}:{int(uptime_minutes)%60}:{int(uptime_seconds)%60}"

#determines if system is using windows 10 or 11 bc the version numbering convention is weird
def windows_check(name, version, release) -> str:
    if name == "Windows" and release == "10":
        build_number = int(version.split(".")[-1])
        if build_number >= 22000:
            return "Windows 11"
        else:
            return "Windows 10" 
        
def get_primary_drive_letter() -> str:
    drive_letter = pathlib.Path.home().drive
    return drive_letter

uname_info = platform.uname()
OS_name = platform.system()
OS_release = uname_info.release
OS_version = uname_info.version
hostname = socket.gethostname()
IP, int_name = get_primary_ip()
primary_drive_letter = get_primary_drive_letter()
disk_stats = list(psutil.disk_usage(primary_drive_letter))
disk_usage = round((100 - disk_stats[3]), 2)
min_percent_disk_space = 10
cpu_usage = psutil.cpu_percent()
RAM_stats = list(psutil.virtual_memory())
RAM_usage = RAM_stats[2]

table = Table(title=f"System Statistics for {hostname}/{IP}", header_style="green")

table.add_column("Metric", justify="left", style="cyan", no_wrap=True)
table.add_column("Information", justify="left", no_wrap=True)

table.add_row("OS ", f"{windows_check(OS_name, OS_version, OS_release)}")
table.add_row("OS Version", f"{OS_version}")
if disk_usage < min_percent_disk_space:
    table.add_row(f"Disk Space ({primary_drive_letter}) ", f"{disk_usage}% [bold red]CRITICALLY LOW!!![/bold red]")
else:
    table.add_row(f"Disk Space ({primary_drive_letter})", f"{disk_usage}%")
table.add_row("Uptime", f"{get_system_uptime()}")
if cpu_usage >= 80:
    table.add_row("CPU Usage", f"{cpu_usage}% [bold red]CRITICALLY HIGH!!![/bold red]")
else:
    table.add_row("CPU Usage", f"{cpu_usage}%")
if RAM_usage >= 80:
    table.add_row("RAM Usage", f"{RAM_usage}% [bold red]CRITICALLY HIGH!!![/bold red]")
else:
    table.add_row("RAM Usage", f"{RAM_usage}%")

console = Console()
console.print(table)

'''
console.print(f"[cyan1]System Statistics for {hostname}/{IP}[cyan1]")
print("------------------------------------------")
print(f"OS: {windows_check(OS_name, OS_version, OS_release)}")
print(f"OS Version: {OS_version}")
if disk_usage < min_percent_disk_space:
    console.print(f"[bold red]ALERT![/bold red] ONLY {disk_usage}% SPACE REMAINING ON {primary_drive_letter}, PRIORITIZE DISK CLEANUP")
else:
    print(f"% Disk Space Remaining on {primary_drive_letter} = {disk_usage}%")
print(get_system_uptime())
print(f"CPU Usage: {cpu_usage}%")
print("------------------------------------------")
'''