import os
import subprocess
from flask import Flask, send_from_directory, request, Response
from datetime import datetime

class WebServer:
    def __init__(self, state, socketio):
        self.state = state
        self.socketio = socketio
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.before_request
        def security_and_logging():
            # DDoS Protection Check
            if not self.state.ddos_protector.is_allowed(request.remote_addr):
                self.state.security_alert.trigger_alert(f"DDoS Block: IP {request.remote_addr} throttled")
                return "Forbidden: Too many requests", 403

            # Security Alert Analysis
            self.state.security_alert.analyze_request(request)

            # Logging Traffic
            log_entry = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'method': request.method,
                'path': request.path,
                'ip': request.remote_addr,
                'status': 200
            }
            self.state.logs.append(log_entry)
            self.socketio.emit('new_log', log_entry, namespace='/panel')

        @self.app.route('/')
        @self.app.route('/<path:path>')
        def serve_files(path='index.html'):
            full_path = os.path.join(self.state.project_path, path)
            
            # Auto-index handling
            if os.path.isdir(full_path):
                full_path = os.path.join(full_path, 'index.html')
            
            # Handle PHP files
            if path.endswith('.php') or (not path and os.path.exists(os.path.join(self.state.project_path, 'index.php'))):
                target = full_path if not full_path.endswith('/') else os.path.join(full_path, 'index.php')
                return self.handle_php(target)
            
            return send_from_directory(self.state.project_path, path if not os.path.isdir(full_path) else 'index.html')

    def handle_php(self, script_path):
        if not os.path.exists(script_path):
            return "PHP File not found", 404
        
        try:
            # Execute PHP via CLI
            process = subprocess.Popen(
                ['php', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ
            )
            stdout, stderr = process.communicate()
            if stderr:
                return f"<pre style='color:red'>PHP Error:\n{stderr}</pre>", 500
            return Response(stdout, mimetype='text/html')
        except FileNotFoundError:
            return "Error: PHP is not installed on this system's PATH.", 500
        except Exception as e:
            return f"PHP Execution Error: {str(e)}", 500

    def run(self, port):
        print(f"[WEB] Starting {'HTTPS' if self.state.use_https else 'HTTP'} server on port {port}...")
        ssl_ctx = 'adhoc' if self.state.use_https else None
        self.app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, ssl_context=ssl_ctx)
