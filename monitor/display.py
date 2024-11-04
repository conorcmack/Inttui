import curses
import time
from datetime import datetime
from pathlib import Path
from .help_system import HelpSystem
from .network_map import NetworkMap
from .themes import Themes

class Dashboard:
    def __init__(self, monitor, ids, network_scanner):
        self.monitor = monitor
        self.ids = ids
        self.network_scanner = network_scanner
        self.screen = None
        self.current_view = 'system'
        self.help_system = HelpSystem()
        self.show_help = False
        self.network_info = None
        self.current_theme = Themes.NORD
        self.network_map = None
        
    def init_curses(self):
        self.screen = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        self.network_map = NetworkMap(self.screen, self.current_theme)
        
    def cleanup_curses(self):
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()
        
    def cycle_theme(self):
        themes = [Themes.NORD, Themes.TOKYO_NIGHT, Themes.CATPPUCCIN, 
                 Themes.GRUVBOX, Themes.DRACULA]
        current_index = themes.index(self.current_theme)
        self.current_theme = themes[(current_index + 1) % len(themes)]
        self.network_map = NetworkMap(self.screen, self.current_theme)

    def display_network_view(self, stats, security_findings):
        self.screen.clear()
        max_y, max_x = self.screen.getmaxyx()
        
        # Update network info if needed
        if not self.network_info:
            self.screen.addstr(0, 0, "Scanning network...", curses.color_pair(3))
            self.screen.refresh()
            self.network_info = self.network_scanner.scan_network()
            
        # Draw title
        title = "Network Map View"
        self.screen.addstr(0, (max_x - len(title)) // 2, title, curses.color_pair(1) | curses.A_BOLD)
        
        # Draw network map
        self.network_map.render_network_map(self.network_info)
        
        # Draw system statistics
        self.network_map.render_stats(stats, max_y - 5, 2)
        
        # Draw legend
        legend_x = max_x - 30
        self.screen.addstr(2, legend_x, "Legend:", curses.color_pair(1))
        self.screen.addstr(3, legend_x, "◆ Server", curses.color_pair(2))
        self.screen.addstr(4, legend_x, "○ Client", curses.color_pair(1))
        self.screen.addstr(5, legend_x, "□ Router", curses.color_pair(3))
        self.screen.addstr(6, legend_x, "▲ Firewall", curses.color_pair(4))
        self.screen.addstr(7, legend_x, "✕ Blocked", curses.color_pair(5))
        
        # Draw theme info
        theme_info = f"Theme: {self.current_theme.__class__.__name__} (Press 't' to change)"
        self.screen.addstr(max_y - 1, 2, theme_info, curses.color_pair(1))
        
    def run(self):
        try:
            self.init_curses()
            while True:
                stats = self.monitor.collect_stats()
                security_findings = self.ids.analyze(stats)
                
                if self.show_help:
                    self.display_help()
                elif self.current_view == 'network':
                    self.display_network_view(stats, security_findings)
                elif self.current_view == 'system':
                    self.display_system_stats(stats, security_findings)
                elif self.current_view == 'security':
                    self.display_security_stats(security_findings)
                elif self.current_view == 'control':
                    self.display_control_screen(stats, security_findings)
                
                self.screen.refresh()
                
                # Handle input
                self.screen.timeout(1000)
                key = self.screen.getch()
                if key == ord('q'):
                    break
                elif key == ord('h'):
                    self.show_help = not self.show_help
                elif key == ord('n'):
                    self.current_view = 'network'
                elif key == ord('s'):
                    self.current_view = 'security'
                elif key == ord('m'):
                    self.current_view = 'system'
                elif key == ord('c'):
                    self.current_view = 'control'
                elif key == ord('t'):
                    self.cycle_theme()
                elif key == ord('r'):
                    self.network_info = None  # Force network rescan
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup_curses()