"""
=============================================================
  System Info & Health Check Tool
  Author  : Priyanshu Negi
  GitHub  : github.com/igpriyanshunegi
  Version : 1.0
  Purpose : Automated system health monitoring and reporting
            for IT Support / Helpdesk use cases
=============================================================
"""

import psutil
import platform
import socket
import datetime
import os
import json
import shutil

# ─────────────────────────────────────────────
#  THRESHOLDS (IT Support standard limits)
# ─────────────────────────────────────────────
THRESHOLD_CPU     = 80   # % — alert if above
THRESHOLD_RAM     = 85   # % — alert if above
THRESHOLD_DISK    = 90   # % — alert if above
THRESHOLD_TEMP    = 75   # °C — alert if above (if sensors available)

# ─────────────────────────────────────────────
#  COLOURS (terminal output)
# ─────────────────────────────────────────────
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def status(value, warn, critical=None):
    """Return coloured OK / WARNING / CRITICAL label."""
    if critical and value >= critical:
        return f"{RED}CRITICAL{RESET}"
    if value >= warn:
        return f"{YELLOW}WARNING{RESET}"
    return f"{GREEN}OK{RESET}"

def separator(char="─", width=60):
    print(f"{CYAN}{char * width}{RESET}")

def section(title):
    separator()
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    separator()

# ─────────────────────────────────────────────
#  1. SYSTEM INFORMATION
# ─────────────────────────────────────────────
def get_system_info():
    section("SYSTEM INFORMATION")
    uname = platform.uname()
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime    = datetime.datetime.now() - boot_time

    info = {
        "Hostname"        : socket.gethostname(),
        "OS"              : f"{uname.system} {uname.release}",
        "OS Version"      : uname.version[:60] + "..." if len(uname.version) > 60 else uname.version,
        "Machine Type"    : uname.machine,
        "Processor"       : uname.processor or platform.processor() or "N/A",
        "Python Version"  : platform.python_version(),
        "Boot Time"       : boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        "System Uptime"   : str(uptime).split(".")[0],
    }
    for k, v in info.items():
        print(f"  {BOLD}{k:<18}{RESET}: {v}")
    return info

# ─────────────────────────────────────────────
#  2. CPU HEALTH
# ─────────────────────────────────────────────
def get_cpu_info():
    section("CPU HEALTH")
    cpu_percent  = psutil.cpu_percent(interval=1)
    cpu_count_l  = psutil.cpu_count(logical=True)
    cpu_count_p  = psutil.cpu_count(logical=False)
    cpu_freq     = psutil.cpu_freq()

    freq_str = f"{cpu_freq.current:.0f} MHz (max {cpu_freq.max:.0f} MHz)" if cpu_freq else "N/A"
    st = status(cpu_percent, THRESHOLD_CPU)

    print(f"  {'Physical Cores':<22}: {cpu_count_p}")
    print(f"  {'Logical Cores':<22}: {cpu_count_l}")
    print(f"  {'Frequency':<22}: {freq_str}")
    print(f"  {'CPU Usage':<22}: {cpu_percent:.1f}%  [{st}]")

    # Per-core usage
    per_core = psutil.cpu_percent(interval=0.5, percpu=True)
    print(f"\n  Per-Core Usage:")
    for i, c in enumerate(per_core):
        bar = "█" * int(c / 5) + "░" * (20 - int(c / 5))
        color = RED if c >= THRESHOLD_CPU else (YELLOW if c >= 60 else GREEN)
        print(f"    Core {i:<3}: {color}{bar}{RESET} {c:.1f}%")

    return {"cpu_usage_percent": cpu_percent, "cores_logical": cpu_count_l}

# ─────────────────────────────────────────────
#  3. MEMORY (RAM) HEALTH
# ─────────────────────────────────────────────
def get_memory_info():
    section("MEMORY (RAM) HEALTH")
    ram  = psutil.virtual_memory()
    swap = psutil.swap_memory()

    ram_st  = status(ram.percent,  THRESHOLD_RAM)
    swap_st = status(swap.percent, THRESHOLD_RAM)

    def fmt(b): return f"{b / (1024**3):.2f} GB"

    print(f"  {'Total RAM':<22}: {fmt(ram.total)}")
    print(f"  {'Used RAM':<22}: {fmt(ram.used)}")
    print(f"  {'Available RAM':<22}: {fmt(ram.available)}")
    print(f"  {'RAM Usage':<22}: {ram.percent:.1f}%  [{ram_st}]")
    print()
    print(f"  {'Swap Total':<22}: {fmt(swap.total)}")
    print(f"  {'Swap Used':<22}: {fmt(swap.used)}")
    print(f"  {'Swap Usage':<22}: {swap.percent:.1f}%  [{swap_st}]")

    return {"ram_usage_percent": ram.percent, "ram_available_gb": round(ram.available / (1024**3), 2)}

