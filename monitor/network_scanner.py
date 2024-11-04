import socket
import subprocess
import ipaddress
from concurrent.futures import ThreadPoolExecutor
import netifaces
import json
from pathlib import Path

class NetworkScanner:
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.scan_results_file = self.config_dir / "network_scan.json"
        
    def get_interfaces(self):
        interfaces = {}
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                interfaces[iface] = {
                    'ip': addrs[netifaces.AF_INET][0]['addr'],
                    'netmask': addrs[netifaces.AF_INET][0]['netmask']
                }
        return interfaces
        
    def scan_port(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((str(ip), port))
        sock.close()
        return port if result == 0 else None
        
    def scan_host(self, ip):
        common_ports = [20, 21, 22, 23, 25, 53, 80, 443, 3306, 5432, 8080]
        open_ports = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            port_results = executor.map(lambda p: self.scan_port(ip, p), common_ports)
            open_ports = [p for p in port_results if p is not None]
            
        if open_ports:
            return {
                'ip': str(ip),
                'hostname': self.get_hostname(str(ip)),
                'open_ports': open_ports
            }
        return None
        
    def get_hostname(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror):
            return "Unknown"
            
    def scan_network(self):
        scan_results = {
            'interfaces': self.get_interfaces(),
            'hosts': []
        }
        
        for iface, info in scan_results['interfaces'].items():
            network = ipaddress.IPv4Network(
                f"{info['ip']}/{info['netmask']}", strict=False
            )
            
            with ThreadPoolExecutor(max_workers=20) as executor:
                host_results = executor.map(self.scan_host, network.hosts())
                scan_results['hosts'].extend([h for h in host_results if h is not None])
                
        with open(self.scan_results_file, 'w') as f:
            json.dump(scan_results, f)
            
        return scan_results