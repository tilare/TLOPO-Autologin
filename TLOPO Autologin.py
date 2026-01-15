import os
import subprocess
import sys

# Try to import requests; if not found, warn the user
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
# Path to the game engine executable
# double-check this path exists on your PC
GAME_EXE_PATH = r"C:\Program Files (x86)\TLOPO\tlopo.exe" 
# ---------------------

def login_and_play():
    if not os.path.exists(GAME_EXE_PATH):
        print(f"Error: Game executable not found at: {GAME_EXE_PATH}")
        return

    print("Authenticating with TLOPO API...")
    
    try:
        # standard login request
        payload = {'username': USERNAME, 'password': PASSWORD}
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        
        r = requests.post('https://api.tlopo.com/login/', data=payload, headers=headers)
        
        # Check if the API call itself worked (HTTP 200)
        if r.status_code != 200:
            print(f"API Error (HTTP {r.status_code})")
            return

        response = r.json()

    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # Check if the response contains the data we need
    if 'gameserver' in response and 'token' in response:
        print(f"Login successful! Token: {response['token'][:10]}...") # Print part of token for verification
        
        # Set Environment Variables required by the game engine
        env = os.environ.copy()
        env['TLOPO_GAMESERVER'] = response['gameserver']
        env['TLOPO_PLAYCOOKIE'] = response['token']
        
        # Launch the game
        print("Launching TLOPO...")
        subprocess.Popen([GAME_EXE_PATH], env=env, cwd=os.path.dirname(GAME_EXE_PATH))
        
    else:
        # Handle errors or 2FA requests
        message = response.get('message', 'Unknown error')
        print(f"\nLogin Failed: {message}")
        
        # Specific check for 2FA
        if "two-factor" in message.lower() or "gtoken" in str(response):
            print(">> It looks like you have 2FA enabled. This script currently only supports standard password login.")
            print(">> You may need to disable 2FA to use auto-login, or modify the script to accept a 'gtoken'.")

if __name__ == "__main__":
    login_and_play()