from msal import PublicClientApplication, SerializableTokenCache
import os
import atexit
import requests
import json
import sys

# Constants
CLIENT_ID = os.getenv('OPSP_XR_CLIENT_ID')
SCOPES = ["Xboxlive.signin", "Xboxlive.offline_access"]
XBL_VERSION = "3.0"
TOKEN_CACHE_PATH = "cache.bin"

# Token cache setup
cache = SerializableTokenCache()

target_gamertag = sys.argv[1] if len(sys.argv) > 1 else "BreadKrtek"

# Saves the token cache to disk to make sure that we're not authenticating
# from scratch every single time the script runs.
def save_cache():
    if cache.has_state_changed:
        with open(TOKEN_CACHE_PATH, "w") as token_cache_file:
            token_cache_file.write(cache.serialize())

# Request the Xbox user token.
def request_user_token(access_token):
    ticket_data = {
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": f"d={access_token}"
        }
    }

    headers = {
        "x-xbl-contract-version": "1",
        "Content-Type": "application/json"
    }

    response = requests.post(
        url="https://user.auth.xboxlive.com/user/authenticate",
        json=ticket_data,
        headers=headers
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Request XSTS token from Xbox.
def request_xsts_token(user_token):
    ticket_data = {
        "RelyingParty": "http://xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "UserTokens": [user_token],
            "SandboxId": "RETAIL"
        }
    }

    headers = {
        "x-xbl-contract-version": "1",
        "Content-Type": "application/json"
    }

    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    response = requests.post(url, json=ticket_data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Search for users on Xbox based on a gamertag.
def search_for_user(gamertag, token):
    headers = {
        "x-xbl-contract-version": "3",
        "Content-Type": "application/json",
        "Authorization": token,
        "Accept-Language": "en-us"
    }

    url = f"https://peoplehub.xboxlive.com/users/me/people/search/decoration/detail,preferredColor?q={gamertag}&maxItems=25"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Extract and print gamertags and the associated XUIDs.
def get_gamertags(data):
	if 'people' in data:
		print("{:<20} {}".format("Gamertag", "XUID"))
		print("-" * 30)
		for person in data['people']:
			gamertag = person.get('gamertag', 'Unknown Gamertag')
			xuid = person.get('xuid', 'Unknown XUID')
			print("{:<20} {}".format(gamertag, xuid))

# Load token cache if exists
if os.path.exists(TOKEN_CACHE_PATH):
    print("Loading token cache from disk")
    with open(TOKEN_CACHE_PATH, "r") as token_cache_file:
        cache.deserialize(token_cache_file.read())
    print("Loaded token cache from disk")

atexit.register(save_cache)

# Initialize MSAL to get the user token for their application
app = PublicClientApplication(
    CLIENT_ID,
    authority="https://login.microsoftonline.com/consumers",
    token_cache=cache
)

accounts = app.get_accounts()
result = None

# Acquire token.
if accounts:
    print("Account exists in the cache.")
    result = app.acquire_token_silent(SCOPES, account=accounts[0])
else:
    print("No accounts in the cache")
    result = app.acquire_token_interactive(SCOPES)

# Proceed if token is obtained.
if result and 'access_token' in result:
    ticket = request_user_token(result['access_token'])
    
    if ticket:
        user_token = ticket.get('Token')
        user_hash = ticket.get('DisplayClaims', {}).get('xui', [{}])[0].get('uhs')

        xsts_ticket = request_xsts_token(user_token)
        
        if xsts_ticket:
            xsts_token = xsts_ticket.get('Token')
            xbl_token = f'XBL{XBL_VERSION} x={user_hash};{xsts_token}'

            user_data = search_for_user(target_gamertag, xbl_token)

            if user_data:
                get_gamertags(user_data)
