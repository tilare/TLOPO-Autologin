import os
import subprocess
import sys

# Try to import requests
try:
    import requests
except ImportError:
    print("Error: 'requests' library not found.")
    print("Please run: pip install requests")
    input("Press Enter to exit...")
    sys.exit()

# --- CONFIGURATION ---
USERNAME = 'YourUsername'
PASSWORD = 'YourPassword'
GAME_EXE_PATH = r"C:\Program Files (x86)\TLOPO\tlopo.exe" 
# ---------------------

def login_and_play():
    if not os.path.exists(GAME_EXE_PATH):
        print(f"Error: Game executable not found at: {GAME_EXE_PATH}")
        input("Press Enter to exit...")
        return

    print(f"Authenticating '{USERNAME}'...")
    
    # 1. First Login Attempt
    session = requests.Session()
    payload = {'username': USERNAME, 'password': PASSWORD}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    
    try:
        r = session.post('https://api.tlopo.com/login/', data=payload, headers=headers)
        response = r.json()
    except Exception as e:
        print(f"Connection failed: {e}")
        input("Press Enter to exit...")
        return

    # 2. Check Status
    status = int(response.get('status', 0))

    # STATUS 3: 2FA REQUIRED
    if status == 3:
        print("\n>> Two-Factor Authentication (2FA) requested by server.")
        gtoken = input(">> Please enter your 2FA Code (from app/email): ")
        
        # Resend login with the 2FA code (gtoken)
        payload['gtoken'] = gtoken
        print("Verifying code...")
        
        try:
            r = session.post('https://api.tlopo.com/login/', data=payload, headers=headers)
            response = r.json()
            status = int(response.get('status', 0))
        except Exception as e:
            print(f"Connection failed: {e}")
            return

    # STATUS 11: NEW LOCATION (Arrrmor)
    if status == 11:
        print("\n>> TLOPO 'Arrrmor' triggered.")
        print(">> The server sees this as a new location. Please check your email to approve this IP.")
        input("Press Enter to exit...")
        return

    # 3. Final Success Check
    if status == 7 and 'token' in response:
        print(f"\nLogin successful! Token acquired.")
        
        # Set Environment Variables
        env = os.environ.copy()
        env['TLOPO_GAMESERVER'] = response['gameserver']
        env['TLOPO_PLAYCOOKIE'] = response['token']
        
        # Launch
        print("Launching TLOPO...")
        subprocess.Popen([GAME_EXE_PATH], env=env, cwd=os.path.dirname(GAME_EXE_PATH))
        
    else:
        # Failure
        msg = response.get('message', 'Unknown error')
        print(f"\nLogin Failed (Status {status}): {msg}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    login_and_play()
