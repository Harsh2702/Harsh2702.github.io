from pyngrok import ngrok
import subprocess
import time

# Step 1: Start Flask app
flask_process = subprocess.Popen(["python", "demo.py"])
print("[✔] Flask app started...")

# Step 2: Wait a few seconds to ensure Flask is running
time.sleep(5)  # You can adjust this if needed

# Step 3: Start Ngrok tunnel
port = 5000  # or the port your Flask app uses
public_url = ngrok.connect(port, "http")
print(f"[✔] Ngrok tunnel established:-- {public_url.public_url+"/demo"}")

# Optional: Save URL to a file for easy access
with open("webhook_url.txt", "w") as f:
    f.write(str(public_url.public_url+"/demo"))

print("\n[✅] All set! Paste this URL into Dialogflow webhook settings.")
input("Press ENTER to quit and terminate the server...\n")

# Step 4: Clean up
flask_process.terminate()
ngrok.kill()
