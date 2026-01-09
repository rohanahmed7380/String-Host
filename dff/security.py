import time
from collections import deque

class SecurityAlert:
    def __init__(self, state, socketio):
        self.state = state
        self.socketio = socketio
        self.alerts = []
        self.blacklist = set()

    def analyze_request(self, request):
        if request.remote_addr in self.blacklist:
            return False

        # WAF - Basic Malicious Pattern Detection
        malicious_patterns = [
            '../', '/etc/passwd', 'wp-config', '.env', '.git',
            'select ', 'union ', 'insert ', 'drop ', # SQLi
            '<script>', 'alert(', 'onerror=' # XSS
        ]
        
        path = request.path.lower()
        query = request.query_string.decode().lower()

        for pattern in malicious_patterns:
            if pattern in path or pattern in query:
                self.trigger_alert(f"BLOCKED ATTACK: {pattern} from {request.remote_addr}", critical=True)
                self.blacklist.add(request.remote_addr)
                return False
        return True

    def trigger_alert(self, message, critical=False):
        alert_data = {
            'time': time.strftime("%H:%M:%S"),
            'message': message,
            'type': 'CRITICAL' if critical else 'WARNING'
        }
        self.alerts.append(alert_data)
        self.socketio.emit('security_alert', alert_data, namespace='/panel')
        print(f"[{alert_data['type']}] {message}")

class DDoSProtection:
    def __init__(self, security_alert, threshold=40, window=10):
        self.security_alert = security_alert
        self.threshold = threshold 
        self.window = window 
        self.history = {} 

    def is_allowed(self, ip):
        if ip in self.security_alert.blacklist:
            return False

        now = time.time()
        if ip not in self.history:
            self.history[ip] = deque()
        
        # Remove expired timestamps
        while self.history[ip] and now - self.history[ip][0] > self.window:
            self.history[ip].popleft()
            
        if len(self.history[ip]) > self.threshold:
            self.security_alert.trigger_alert(f"DDoS PROTECT: IP {ip} Blacklisted (High Volume)", critical=True)
            self.security_alert.blacklist.add(ip)
            return False
            
        self.history[ip].append(now)
        return True
