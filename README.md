# 🖥️ System Health Check Tool

A Python-based real-time system monitoring and health reporting tool built for IT Support and Helpdesk use cases. It tracks CPU, RAM, disk, and network metrics, flags issues with colour-coded alerts, and generates timestamped reports for IT documentation.

---

## 📌 Project Overview

| Field        | Details                            |
|--------------|------------------------------------|
| **Author**   | Priyanshu Negi                     |
| **Language** | Python 3.x                         |
| **Library**  | psutil                             |
| **Domain**   | IT Support / System Administration |
| **Type**     | CLI Tool                           |
| **GitHub**   | [igpriyanshunegi/system-health-check-tool](https://github.com/igpriyanshunegi/system-health-check-tool) |

---

## ⚙️ Features

- ✅ **System Information** — OS, hostname, processor, uptime, boot time
- ✅ **CPU Health** — usage %, per-core visual bar chart, clock frequency
- ✅ **RAM & Swap Health** — total, used, available memory with usage %
- ✅ **Disk Health** — all drives, usage %, read/write I/O stats
- ✅ **Network Health** — IP address, interfaces, bytes sent/received, errors, active connections
- ✅ **Top Processes** — top 5 processes by CPU and RAM usage
- ✅ **Automated Alerts** — flags CPU > 80%, RAM > 85%, Disk > 90%
- ✅ **Report Generation** — saves a timestamped `.txt` health report for IT documentation

---

## 🚨 Alert Thresholds

| Metric     | Warning Threshold |
|------------|------------------|
| CPU Usage  | > 80%            |
| RAM Usage  | > 85%            |
| Disk Usage | > 90%            |

---

## 📥 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/igpriyanshunegi/system-health-check-tool.git
```

### 2. Navigate into the folder
```bash
cd system-health-check-tool
```

### 3. Install dependency
```bash
pip install psutil
```

---

## ▶️ How to Run

```bash
python system_health_check.py
```

At the end, you will be prompted:
```
Save report to file? (y/n):
```
Press `y` to save a timestamped report like `health_report_20260617_143025.txt`.

---

## 📊 Sample Output

```
════════════════════════════════════════════════════════════
   SYSTEM HEALTH CHECK TOOL  |  Priyanshu Negi
   Wednesday, 17 June 2026  14:30:25
════════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────
  SYSTEM INFORMATION
────────────────────────────────────────────────────────────
  Hostname          : DESKTOP-XYZ
  OS                : Windows 10
  Python Version    : 3.11.0
  System Uptime     : 3:45:12

────────────────────────────────────────────────────────────
  CPU HEALTH
────────────────────────────────────────────────────────────
  Physical Cores        : 4
  Logical Cores         : 8
  CPU Usage             : 23.5%  [OK]

  Per-Core Usage:
    Core 0  : ████░░░░░░░░░░░░░░░░ 23.1%
    Core 1  : ██░░░░░░░░░░░░░░░░░░ 11.4%

────────────────────────────────────────────────────────────
  HEALTH SUMMARY & ALERTS
────────────────────────────────────────────────────────────
  [OK]  CPU Usage     : 23.5%
  [OK]  RAM Usage     : 61.2%
  [OK]  Disk C:\      : 54.3%

  ✔  All systems are healthy. No critical issues found.
```

---

## 📁 Project Structure

```
system-health-check-tool/
│
├── system_health_check.py   # Main script
├── health_report_*.txt      # Auto-generated reports (created on run)
└── README.md                # Project documentation
```

---

## 💡 Use Cases

- IT Support engineers running quick system diagnostics
- Helpdesk staff documenting system state before/after troubleshooting
- System administrators monitoring multiple machines
- Learning Python system monitoring with psutil

---


## 🔗 Connect

- **GitHub** : [github.com/igpriyanshunegi](https://github.com/igpriyanshunegi)
- **LinkedIn** : [linkedin.com/in/igpriyanshunegi](https://www.linkedin.com/in/igpriyanshunegi)
- **Email** : priyanshun898@gmail.com
