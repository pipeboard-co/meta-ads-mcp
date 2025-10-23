#!/usr/bin/env python3
import subprocess
import time
import requests

print("Starting server...")
proc = subprocess.Popen(
    ["python3", "run_http_server.py"],
    cwd="/Users/naveengarhwal/meta-ads-mcp-1",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print(f"Process started with PID: {proc.pid}")
time.sleep(5)

try:
    response = requests.get("http://localhost:8080/health", timeout=2)
    print(f"Health check: {response.status_code}")
    print(response.json())
except Exception as e:
    print(f"Health check failed: {e}")

print("\nServer logs:")
stdout, stderr = proc.communicate(timeout=1)
print(stdout.decode() if stdout else "No stdout")
print(stderr.decode() if stderr else "No stderr")

