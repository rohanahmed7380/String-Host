import os
import sys
import threading
import time
import socket
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import click

# Import our modular components
from dff.server import WebServer
from dff.dns import DNSServer
from dff.security import SecurityAlert, DDoSProtection

class StringState:
    def __init__(self):
        self.logs = []
        self.target_domains = [] # List of domains
        self.project_path = ""
        self.use_https = False
        self.local_ip = self.get_local_ip()
        self.security_alert = None
        self.ddos_protector = None

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            # Fallback for offline mode
            return socket.gethostbyname(socket.gethostname())

state = StringState()

# --- Admin Panel ---
panel_app = Flask(__name__)
socketio = SocketIO(panel_app, cors_allowed_origins="*")

@panel_app.route('/')
def index():
    return render_template('index.html', 
                          domains=state.target_domains, 
                          ip=state.local_ip, 
                          alerts=state.security_alert.alerts if state.security_alert else [])

@socketio.on('connect', namespace='/panel')
def on_connect():
    emit('init_logs', state.logs, namespace='/panel')
    if state.security_alert:
        emit('init_alerts', state.security_alert.alerts, namespace='/panel')

@socketio.on('refresh_traffic', namespace='/panel')
def refresh_traffic():
    state.logs = []
    emit('init_logs', [], namespace='/panel')

# --- CLI Execution ---
@click.command()
@click.option('--path', prompt='Project path', help='Project folder with index.html/php')
@click.option('--domains', prompt='Domains (comma separated, e.g. site.local, myapp.st, business.pk)', help='Custom domains for hosting')
@click.option('--webport', default=443, help='Web server port (default 443 for HTTPS)')
@click.option('--panelport', default=1947, help='Admin panel port')
@click.option('--https/--no-https', default=True, help='Enable/Disable HTTPS (default: Enabled)')
def start(path, domains, webport, panelport, https):
    """String: Advanced Modular Terminal Hosting Tool"""
    
    # Check for Admin rights immediately
    is_admin = False
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        pass

    state.project_path = os.path.abspath(path)
    state.use_https = https
    # Parse multiple domains
    state.target_domains = [d.strip() for d in domains.split(',')]

    if not is_admin:
        print("\n" + "!"*60)
        print(" [WARNING] RUNNING WITHOUT ADMINISTRATOR RIGHTS ".center(60, "!"))
        print(" The domain system WILL NOT work correctly. ".center(60))
        print(" Please right-click your Terminal/CMD and 'Run as Admin' ".center(60))
        print("!"*60 + "\n")

    if not os.path.exists(state.project_path):
        print(f"[ERROR] Path not found: {state.project_path}")
        return

    # Initialize Security
    state.security_alert = SecurityAlert(state, socketio)
    state.ddos_protector = DDoSProtection(state.security_alert)

    # Initialize Servers
    web_server = WebServer(state, socketio)
    dns_server = DNSServer(state)

    # SECURE HEADERS for Panel
    @panel_app.after_request
    def add_secure_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    # Apply local domain mapping immediately
    dns_server.update_hosts(state.target_domains, "127.0.0.1")

    # Threads
    threads = [
        threading.Thread(target=dns_server.run, daemon=True),
        threading.Thread(target=lambda: web_server.run(webport), daemon=True),
        threading.Thread(target=lambda: socketio.run(panel_app, host='0.0.0.0', port=panelport, debug=False, use_reloader=False), daemon=True)
    ]

    for t in threads:
        t.start()

    print("\n" + "█"*50)
    print(" STRING MODULAR SERVER ACTIVE ".center(50, "█"))
    print(f" PROTOCOL: {'HTTPS (Self-signed)' if state.use_https else 'HTTP'}")
    print(f" DOMAINS:  {', '.join(state.target_domains)}")
    print(f" LOCAL IP: {state.local_ip}")
    print(f" PANEL:    http://localhost:{panelport}")
    print(f" MODE:     Multi-Domain & Multi-TLD (.pk, .com, .local)")
    print("█"*50)
    print("\n[HINT] To make this accessible to other devices, ensure Port 53 is free.")
    print("[HINT] Run 'net stop SharedAccess' in Admin CMD to free up DNS port.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] String is stopping...")
        if 'dns_server' in locals():
            dns_server.cleanup()

if __name__ == '__main__':
    start()
