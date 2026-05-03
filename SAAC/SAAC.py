import requests
import os
import random
import json
import sys
from pathlib import Path

CONFIG_FILE = 'config.json'
COOKIES_FILE = 'scookie.txt'

def load_config():
    default_config = {
        "photos_path": str(Path.home() / "Pictures")
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                config = json.loads(content)
                return config
        except Exception as e:
            print(f"[!] Error reading {CONFIG_FILE}: {e}")
            save_config(default_config)
            return default_config
    else:
        save_config(default_config)
        print(f"[!] {CONFIG_FILE} created. Please configure your photos path in it.")
        print(f"[!] Default path set to: {default_config['photos_path']}")
        return default_config

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Error saving {CONFIG_FILE}: {e}")

def load_cookies(path):
    cookies = {}
    if not os.path.exists(path):
        print(f"[!] {COOKIES_FILE} not found.")
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.startswith('#') and line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 7:
                        cookies[parts[5].strip()] = parts[6].strip()
        return cookies if cookies else None
    except Exception as e:
        print(f"[!] Error loading cookies: {e}")
        return None

def fetch_profile_data(session, steam_id):
    url_id = steam_id
    nickname = steam_id
    try:
        res = session.get(f"https://steamcommunity.com/profiles/{steam_id}/", timeout=5)
        if res.status_code == 200:
            if 'rel="canonical" href="https://steamcommunity.com/id/' in res.text:
                url_id = res.text.split('id/')[1].split('/')[0].strip()
            
            if 'actual_persona_name">' in res.text:
                nickname = res.text.split('actual_persona_name">')[1].split('</span>')[0].strip()
    except:
        pass
    return url_id, nickname

def change_steam_photo():
    config = load_config()
    photos_path = config.get('photos_path')
    
    print(f"\nLooking for photos in: {photos_path}")
    
    if not os.path.isdir(photos_path):
        print(f"❌ Directory not found: {photos_path}")
        return False
    
    dict_cookies = load_cookies(COOKIES_FILE)
    if not dict_cookies:
        print("❌ Error loading cookies")
        return False
    
    steam_id_64 = dict_cookies.get('steamLoginSecure', '').split('%7C%7C')[0]
    sess_id = dict_cookies.get('sessionid')
    
    if not steam_id_64 or not sess_id:
        print("❌ Invalid or expired cookies.")
        return False
    
    session = requests.Session()
    for name, value in dict_cookies.items():
        session.cookies.set(name, value, domain='steamcommunity.com')
    
    display_id, profile_name = fetch_profile_data(session, steam_id_64)
    
    try:
        photos = [f for f in os.listdir(photos_path) if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if not photos:
            print("❌ No images found in directory.")
            return False
        
        chosen_photo = os.path.join(photos_path, random.choice(photos))
    except Exception as e:
        print(f"❌ Error listing photos: {e}")
        return False
    
    print(f"\n👤 [ID] {steam_id_64}")
    print(f"📸 [Avatar] {os.path.basename(chosen_photo)}")
    print(f"🎮 [User] {profile_name}")
    
    upload_data = {
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
            response = session.post(
                "https://steamcommunity.com/actions/FileUploader/",
                data=upload_data,
                files=files,
                headers=headers,
                timeout=10
            )
        
        print(f"\nResult: Status Code #{response.status_code}")
        
        if response.status_code == 200:
            res_lower = response.text.lower()
            if "error" not in res_lower:
                print("✅ Avatar changed successfully!\n")
                return True
            else:
                print("❌ Failed to upload.\n")
                print(f"[DEBUG] Response: {response.text[:200]}")
                return False
        else:
            print(f"❌ Upload failed (HTTP {response.status_code}).\n")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False

if __name__ == "__main__":
    change_steam_photo()