# ─────────────────────────────────────────────
#  4. DISK HEALTH
# ─────────────────────────────────────────────
def get_disk_info():
    section("DISK HEALTH")
    partitions = psutil.disk_partitions()
    disk_data  = []

    for p in partitions:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            st    = status(usage.percent, THRESHOLD_DISK)
            def fmt(b): return f"{b / (1024**3):.1f} GB"
            print(f"  Drive  : {BOLD}{p.device}{RESET}  ({p.fstype})")
            print(f"    Mount    : {p.mountpoint}")
            print(f"    Total    : {fmt(usage.total)}")
            print(f"    Used     : {fmt(usage.used)}")
            print(f"    Free     : {fmt(usage.free)}")
            print(f"    Usage    : {usage.percent:.1f}%  [{st}]")
            print()
            disk_data.append({"drive": p.device, "usage_percent": usage.percent})
        except PermissionError:
            print(f"  {p.device}: Permission denied")

    # Disk I/O
    io = psutil.disk_io_counters()
    if io:
        print(f"  {'Total Read':<22}: {io.read_bytes / (1024**3):.2f} GB")
        print(f"  {'Total Written':<22}: {io.write_bytes / (1024**3):.2f} GB")

    return disk_data

# ─────────────────────────────────────────────
#  5. NETWORK HEALTH
# ─────────────────────────────────────────────
def get_network_info():
    section("NETWORK HEALTH")
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "Unable to resolve"

    print(f"  {'Hostname':<22}: {hostname}")
    print(f"  {'Local IP':<22}: {local_ip}")

    # Network interfaces
    interfaces = psutil.net_if_addrs()
    print(f"\n  Network Interfaces:")
    for iface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                print(f"    {iface:<15}: {addr.address}")

    # Network I/O stats
    net_io = psutil.net_io_counters()
    print(f"\n  {'Bytes Sent':<22}: {net_io.bytes_sent / (1024**2):.2f} MB")
    print(f"  {'Bytes Received':<22}: {net_io.bytes_recv / (1024**2):.2f} MB")
    print(f"  {'Packets Sent':<22}: {net_io.packets_sent:,}")
    print(f"  {'Packets Received':<22}: {net_io.packets_recv:,}")
    print(f"  {'Errors (in/out)':<22}: {net_io.errin} / {net_io.errout}")
    print(f"  {'Dropped (in/out)':<22}: {net_io.dropin} / {net_io.dropout}")

    # Active connections count
    try:
        conns = psutil.net_connections()
        established = sum(1 for c in conns if c.status == "ESTABLISHED")
        print(f"  {'Active Connections':<22}: {established}")
    except Exception:
        pass

    return {"local_ip": local_ip, "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2)}

# ─────────────────────────────────────────────
#  6. TOP PROCESSES (by CPU & RAM)
# ─────────────────────────────────────────────
def get_top_processes():
    section("TOP PROCESSES")
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Top 5 by CPU
    top_cpu = sorted(procs, key=lambda x: x["cpu_percent"] or 0, reverse=True)[:5]
    print(f"  {'Top 5 by CPU Usage':}")
    print(f"  {'PID':<8} {'Name':<25} {'CPU%':<10} {'RAM%':<10} {'Status'}")
    print(f"  {'─'*65}")
    for p in top_cpu:
        print(f"  {p['pid']:<8} {(p['name'] or 'N/A')[:24]:<25} {p['cpu_percent']:<10.1f} {(p['memory_percent'] or 0):<10.1f} {p['status']}")

    print()

    # Top 5 by RAM
    top_ram = sorted(procs, key=lambda x: x["memory_percent"] or 0, reverse=True)[:5]
    print(f"  {'Top 5 by RAM Usage':}")
    print(f"  {'PID':<8} {'Name':<25} {'CPU%':<10} {'RAM%':<10} {'Status'}")
    print(f"  {'─'*65}")
    for p in top_ram:
        print(f"  {p['pid']:<8} {(p['name'] or 'N/A')[:24]:<25} {p['cpu_percent']:<10.1f} {(p['memory_percent'] or 0):<10.1f} {p['status']}")

# ─────────────────────────────────────────────
#  7. HEALTH SUMMARY & ALERTS
# ─────────────────────────────────────────────
def print_summary(cpu_data, mem_data, disk_data):
    section("HEALTH SUMMARY & ALERTS")
    alerts = []
    all_ok = True

    # CPU check
    cpu_pct = cpu_data.get("cpu_usage_percent", 0)
    if cpu_pct >= THRESHOLD_CPU:
        alerts.append(f"{RED}[ALERT] CPU usage is HIGH: {cpu_pct:.1f}% (threshold: {THRESHOLD_CPU}%){RESET}")
        all_ok = False
    else:
        print(f"  {GREEN}[OK]{RESET}  CPU Usage     : {cpu_pct:.1f}%")

    # RAM check
    ram_pct = mem_data.get("ram_usage_percent", 0)
    if ram_pct >= THRESHOLD_RAM:
        alerts.append(f"{RED}[ALERT] RAM usage is HIGH: {ram_pct:.1f}% (threshold: {THRESHOLD_RAM}%){RESET}")
        all_ok = False
    else:
        print(f"  {GREEN}[OK]{RESET}  RAM Usage     : {ram_pct:.1f}%")

    # Disk check
    for d in disk_data:
        if d["usage_percent"] >= THRESHOLD_DISK:
            alerts.append(f"{RED}[ALERT] Disk {d['drive']} is almost FULL: {d['usage_percent']:.1f}% (threshold: {THRESHOLD_DISK}%){RESET}")
            all_ok = False
        else:
            print(f"  {GREEN}[OK]{RESET}  Disk {d['drive']:<10}: {d['usage_percent']:.1f}%")

    if alerts:
        print()
        for a in alerts:
            print(f"  {a}")
    else:
        print(f"\n  {GREEN}{BOLD}✔  All systems are healthy. No critical issues found.{RESET}")

    return alerts

# ─────────────────────────────────────────────
#  8. SAVE REPORT TO FILE
# ─────────────────────────────────────────────
def save_report(sys_info, cpu_data, mem_data, disk_data, net_data, alerts):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"health_report_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("  SYSTEM HEALTH CHECK REPORT\n")
        f.write(f"  Generated : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"  Author    : Priyanshu Negi\n")
        f.write("=" * 60 + "\n\n")

        f.write("[SYSTEM INFO]\n")
        for k, v in sys_info.items():
            f.write(f"  {k:<18}: {v}\n")

        f.write("\n[CPU]\n")
        for k, v in cpu_data.items():
            f.write(f"  {k:<22}: {v}\n")

        f.write("\n[MEMORY]\n")
        for k, v in mem_data.items():
            f.write(f"  {k:<22}: {v}\n")

        f.write("\n[DISK]\n")
        for d in disk_data:
            f.write(f"  {d['drive']:<15}: {d['usage_percent']:.1f}%\n")

        f.write("\n[NETWORK]\n")
        for k, v in net_data.items():
            f.write(f"  {k:<22}: {v}\n")

        f.write("\n[ALERTS]\n")
        if alerts:
            for a in alerts:
                # strip ANSI colour codes for plain text file
                clean = a.replace(RED,"").replace(YELLOW,"").replace(GREEN,"").replace(RESET,"")
                f.write(f"  {clean}\n")
        else:
            f.write("  No alerts. All systems healthy.\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("  END OF REPORT\n")
        f.write("=" * 60 + "\n")

    print(f"\n  {GREEN}Report saved:{RESET} {filename}")
    return filename

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    print(f"\n{BOLD}{CYAN}{'═'*60}{RESET}")
    print(f"{BOLD}{CYAN}   SYSTEM HEALTH CHECK TOOL  |  Priyanshu Negi{RESET}")
    print(f"{BOLD}{CYAN}   {datetime.datetime.now().strftime('%A, %d %B %Y  %H:%M:%S')}{RESET}")
    print(f"{BOLD}{CYAN}{'═'*60}{RESET}\n")

    sys_info  = get_system_info()
    cpu_data  = get_cpu_info()
    mem_data  = get_memory_info()
    disk_data = get_disk_info()
    net_data  = get_network_info()
    get_top_processes()
    alerts    = print_summary(cpu_data, mem_data, disk_data)

    # Ask user if they want to save the report
    print()
    separator()
    save = input(f"  {BOLD}Save report to file? (y/n): {RESET}").strip().lower()
    if save == "y":
        save_report(sys_info, cpu_data, mem_data, disk_data, net_data, alerts)

    print(f"\n{CYAN}{'═'*60}{RESET}")
    print(f"{BOLD}  Health check complete.{RESET}")
    print(f"{CYAN}{'═'*60}{RESET}\n")

if __name__ == "__main__":
    main()