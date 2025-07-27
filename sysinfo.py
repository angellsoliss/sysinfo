import socket
import psutil
import time
import platform
import psutil
import ipaddress
import wmi
import cpuinfo
from rich.console import Console
from rich.table import Table

def get_primary_ip() -> str | None:
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

def get_gpus() -> str | list :
    w = wmi.WMI()
    gpus_list = []
    for gpu in w.Win32_VideoController():
        gpus_list.append(gpu.Name)
    
    if len(gpus_list) >= 1:
        return gpus_list
    else:
        return "No GPU detected"
    
uname_info = platform.uname()
OS_name = platform.system()
OS_release = uname_info.release
OS_version = uname_info.version
hostname = socket.gethostname()
IP, int_name = get_primary_ip()
min_percent_disk_space = 10
cpu_usage = psutil.cpu_percent()
RAM_stats = list(psutil.virtual_memory())
RAM_usage = RAM_stats[2]
partitions = psutil.disk_partitions()
gpus = get_gpus()

table = Table(title=f"System Statistics for {hostname}/{IP}", header_style="green")

table.add_column("Metric", justify="right", style="cyan", no_wrap=True)
table.add_column("Information", justify="left", no_wrap=True)

table.add_row("OS ", f"{windows_check(OS_name, OS_version, OS_release)}")
table.add_row("OS Version", f"{OS_version}")

for p in partitions:
    drive_letter = p.mountpoint
    space_remaining = round(100 - psutil.disk_usage(drive_letter)[3], 2)
    if space_remaining < min_percent_disk_space:
        table.add_row(f"Drive Space Remaining ({drive_letter[0]})", f"{space_remaining}% [bold red]CRITICALLY LOW!!![/bold red]")
    else:
        table.add_row(f"Drive Space Remaining ({drive_letter[0]}) ", f"{space_remaining}%")

table.add_row("Uptime", f"{get_system_uptime()}")

table.add_row("CPU", f"{cpuinfo.get_cpu_info()['brand_raw']}")

table.add_row("Platform", f"{platform.machine()}")

table.add_row("GPU(s)", f"{gpus}")

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