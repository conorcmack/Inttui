#!/usr/bin/env python3
from monitor.system_stats import SystemMonitor
from monitor.display import Dashboard
from monitor.ids import IntrusionDetector
from monitor.network_scanner import NetworkScanner

def main():
    monitor = SystemMonitor()
    ids = IntrusionDetector()
    network_scanner = NetworkScanner()
    dashboard = Dashboard(monitor, ids, network_scanner)
    dashboard.run()

if __name__ == "__main__":
    main()