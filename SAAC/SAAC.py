import requests
import os
import random
import json
import sys
import logging
import time
from pathlib import Path
from datetime import datetime

CONFIG_FILE = 'config.json'
COOKIES_FILE = 'scookie.txt'
LOG_FILE = 'SAAC_audit.log'
MAX_FILE_SIZE = 1048576
MAX_RETRIES = 3
RETRY_DELAY = 2

def setup_logging():
    logger = logging.getLogger('SAAC')
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

def print_console(message):
    print(message)

def log_only(message, level='info'):
    if level == 'debug':
        logger.debug(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    else:
        logger.info(message)

def validate_file_size(file_path, max_size=MAX_FILE_SIZE):
    try:
        file_size = os.path.getsize(file_path)
        size_mb = file_size / (1024 * 1024)
        
        if file_size > max_size:
            log_only(
                f"File '{os.path.basename(file_path)}' exceeds maximum size: "
                f"{size_mb:.2f}MB (maximum: {max_size / (1024 * 1024):.2f}MB)",
                'warning'
            )
            print_console(f"❌ File exceeds maximum size ({size_mb:.2f}MB)")
            return False
        
        log_only(f"File '{os.path.basename(file_path)}' validated: {size_mb:.2f}MB", 'debug')
        return True
    except Exception as e:
        log_only(f"Error validating file size: {e}", 'error')
        print_console(f"❌ Error validating file: {e}")
        return False

def upload_avatar_with_retry(session, upload_data, files, headers, steam_id_64, photo_name):
    attempt = 0
    
    while attempt < MAX_RETRIES:
        try:
            attempt += 1
            print_console(f"⏳ Attempt {attempt}/{MAX_RETRIES} to upload avatar...")
            log_only(f"Attempt {attempt}/{MAX_RETRIES} to upload avatar...")
            
            response = session.post(
                "https://steamcommunity.com/actions/FileUploader/",
                data=upload_data,
                files=files,
                headers=headers,
                timeout=10
            )
            
            log_only(f"HTTP Response: {response.status_code}", 'debug')
            
            if response.status_code == 200:
                res_lower = response.text.lower()
                if "error" not in res_lower:
                    log_only(
                        f"Avatar changed successfully! Photo: {photo_name}, "
                        f"Steam ID: {steam_id_64}, Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    print_console("✅ Avatar changed successfully!")
                    return True, response
                else:
                    log_only(f"Error in Steam response: {response.text[:200]}", 'warning')
                    print_console(f"❌ Upload failed.")
                    return False, response
            else:
                log_only(f"HTTP {response.status_code} - Retrying...", 'warning')
                
                if attempt < MAX_RETRIES:
                    log_only(f"Waiting {RETRY_DELAY}s before next attempt...")
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    log_only(f"Upload failed after {MAX_RETRIES} attempts", 'error')
                    print_console(f"❌ Upload failed after {MAX_RETRIES} attempts.")
                    return False, response
        
        except requests.Timeout:
            log_only(f"Timeout on attempt {attempt} - Retrying...", 'warning')
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                log_only(f"Timeout after {MAX_RETRIES} attempts", 'error')
                print_console(f"❌ Timeout after {MAX_RETRIES} attempts.")
                return False, None
        
        except requests.RequestException as e:
            log_only(f"Connection error on attempt {attempt}: {e}", 'warning')
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                log_only(f"Connection failed after {MAX_RETRIES} attempts", 'error')
                print_console(f"❌ Connection error after {MAX_RETRIES} attempts.")
                return False, None
        
        except Exception as e:
            log_only(f"Unexpected error on attempt {attempt}: {e}", 'error')
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                return False, None
    
    return False, None

def load_config():
    default_config = {
        "photos_path": str(Path.home() / "Pictures")
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                config = json.loads(content)
                log_only(f"Config loaded: {config.get('photos_path')}")
                return config
        except Exception as e:
            log_only(f"Error reading {CONFIG_FILE}: {e}", 'error')
            save_config(default_config)
            return default_config
    else:
        save_config(default_config)
        log_only(f"{CONFIG_FILE} created with default path: {default_config['photos_path']}")
        print_console(f"[!] {CONFIG_FILE} created. Please configure your photos path in it.")
        return default_config

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        log_only("Config saved successfully")
    except Exception as e:
        log_only(f"Error saving {CONFIG_FILE}: {e}", 'error')

def load_cookies(path):
    cookies = {}
    if not os.path.exists(path):
        log_only(f"{COOKIES_FILE} not found at {path}", 'error')
        print_console(f"[!] {COOKIES_FILE} not found.")
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.startswith('#') and line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 7:
                        cookies[parts[5].strip()] = parts[6].strip()
        
        log_only(f"Cookies loaded successfully ({len(cookies)} cookies)")
        return cookies if cookies else None
    except Exception as e:
        log_only(f"Error loading cookies: {e}", 'error')
        print_console(f"[!] Error loading cookies: {e}")
        return None

def fetch_profile_data(session, steam_id):
    url_id = steam_id
    nickname = steam_id
    try:
        log_only(f"Fetching profile data for Steam ID: {steam_id}", 'debug')
        res = session.get(f"https://steamcommunity.com/profiles/{steam_id}/", timeout=5)
        
        if res.status_code == 200:
            if 'rel="canonical" href="https://steamcommunity.com/id/' in res.text:
                url_id = res.text.split('id/')[1].split('/')[0].strip()
            
            if 'actual_persona_name">' in res.text:
                nickname = res.text.split('actual_persona_name">')[1].split('</span>')[0].strip()
            
            log_only(f"Profile identified: {nickname} (ID: {url_id})")
        else:
            log_only(f"Status {res.status_code} when fetching profile", 'warning')
    except Exception as e:
        log_only(f"Error fetching profile data: {e}", 'error')
    
    return url_id, nickname

def change_steam_photo():
    log_only("=" * 60)
    log_only("Starting Steam Auto Avatar Changer")
    log_only("=" * 60)
    
    print_console("[Starting Steam Auto Avatar Changer]".center(os.get_terminal_size().columns))
    
    config = load_config()
    photos_path = config.get('photos_path')
    
    print(f"🔍 Looking for photos in: {photos_path}")
    log_only(f"Looking for photos in: {photos_path}")
    
    if not os.path.isdir(photos_path):
        print(f"❌ Directory not found: {photos_path}")
        log_only(f"Directory not found: {photos_path}", 'error')
        return False
    
    dict_cookies = load_cookies(COOKIES_FILE)
    if not dict_cookies:
        print("❌ Error loading cookies")
        log_only("Error loading cookies", 'error')
        return False
    
    steam_id_64 = dict_cookies.get('steamLoginSecure', '').split('%7C%7C')[0]
    sess_id = dict_cookies.get('sessionid')
    
    if not steam_id_64 or not sess_id:
        print("❌ Invalid or expired cookies.")
        log_only("Invalid or expired cookies", 'error')
        return False
    
    log_only(f"Authenticated Steam ID: {steam_id_64}")
    
    session = requests.Session()
    for name, value in dict_cookies.items():
        session.cookies.set(name, value, domain='steamcommunity.com')
    
    display_id, profile_name = fetch_profile_data(session, steam_id_64)
    
    try:
        photos = [f for f in os.listdir(photos_path) if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if not photos:
            print("❌ No images found in directory.")
            log_only("No images found in directory", 'error')
            return False
        
        print_console(f"📊 Found {len(photos)} images in directory")
        log_only(f"Found {len(photos)} images in directory")
        
        chosen_photo = os.path.join(photos_path, random.choice(photos))
        chosen_photo_name = os.path.basename(chosen_photo)
        
        log_only(f"Photo selected: {chosen_photo_name}")
    except Exception as e:
        print(f"❌ Error listing photos: {e}")
        log_only(f"Error listing photos: {e}", 'error')
        return False
    
    if not validate_file_size(chosen_photo):
        log_only("File rejected: size exceeds limit", 'error')
        return False
    
    print(f"👤 [ID] {steam_id_64}")
    print(f"📸 [Avatar] {chosen_photo_name}")
    print(f"🎮 [User] {profile_name}")
    log_only(f"Starting upload - Photo: {chosen_photo_name}, Steam ID: {steam_id_64}, User: {profile_name}")
    
    upload_data = {
        "MAX_FILE_SIZE": str(MAX_FILE_SIZE),
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
            files = {'avatar': (chosen_photo_name, f, 'image/jpeg')}
            success, response = upload_avatar_with_retry(
                session, upload_data, files, headers, steam_id_64, chosen_photo_name
            )
        
        if success:
            log_only("Process completed successfully!")
            return True
        else:
            if response:
                log_only(f"Upload failed (HTTP {response.status_code})", 'error')
            return False
    
    except FileNotFoundError:
        print(f"❌ File not found: {chosen_photo}")
        log_only(f"File not found: {chosen_photo}", 'error')
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        log_only(f"Error during upload: {e}", 'error')
        return False
    finally:
        log_only("=" * 60)

if __name__ == "__main__":
    change_steam_photo()
