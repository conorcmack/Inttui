import subprocess
import psutil
from pathlib import Path
import json
import logging
from datetime import datetime

class PortManager:
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.blocked_ports_file = self.config_dir / "blocked_ports.json"
        self.load_blocked_ports()
        
    def load_blocked_ports(self):
        if self.blocked_ports_file.exists():
            with open(self.blocked_ports_file, 'r') as f:
                self.blocked_ports = json.load(f)
        else:
            self.blocked_ports = []
            self.save_blocked_ports()
            
    def save_blocked_ports(self):
        with open(self.blocked_ports_file, 'w') as f:
            json.dump(self.blocked_ports, f)
            
    def block_port(self, port, protocol='tcp'):
        try:
            if port not in self.blocked_ports:
                # Block incoming
                subprocess.run([
                    'sudo', 'iptables', '-A', 'INPUT', 
                    '-p', protocol, '--dport', str(port), 
                    '-j', 'DROP'
                ], check=True)
                
                # Block outgoing
                subprocess.run([
                    'sudo', 'iptables', '-A', 'OUTPUT', 
                    '-p', protocol, '--dport', str(port), 
                    '-j', 'DROP'
                ], check=True)
                
                self.blocked_ports.append(port)
                self.save_blocked_ports()
                return True, f"Port {port} blocked successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to block port {port}: {str(e)}"
            
    def unblock_port(self, port, protocol='tcp'):
        try:
            if port in self.blocked_ports:
                # Unblock incoming
                subprocess.run([
                    'sudo', 'iptables', '-D', 'INPUT', 
                    '-p', protocol, '--dport', str(port), 
                    '-j', 'DROP'
                ], check=True)
                
                # Unblock outgoing
                subprocess.run([
                    'sudo', 'iptables', '-D', 'OUTPUT', 
                    '-p', protocol, '--dport', str(port), 
                    '-j', 'DROP'
                ], check=True)
                
                self.blocked_ports.remove(port)
                self.save_blocked_ports()
                return True, f"Port {port} unblocked successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to unblock port {port}: {str(e)}"
            
    def get_blocked_ports(self):
        return self.blocked_ports