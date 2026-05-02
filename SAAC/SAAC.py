import requests
import os
import random

# --- SETTINGS ---
COOKIES_FILE = 'scookie.txt' 
PHOTOS_PATH = r'C:\Path\To\Profile\Pictures\'
# ---------------------

def load_cookies(path):
    cookies = {}
    if not os.path.exists(path): return None
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('#') and line.strip():
                parts = line.split('\t')
                if len(parts) >= 7:
                    cookies[parts[5].strip()] = parts[6].strip()
    return cookies

def fetch_profile_data(session, steam_id):
    """Returns (URL_ID, Nickname)"""
    url_id = steam_id
    nickname = steam_id
    try:
        res = session.get(f"https://steamcommunity.com/profiles/{steam_id}/", timeout=5)
        if res.status_code == 200:
            # Captures URL ID (e.g., akaimxntis)
            if 'rel="canonical" href="https://steamcommunity.com/id/' in res.text:
                url_id = res.text.split('id/')[1].split('/')[0].strip()
            
            # Captures Nickname (e.g., ᴉɐʞⱯ)
            if 'actual_persona_name">' in res.text:
                nickname = res.text.split('actual_persona_name">')[1].split('</span>')[0].strip()
    except:
        pass
    return url_id, nickname

def change_steam_photo():
    cookies_dict = load_cookies(COOKIES_FILE)
    if not cookies_dict:
        print("❌ Error: Cookies file not found.")
        return

    steam_id_64 = cookies_dict.get('steamLoginSecure', '').split('%7C%7C')[0]
    sess_id = cookies_dict.get('sessionid')

    session = requests.Session()
    for name, value in cookies_dict.items():
        session.cookies.set(name, value, domain='steamcommunity.com')

    # Automatically fetches both names
    display_id, profile_name = fetch_profile_data(session, steam_id_64)

    photos = [f for f in os.listdir(PHOTOS_PATH) if f.endswith(('.png', '.jpg', '.jpeg'))]
    if not photos: 
        print("❌ No images found in the directory.")
        return
        
    chosen_photo = os.path.join(PHOTOS_PATH, random.choice(photos))

    print(f"👤 Identified user: {display_id}")
    print(f"📸 Photo: {os.path.basename(chosen_photo)}")
    
    payload = {
        "MAX_FILE_SIZE": "1048576",
        "type": "player_avatar_image",
        "sId": steam_id_64,
        "sessionid": sess_id,
        "doSub": "1"
    }

    headers = {
        "User-Agent": "Mozilla/5.0", 
        "Referer": f"https://steamcommunity.com/profiles/{steam_id_64}/edit/avatar"
    }

    try:
        with open(chosen_photo, 'rb') as f:
            files = {'avatar': (os.path.basename(chosen_photo), f, 'image/jpeg')}
            response = session.post("https://steamcommunity.com/actions/FileUploader/", data=payload, files=files, headers=headers)
            
        if response.status_code == 200 and "error" not in response.text.lower():
            print(f"✅ Success! {profile_name}'s photo has been changed.")
        else:
            print(f"❌ Upload failed for {display_id}.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    change_steam_photo()