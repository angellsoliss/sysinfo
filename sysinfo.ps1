#get hostname and ip
$hostname = $env:COMPUTERNAME

#Get_NetIPAddress -AddressFamily IPv4 returns the addresses assigned to all network interfaces on the system
#ignore link local addresses (169.254.*) and loopback (127.*)
#Select the first address of the primary network interfaces (Wifi/ethernet)
$ip = (Get-NetIPAddress -AddressFamily IPv4 `
| Where-Object { $_.IPAddress -notlike '169.254.*' -and $_.IPAddress -notlike '127.*' } `
| Select-Object -First 1 -ExpandProperty IPAddress)

#get system uptime
$now = Get-Date
$last_boot = Get-CimInstance -ClassName Win32_OperatingSystem |`
    Select-Object -ExpandProperty LastBootUpTime

$uptime = $now - $last_boot
$days = $uptime.Days
$hours = $uptime.Hours
$minutes = $uptime.Minutes
$seconds = $uptime.Seconds

#get os name and version
$OS_info = (Get-ComputerInfo | Select-Object OsName, OsVersion)

Write-Host (Get-Date)
Write-Host "System Statistics for $hostname/$ip"
Write-Host "-----------------------------------------------"
Write-Host "$OS_info"
Write-Host "Uptime: $days days, $hours hours, $minutes minutes, $seconds seconds"