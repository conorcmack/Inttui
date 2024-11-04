#!/usr/bin/env python3
import sys
import time
import daemon
import lockfile
from pathlib import Path
from monitor.system_stats import SystemMonitor
from monitor.ids import IntrusionDetector

def run_monitor():
    monitor = SystemMonitor()
    ids = IntrusionDetector()
    
    while True:
        try:
            stats = monitor.collect_stats()
            security_findings = ids.analyze(stats)
            time.sleep(60)  # Check every minute
        except Exception as e:
            with open("monitor_error.log", "a") as f:
                f.write(f"{time.ctime()}: Error - {str(e)}\n")
            time.sleep(300)  # Wait 5 minutes on error

def start_daemon():
    work_dir = Path.home() / ".system_monitor"
    work_dir.mkdir(exist_ok=True)
    
    with daemon.DaemonContext(
        working_directory=str(work_dir),
        pidfile=lockfile.FileLock("/var/run/system_monitor.pid"),
        umask=0o002,
    ):
        run_monitor()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        start_daemon()
    else:
        run_monitor()