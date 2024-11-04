"""Help system for the intrusion detection monitor"""

class HelpSystem:
    def __init__(self):
        self.help_topics = {
            'general': {
                'title': 'General Controls',
                'content': [
                    "'q' - Quit application",
                    "'m' - Main system view",
                    "'s' - Security view",
                    "'c' - Control panel",
                    "'h' - Toggle help view",
                    "'i' - Installation options"
                ]
            },
            'security': {
                'title': 'Security Features',
                'content': [
                    "- Real-time port monitoring",
                    "- Failed login detection",
                    "- Suspicious connection tracking",
                    "- Resource usage monitoring",
                    "- Port blocking/unblocking",
                    "- Process termination"
                ]
            },
            'control': {
                'title': 'Control Panel',
                'content': [
                    "'b' - Block a port",
                    "'u' - Unblock a port",
                    "'t' - Terminate process",
                    "'r' - Set resource thresholds"
                ]
            },
            'monitoring': {
                'title': 'System Monitoring',
                'content': [
                    "- CPU and memory usage",
                    "- Network connections",
                    "- Open ports",
                    "- Process resource usage",
                    "- System logs analysis"
                ]
            }
        }