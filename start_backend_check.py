
import os
import subprocess
import sys
import time

# Set environment variables
os.environ["QDRANT_URL"] = "https://44f1eced-a617-4726-8d5d-90f66a56e2e2.us-east4-0.gcp.cloud.qdrant.io"
os.environ["QDRANT_API_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.XLi_uw9vKDmaR7DK565IDF7Ryl5AxubOMhVO2Mi928U"
os.environ["GOOGLE_API_KEY"] = "AIzaSyA6a_PAT_ZRB4gDs3j-CCel7nQw2BNVaDw"

# Construct the command to run src/main.py
backend_script_path = os.path.join("D:/physical-ai-humanoid-textbook/src", "main.py")
command = [sys.executable, backend_script_path]

# Start the process. Using Popen directly for more control and to run in background.
# Redirecting stdout and stderr to DEVNULL to avoid blocking or filling up logs
# if the output is not explicitly managed.
print(f"Starting backend server with command: {' '.join(command)}")
process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"Backend server process started with PID: {process.pid}")
print("Backend server is expected to be running in the background on port 8000.")
print("You may need to manually terminate this process later (PID: {process.pid}).")

# Sleep briefly to give the server time to start up
time.sleep(10) # Increased sleep time to ensure FastAPI fully starts
