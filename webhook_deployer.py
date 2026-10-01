import hashlib
import hmac
import json
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 9000
SECRET = ""  # Set webhook secret here if wanted
APP_DIR = "d:/simple-python-ci-cd"
IMAGE_NAME = "simple-python-app"
CONTAINER_NAME = "simple-python-app"


def run_command(cmd, cwd=APP_DIR):
    print(f">> RUN: {cmd}")
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAIL ({res.returncode}): {res.stderr.strip()}")
        return False
    print(f"OK: {res.stdout.strip()}")
    return True


def deploy_task():
    print("\n[+] START AUTO DEPLOY")

    # 1. Fetch latest main
    if not run_command("git fetch origin main"):
        print("[-] Fetch failed. Stop.")
        return
    run_command("git reset --hard origin/main")

    # 2. Run unit tests before touch docker
    print("[+] Test code...")
    if not run_command("python -m pytest test_app.py"):
        print("[-] TESTS FAILED! Abort deploy. Container keep running old good code.")
        return

    # 3. Build new docker image
    print("[+] Build docker...")
    if not run_command(f"docker build -t {IMAGE_NAME}:latest ."):
        print("[-] Build failed. Stop.")
        return

    # 4. Stop and remove old container
    print("[+] Stop old container...")
    run_command(f"docker stop {CONTAINER_NAME}")
    run_command(f"docker rm {CONTAINER_NAME}")

    # 5. Run new container
    print("[+] Start new container...")
    if run_command(f"docker run -d -p 8080:8080 --name {CONTAINER_NAME} {IMAGE_NAME}:latest"):
        print("[+] DEPLOY SUCCESS! APP UPDATED at http://localhost:8080\n")
    else:
        print("[-] Container start failed.\n")


class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Health check
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status": "webhook listener active"}\n')

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length)

        # Check secret HMAC if set
        if SECRET:
            sig = self.headers.get("X-Hub-Signature-256", "")
            calc = "sha256=" + hmac.new(SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, calc):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Bad signature\n")
                return

        event = self.headers.get("X-GitHub-Event", "")

        # GitHub ping test
        if event == "ping":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Pong!\n")
            return

        # Push or PR merge to main
        if event == "push":
            try:
                payload = json.loads(raw_body.decode("utf-8"))
            except Exception:
                payload = {}

            branch = payload.get("ref", "")
            if branch == "refs/heads/main":
                # Respond to GitHub immediate so no timeout
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Deploy started in background\n")

                # Run deploy in thread
                t = threading.Thread(target=deploy_task)
                t.start()
                return

        # Other events
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Event ignored\n")


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    print(f"[+] Webhook listener running at http://0.0.0.0:{PORT}")
    server.serve_forever()
