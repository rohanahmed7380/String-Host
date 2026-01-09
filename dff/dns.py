import socket
import os
import subprocess
from dnslib import DNSRecord, QTYPE, RR, A

class DNSServer:
    def __init__(self, state):
        self.state = state
        self.hosts_path = r"C:\Windows\System32\drivers\etc\hosts"

    def update_hosts(self, domains, ip):
        """Adds or updates multiple domains in the Windows hosts file."""
        print(f"[DNS] Mapping domains to {ip} in hosts file...")
        try:
            if not os.path.exists(self.hosts_path):
                print("[DNS ERROR] Hosts file not found.")
                return

            with open(self.hosts_path, 'r') as f:
                content = f.read()
            
            lines = content.splitlines()
            # Remove any existing lines containing our domains
            new_lines = [line for line in lines if not any(dom in line for dom in domains) or line.strip().startswith('#')]
            
            for dom in domains:
                new_lines.append(f"{ip} {dom}")
            
            with open(self.hosts_path, 'w') as f:
                f.write('\n'.join(new_lines) + '\n')
            
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
            print(f"[DNS] SUCCESS: Local system now recognizes: {', '.join(domains)}")
            
        except PermissionError:
            print("\n" + "!"*60)
            print(" [CRITICAL] ACCESS DENIED: TERMINAL NOT IN ADMIN MODE ".center(60, "!"))
            print(" String cannot map the domains without Administrator rights. ".center(60))
            print(" PLEASE RESTART THE TERMINAL AS ADMINISTRATOR! ".center(60))
            print("!"*60 + "\n")
        except Exception as e:
            print(f"[DNS ERROR] Failed to update hosts: {e}")

    def resolve(self, request):
        reply = request.reply()
        qname = str(request.q.qname).rstrip('.')
        
        # Match any of the target domains
        is_target = False
        for dom in self.state.target_domains:
            if qname == dom or qname.endswith("." + dom):
                is_target = True
                break

        if is_target:
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(self.state.local_ip), ttl=60))
            print(f"[DNS] Network Query: {qname} -> {self.state.local_ip}")
        
        return reply

    def cleanup(self):
        """Removes the domain entries from the hosts file."""
        try:
            with open(self.hosts_path, 'r') as f:
                content = f.read()
            
            lines = content.splitlines()
            new_lines = [line for line in lines if not any(dom in line for dom in self.state.target_domains)]
            
            with open(self.hosts_path, 'w') as f:
                f.write('\n'.join(new_lines) + '\n')
            
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
            print(f"[DNS] Cleanup complete: Removed domains from hosts.")
        except:
            pass

    def run(self):
        print(f"[DNS] Starting network-wide DNS listener...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('', 53))
            while True:
                data, addr = sock.recvfrom(512)
                dns_req = DNSRecord.parse(data)
                dns_rep = self.resolve(dns_req)
                sock.sendto(dns_rep.pack(), addr)
        except PermissionError:
            pass
        except OSError as e:
            if e.errno == 10048:
                print(f"[DNS INFO] Network DNS (Port 53) is busy. Only this device will resolve domains.")
                print(f"[DNS INFO] Suggestion: Stop 'Internet Connection Sharing' in Windows Services.")
            else:
                print(f"[DNS CRITICAL] {e}")
        except Exception as e:
            print(f"[DNS CRITICAL] {e}")
