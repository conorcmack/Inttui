import curses
import math
from .themes import Themes

class NetworkMap:
    def __init__(self, screen, theme=Themes.NORD):
        self.screen = screen
        self.theme = theme
        self.icons = {
            'server': '◆',
            'client': '○',
            'router': '□',
            'firewall': '▲',
            'blocked': '✕',
            'suspicious': '⚠',
            'connection': '─│┌┐└┘├┤┬┴┼'
        }
        self.init_colors()
        
    def init_colors(self):
        # Initialize color pairs
        curses.init_pair(1, *self._rgb_to_curses(self.theme['fg_primary'], self.theme['bg_primary']))
        curses.init_pair(2, *self._rgb_to_curses(self.theme['accent1'], self.theme['bg_primary']))
        curses.init_pair(3, *self._rgb_to_curses(self.theme['accent2'], self.theme['bg_primary']))
        curses.init_pair(4, *self._rgb_to_curses(self.theme['warning'], self.theme['bg_primary']))
        curses.init_pair(5, *self._rgb_to_curses(self.theme['error'], self.theme['bg_primary']))
        curses.init_pair(6, *self._rgb_to_curses(self.theme['success'], self.theme['bg_primary']))
        
    def _rgb_to_curses(self, fg, bg):
        # Convert RGB colors to closest curses colors
        def _closest_color(r, g, b):
            colors = [
                (0, 0, 0),        # BLACK
                (1000, 0, 0),     # RED
                (0, 1000, 0),     # GREEN
                (1000, 1000, 0),  # YELLOW
                (0, 0, 1000),     # BLUE
                (1000, 0, 1000),  # MAGENTA
                (0, 1000, 1000),  # CYAN
                (1000, 1000, 1000)# WHITE
            ]
            distances = []
            for i, c in enumerate(colors):
                d = math.sqrt((r-c[0])**2 + (g-c[1])**2 + (b-c[2])**2)
                distances.append((d, i))
            return min(distances)[1]
            
        fg_color = _closest_color(*fg)
        bg_color = _closest_color(*bg)
        return fg_color, bg_color
        
    def draw_connection(self, start_y, start_x, end_y, end_x, style=1):
        # Draw connection lines between nodes
        if start_y == end_y:
            # Horizontal line
            for x in range(min(start_x, end_x), max(start_x, end_x) + 1):
                self.screen.addch(start_y, x, self.icons['connection'][0], curses.color_pair(style))
        elif start_x == end_x:
            # Vertical line
            for y in range(min(start_y, end_y), max(start_y, end_y) + 1):
                self.screen.addch(y, start_x, self.icons['connection'][1], curses.color_pair(style))
        else:
            # Draw corner
            mid_y = (start_y + end_y) // 2
            self.draw_connection(start_y, start_x, mid_y, start_x, style)
            self.draw_connection(mid_y, start_x, mid_y, end_x, style)
            self.draw_connection(mid_y, end_x, end_y, end_x, style)
            
    def draw_node(self, y, x, node_type, label, style=1):
        # Draw node icon and label
        self.screen.addch(y, x, self.icons[node_type], curses.color_pair(style))
        self.screen.addstr(y, x + 2, label[:20], curses.color_pair(style))
        
    def draw_progress_bar(self, y, x, width, percentage, style=1):
        # Draw a progress bar
        filled = int(width * percentage / 100)
        self.screen.addstr(y, x, '█' * filled + '░' * (width - filled), curses.color_pair(style))
        self.screen.addstr(y, x + width + 1, f"{percentage:3.0f}%", curses.color_pair(style))
        
    def render_network_map(self, network_data):
        max_y, max_x = self.screen.getmaxyx()
        center_y, center_x = max_y // 2, max_x // 2
        
        # Draw local system at center
        self.draw_node(center_y, center_x, 'server', 'Local System', 2)
        
        # Calculate positions for connected hosts
        radius = min(max_y // 4, max_x // 4)
        hosts = network_data['hosts']
        for i, host in enumerate(hosts):
            angle = (2 * math.pi * i) / len(hosts)
            host_y = center_y + int(radius * math.sin(angle))
            host_x = center_x + int(radius * math.cos(angle) * 2)
            
            # Determine node type and style based on host properties
            node_type = 'client'
            style = 1
            
            if any(p in [22, 3306, 5432] for p in host['open_ports']):
                node_type = 'server'
                style = 3
            if any(p in [80, 443, 8080] for p in host['open_ports']):
                node_type = 'router'
                style = 2
                
            # Draw host node
            self.draw_node(host_y, host_x, node_type, f"{host['ip']}", style)
            
            # Draw connection line
            connection_style = 1
            if node_type == 'server':
                connection_style = 3
            self.draw_connection(center_y, center_x, host_y, host_x, connection_style)
            
            # Draw port information
            port_y = host_y + 1
            port_info = f"Ports: {', '.join(map(str, host['open_ports']))}"
            self.screen.addstr(port_y, host_x, port_info[:20], curses.color_pair(style))
            
    def render_stats(self, stats, y, x):
        # Draw system statistics with progress bars
        self.screen.addstr(y, x, "System Statistics:", curses.color_pair(1))
        
        # CPU Usage
        self.screen.addstr(y + 1, x, "CPU: ", curses.color_pair(1))
        self.draw_progress_bar(y + 1, x + 5, 20, stats['cpu'], 
                             6 if stats['cpu'] < 70 else 4 if stats['cpu'] < 90 else 5)
        
        # Memory Usage
        mem = stats['memory']['percent']
        self.screen.addstr(y + 2, x, "MEM: ", curses.color_pair(1))
        self.draw_progress_bar(y + 2, x + 5, 20, mem,
                             6 if mem < 70 else 4 if mem < 90 else 5)