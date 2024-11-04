import psutil
import logging
from datetime import datetime
import json
from pathlib import Path

class ProcessController:
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.thresholds_file = self.config_dir / "process_thresholds.json"
        self.load_thresholds()
        
    def load_thresholds(self):
        if self.thresholds_file.exists():
            with open(self.thresholds_file, 'r') as f:
                self.thresholds = json.load(f)
        else:
            self.thresholds = {
                'cpu_percent': 80.0,
                'memory_percent': 75.0,
                'network_connections': 100
            }
            self.save_thresholds()
            
    def save_thresholds(self):
        with open(self.thresholds_file, 'w') as f:
            json.dump(self.thresholds, f)
            
    def set_threshold(self, resource, value):
        if resource in self.thresholds:
            self.thresholds[resource] = float(value)
            self.save_thresholds()
            return True, f"Threshold for {resource} set to {value}"
        return False, f"Invalid resource: {resource}"
        
    def get_resource_hogs(self):
        hogs = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'connections']):
            try:
                info = proc.info
                if (info['cpu_percent'] > self.thresholds['cpu_percent'] or
                    info['memory_percent'] > self.thresholds['memory_percent'] or
                    len(proc.connections()) > self.thresholds['network_connections']):
                    
                    hogs.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'cpu_percent': info['cpu_percent'],
                        'memory_percent': info['memory_percent'],
                        'connections': len(proc.connections())
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return hogs
        
    def terminate_process(self, pid):
        try:
            process = psutil.Process(pid)
            process.terminate()
            return True, f"Process {pid} terminated successfully"
        except psutil.NoSuchProcess:
            return False, f"Process {pid} not found"
        except psutil.AccessDenied:
            return False, f"Access denied to terminate process {pid}"