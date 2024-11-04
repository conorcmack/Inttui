import os
import socket
import subprocess
import re
from datetime import datetime
import json
from pathlib import Path
from .port_manager import PortManager
from .process_control import ProcessController

class IntrusionDetector:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.port_manager = PortManager()
        self.process_controller = ProcessController()
        self.suspicious_patterns = [
            r"(?i)sqlmap",
            r"(?i)nikto",
            r"(?i)nmap",
            r"\.(php|asp|aspx|jsp)\?",
            r"(?i)(union|select|insert|drop|delete)\s+.*",
        ]
        
    def check_failed_logins(self):
        failed_attempts = []
        try:
            with open("/var/log/auth.log", "r") as f:
                for line in f:
                    if "Failed password" in line:
                        failed_attempts.append(line.strip())
        except Exception as e:
            return [f"Error reading auth.log: {str(e)}"]
        return failed_attempts[-10:]  # Return last 10 failed attempts
        
    def scan_open_ports(self):
        open_ports = []
        for port in [20, 21, 22, 23, 25, 53, 80, 443, 3306, 5432]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        return open_ports
        
    def check_suspicious_connections(self, connections):
        suspicious = []
        for conn in connections:
            # Check for common suspicious ports
            remote_port = int(conn['remote_addr'].split(':')[1]) if ':' in conn['remote_addr'] else 0
            if remote_port in [22, 3306, 5432]:
                suspicious.append({
                    'type': 'suspicious_port',
                    'details': conn
                })
        return suspicious
        
    def log_event(self, event_type, details):
        timestamp = datetime.now().isoformat()
        log_file = self.log_dir / f"ids_{datetime.now().strftime('%Y%m%d')}.log"
        
        event = {
            'timestamp': timestamp,
            'type': event_type,
            'details': details
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
            
    def analyze(self, system_stats):
        findings = {
            'timestamp': datetime.now().isoformat(),
            'alerts': [],
            'open_ports': self.scan_open_ports(),
            'failed_logins': self.check_failed_logins(),
            'suspicious_connections': self.check_suspicious_connections(system_stats['connections']),
            'blocked_ports': self.port_manager.get_blocked_ports(),
            'resource_hogs': self.process_controller.get_resource_hogs()
        }
        
        # Log significant findings
        if findings['suspicious_connections']:
            self.log_event('suspicious_connections', findings['suspicious_connections'])
        if findings['failed_logins']:
            self.log_event('failed_logins', findings['failed_logins'])
        if findings['resource_hogs']:
            self.log_event('resource_hogs', findings['resource_hogs'])
            
        return findings
        
    def block_port(self, port, protocol='tcp'):
        return self.port_manager.block_port(port, protocol)
        
    def unblock_port(self, port, protocol='tcp'):
        return self.port_manager.unblock_port(port, protocol)
        
    def terminate_process(self, pid):
        return self.process_controller.terminate_process(pid)
        
    def set_resource_threshold(self, resource, value):
        return self.process_controller.set_threshold(resource, value)