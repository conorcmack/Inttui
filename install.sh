#!/bin/bash

# Create installation directory
sudo mkdir -p /opt/system-monitor
sudo cp -r monitor/ main.py monitor_service.py /opt/system-monitor/

# Set up systemd service
sudo cp system-monitor.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/system-monitor.service

# Create log directory
sudo mkdir -p /var/log/system-monitor
sudo chmod 755 /var/log/system-monitor

# Set proper permissions
sudo chmod +x /opt/system-monitor/monitor_service.py
sudo chmod +x /opt/system-monitor/main.py

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable system-monitor
sudo systemctl start system-monitor

echo "Installation complete. Service started."
echo "View live monitor with: python3 /opt/system-monitor/main.py"
echo "Check service status with: sudo systemctl status system-monitor"