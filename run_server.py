import os
import sys
import subprocess
import time
import socket

os.environ["DISABLE_SENTENCE_TRANSFORMERS"] = "1"

PORT = 8000

def kill_process_on_port(port):
    """Find and kill any process using the specified port on Windows."""
    if os.name != 'nt':
        return
        
    try:
        # Get the PID of the process using the port
        cmd = f"netstat -ano | findstr :{port}"
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')
        pids = set()
        for line in output.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 5 and 'LISTENING' in parts:
                pids.add(parts[-1])
                
        for pid in pids:
            print(f"Found lingering process on port {port} with PID {pid}. Killing it...")
            subprocess.run(f"taskkill /F /PID {pid}", shell=True)
            time.sleep(0.5)
    except subprocess.CalledProcessError:
        # findstr exits with code 1 if no matches are found
        pass
    except Exception as e:
        print(f"Error checking/killing process on port {port}: {e}")

def check_port_free(port):
    """Return True if the port is free, False otherwise."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except socket.error:
            return False

if __name__ == '__main__':
    print("Preparing to start Conservator's Workshop Ledger server...")
    
    # 1. Clean up any existing process on port 8000
    kill_process_on_port(PORT)
    
    # Wait a moment to ensure socket is released
    for _ in range(5):
        if check_port_free(PORT):
            break
        print("Waiting for port 8000 to become free...")
        time.sleep(1)
        
    # 2. Run uvicorn without --reload to avoid file locks, infinite reload loops,
    # and duplicate process spawning in background environments.
    print(f"Starting server on port {PORT} (static mode, no reload to ensure IDE stability)...")
    
    # We use sys.executable to run uvicorn in the current python environment
    cmd = [sys.executable, "-m", "uvicorn", "monitoring.app:app", "--host", "127.0.0.1", "--port", str(PORT)]
    
    # Run the server
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nStopping server...")
