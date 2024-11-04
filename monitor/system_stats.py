import os
import psutil
import time
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.stats_history = []
        
    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self):
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent
        }
    
    def get_network_connections(self):
        connections = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                connections.append({
                    'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}",
                    'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A',
                    'status': conn.status,
                    'pid': conn.pid
                })
        return connections
    
    def get_process_list(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
    
    def collect_stats(self):
        stats = {
            'timestamp': datetime.now().isoformat(),
            'cpu': self.get_cpu_usage(),
            'memory': self.get_memory_usage(),
            'connections': self.get_network_connections(),
            'processes': self.get_process_list()
        }
        self.stats_history.append(stats)
        return stats