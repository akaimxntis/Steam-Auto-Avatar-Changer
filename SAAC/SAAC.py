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
                f"Arquivo '{os.path.basename(file_path)}' excede o tamanho máximo: "
                f"{size_mb:.2f}MB (máximo: {max_size / (1024 * 1024):.2f}MB)",
                'warning'
            )
            print_console(f"❌ Arquivo excede o tamanho máximo ({size_mb:.2f}MB)")
            return False
        
        log_only(f"Arquivo '{os.path.basename(file_path)}' validado: {size_mb:.2f}MB", 'debug')
        return True
    except Exception as e:
        log_only(f"Erro ao validar tamanho do arquivo: {e}", 'error')
        print_console(f"❌ Erro ao validar arquivo: {e}")
        return False

def upload_avatar_with_retry(session, upload_data, files, headers, steam_id_64, photo_name):
    attempt = 0
    
    while attempt < MAX_RETRIES:
        try:
            attempt += 1
            print_console(f"⏳ Tentativa {attempt}/{MAX_RETRIES} de upload da avatar...")
            log_only(f"Tentativa {attempt}/{MAX_RETRIES} de upload da avatar...")
            
            response = session.post(
                "https://steamcommunity.com/actions/FileUploader/",
                data=upload_data,
                files=files,
                headers=headers,
                timeout=10
            )
            
            log_only(f"Resposta HTTP: {response.status_code}", 'debug')
            
            if response.status_code == 200:
                res_lower = response.text.lower()
                if "error" not in res_lower:
                    log_only(
                        f"Avatar alterada com sucesso! Foto: {photo_name}, "
                        f"Steam ID: {steam_id_64}, Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    print_console("✅ Avatar alterada com sucesso!")
                    return True, response
                else:
                    log_only(f"Erro na resposta do Steam: {response.text[:200]}", 'warning')
                    print_console(f"❌ Falha ao fazer upload.")
                    return False, response
            else:
                log_only(f"HTTP {response.status_code} - Tentando novamente...", 'warning')
                
                if attempt < MAX_RETRIES:
                    log_only(f"Aguardando {RETRY_DELAY}s antes da próxima tentativa...")
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    log_only(f"Upload falhou após {MAX_RETRIES} tentativas", 'error')
                    print_console(f"❌ Upload falhou após {MAX_RETRIES} tentativas.")
                    return False, response
        
        except requests.Timeout:
            log_only(f"Timeout na tentativa {attempt} - Retry em andamento...", 'warning')
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                log_only(f"Timeout após {MAX_RETRIES} tentativas", 'error')
                print_console(f"❌ Timeout após {MAX_RETRIES} tentativas.")
                return False, None
        
        except requests.RequestException as e:
            log_only(f"Erro de conexão na tentativa {attempt}: {e}", 'warning')
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                log_only(f"Falha de conexão após {MAX_RETRIES} tentativas", 'error')
                print_console(f"❌ Erro de conexão após {MAX_RETRIES} tentativas.")
                return False, None
        
        except Exception as e:
            log_only(f"Erro inesperado na tentativa {attempt}: {e}", 'error')
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                return False, None
    
    return False, None

def load_config():
    default_config = {
        "caminho_fotos": str(Path.home() / "Pictures")
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                config = json.loads(content)
                log_only(f"Configuração carregada: {config.get('caminho_fotos')}")
                return config
        except Exception as e:
            log_only(f"Erro ao ler {CONFIG_FILE}: {e}", 'error')
            save_config(default_config)
            return default_config
    else:
        save_config(default_config)
        log_only(f"{CONFIG_FILE} criado com path padrão: {default_config['caminho_fotos']}")
        print_console(f"[!] {CONFIG_FILE} criado. Configure o caminho das fotos nele.")
        return default_config

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        log_only("Configuração salva com sucesso")
    except Exception as e:
        log_only(f"Erro ao salvar {CONFIG_FILE}: {e}", 'error')

def load_cookies(path):
    cookies = {}
    if not os.path.exists(path):
        log_only(f"{COOKIES_FILE} não encontrado em {path}", 'error')
        print_console(f"[!] {COOKIES_FILE} não encontrado.")
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            # Tenta ler no formato Netscape (com tabulações)
            if '\t' in content or content.startswith('#'):
                lines = content.split('\n')
                for line in lines:
                    if not line.startswith('#') and line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 7:
                            cookies[parts[5].strip()] = parts[6].strip()
            
            # Tenta ler no formato de string bruta (header HTTP)
            elif '=' in content and ';' in content:
                # Remove espaços e quebras de linha em excesso
                clean_content = content.replace('\n', '').replace('\r', '')
                cookie_pairs = clean_content.split(';')
                for pair in cookie_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        cookies[key.strip()] = value.strip()
            
            else:
                log_only("Formato de cookie não reconhecido.", 'error')
                return None
                
        log_only(f"Cookies carregados com sucesso ({len(cookies)} cookies)")
        return cookies if cookies else None
    except Exception as e:
        log_only(f"Erro ao carregar cookies: {e}", 'error')
        print_console(f"[!] Erro ao carregar cookies: {e}")
        return None

def fetch_profile_data(session, steam_id):
    url_id = steam_id
    nickname = steam_id
    try:
        log_only(f"Buscando dados do perfil para Steam ID: {steam_id}", 'debug')
        res = session.get(f"https://steamcommunity.com/profiles/{steam_id}/", timeout=5)
        
        if res.status_code == 200:
            if 'rel="canonical" href="https://steamcommunity.com/id/' in res.text:
                url_id = res.text.split('id/')[1].split('/')[0].strip()
            
            if 'actual_persona_name">' in res.text:
                nickname = res.text.split('actual_persona_name">')[1].split('</span>')[0].strip()
            
            log_only(f"Perfil identificado: {nickname} (ID: {url_id})")
        else:
            log_only(f"Status {res.status_code} ao buscar perfil", 'warning')
    except Exception as e:
        log_only(f"Erro ao buscar dados do perfil: {e}", 'error')
    
    return url_id, nickname

def change_steam_photo():
    log_only("=" * 60)
    log_only("Iniciando Steam Auto Avatar Changer")
    log_only("=" * 60)
    
    print_console("[Iniciando Steam Auto Avatar Changer]".center(os.get_terminal_size().columns))
    
    config = load_config()
    caminho_fotos = config.get('caminho_fotos')
    
    print(f"\n🔍 Procurando fotos em: {caminho_fotos}")
    log_only(f"Procurando fotos em: {caminho_fotos}")
    
    if not os.path.isdir(caminho_fotos):
        print(f"❌ Diretório não encontrado: {caminho_fotos}")
        log_only(f"Diretório não encontrado: {caminho_fotos}", 'error')
        return False
    
    dict_cookies = load_cookies(COOKIES_FILE)
    if not dict_cookies:
        print("❌ Erro ao carregar cookies")
        log_only("Erro ao carregar cookies", 'error')
        return False
    
    steam_id_64 = dict_cookies.get('steamLoginSecure', '').split('%7C%7C')[0]
    sess_id = dict_cookies.get('sessionid')
    
    if not steam_id_64 or not sess_id:
        print("❌ Cookies inválidos ou expirados.")
        log_only("Cookies inválidos ou expirados", 'error')
        return False
    
    log_only(f"Steam ID autenticado: {steam_id_64}")
    
    session = requests.Session()
    for name, value in dict_cookies.items():
        session.cookies.set(name, value, domain='steamcommunity.com')
    
    display_id, profile_name = fetch_profile_data(session, steam_id_64)
    
    try:
        photos = [f for f in os.listdir(caminho_fotos) if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if not photos:
            print("❌ Nenhuma imagem encontrada no diretório.")
            log_only("Nenhuma imagem encontrada no diretório", 'error')
            return False
        
        print_console(f"📊 Encontradas {len(photos)} imagens no diretório")
        log_only(f"Encontradas {len(photos)} imagens no diretório")
        
        chosen_photo = os.path.join(caminho_fotos, random.choice(photos))
        chosen_photo_name = os.path.basename(chosen_photo)
        
        log_only(f"Foto selecionada: {chosen_photo_name}")
    except Exception as e:
        print(f"❌ Erro ao listar fotos: {e}")
        log_only(f"Erro ao listar fotos: {e}", 'error')
        return False
    
    if not validate_file_size(chosen_photo):
        log_only("Arquivo rejeitado: tamanho excede o limite", 'error')
        return False
    
    print(f"👤 [ID] {steam_id_64}")
    print(f"📸 [Avatar] {chosen_photo_name}")
    print(f"🎮 [Usuário] {profile_name}")
    log_only(f"Iniciando upload - Foto: {chosen_photo_name}, Steam ID: {steam_id_64}, Usuário: {profile_name}")
    
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
            log_only("Processo concluído com sucesso!")
            return True
        else:
            if response:
                log_only(f"Upload falhou (HTTP {response.status_code})", 'error')
            return False
    
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {chosen_photo}")
        log_only(f"Arquivo não encontrado: {chosen_photo}", 'error')
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        log_only(f"Erro durante o upload: {e}", 'error')
        return False
    finally:
        log_only("=" * 60)

if __name__ == "__main__":
    change_steam_photo()
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
                f"Arquivo '{os.path.basename(file_path)}' excede o tamanho máximo: "
                f"{size_mb:.2f}MB (máximo: {max_size / (1024 * 1024):.2f}MB)",
                'warning'
            )
            print_console(f"❌ Arquivo excede o tamanho máximo ({size_mb:.2f}MB)")
            return False
        
        log_only(f"Arquivo '{os.path.basename(file_path)}' validado: {size_mb:.2f}MB", 'debug')
        return True
    except Exception as e:
        log_only(f"Erro ao validar tamanho do arquivo: {e}", 'error')
        print_console(f"❌ Erro ao validar arquivo: {e}")
        return False

def upload_avatar_with_retry(session, upload_data, files, headers, steam_id_64, photo_name):
    attempt = 0
    
    while attempt < MAX_RETRIES:
        try:
            attempt += 1
            print_console(f"⏳ Tentativa {attempt}/{MAX_RETRIES} de upload da avatar...")
            log_only(f"Tentativa {attempt}/{MAX_RETRIES} de upload da avatar...")
            
            response = session.post(
                "https://steamcommunity.com/actions/FileUploader/",
                data=upload_data,
                files=files,
                headers=headers,
                timeout=10
            )
            
            log_only(f"Resposta HTTP: {response.status_code}", 'debug')
            
            if response.status_code == 200:
                res_lower = response.text.lower()
                if "error" not in res_lower:
                    log_only(
                        f"Avatar alterada com sucesso! Foto: {photo_name}, "
                        f"Steam ID: {steam_id_64}, Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    print_console("✅ Avatar alterada com sucesso!")
                    return True, response
                else:
                    log_only(f"Erro na resposta do Steam: {response.text[:200]}", 'warning')
                    print_console(f"❌ Falha ao fazer upload.")
                    return False, response
            else:
                log_only(f"HTTP {response.status_code} - Tentando novamente...", 'warning')
                
                if attempt < MAX_RETRIES:
                    log_only(f"Aguardando {RETRY_DELAY}s antes da próxima tentativa...")
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    log_only(f"Upload falhou após {MAX_RETRIES} tentativas", 'error')
                    print_console(f"❌ Upload falhou após {MAX_RETRIES} tentativas.")
                    return False, response
        
        except requests.Timeout:
            log_only(f"Timeout na tentativa {attempt} - Retry em andamento...", 'warning')
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                log_only(f"Timeout após {MAX_RETRIES} tentativas", 'error')
                print_console(f"❌ Timeout após {MAX_RETRIES} tentativas.")
                return False, None
        
        except requests.RequestException as e:
            log_only(f"Erro de conexão na tentativa {attempt}: {e}", 'warning')
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                log_only(f"Falha de conexão após {MAX_RETRIES} tentativas", 'error')
                print_console(f"❌ Erro de conexão após {MAX_RETRIES} tentativas.")
                return False, None
        
        except Exception as e:
            log_only(f"Erro inesperado na tentativa {attempt}: {e}", 'error')
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                return False, None
    
    return False, None

def load_config():
    default_config = {
        "caminho_fotos": str(Path.home() / "Pictures")
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                config = json.loads(content)
                log_only(f"Configuração carregada: {config.get('caminho_fotos')}")
                return config
        except Exception as e:
            log_only(f"Erro ao ler {CONFIG_FILE}: {e}", 'error')
            save_config(default_config)
            return default_config
    else:
        save_config(default_config)
        log_only(f"{CONFIG_FILE} criado com path padrão: {default_config['caminho_fotos']}")
        print_console(f"[!] {CONFIG_FILE} criado. Configure o caminho das fotos nele.")
        return default_config

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        log_only("Configuração salva com sucesso")
    except Exception as e:
        log_only(f"Erro ao salvar {CONFIG_FILE}: {e}", 'error')

def load_cookies(path):
    cookies = {}
    if not os.path.exists(path):
        log_only(f"{COOKIES_FILE} não encontrado em {path}", 'error')
        print_console(f"[!] {COOKIES_FILE} não encontrado.")
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.startswith('#') and line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 7:
                        cookies[parts[5].strip()] = parts[6].strip()
        
        log_only(f"Cookies carregados com sucesso ({len(cookies)} cookies)")
        return cookies if cookies else None
    except Exception as e:
        log_only(f"Erro ao carregar cookies: {e}", 'error')
        print_console(f"[!] Erro ao carregar cookies: {e}")
        return None

def fetch_profile_data(session, steam_id):
    url_id = steam_id
    nickname = steam_id
    try:
        log_only(f"Buscando dados do perfil para Steam ID: {steam_id}", 'debug')
        res = session.get(f"https://steamcommunity.com/profiles/{steam_id}/", timeout=5)
        
        if res.status_code == 200:
            if 'rel="canonical" href="https://steamcommunity.com/id/' in res.text:
                url_id = res.text.split('id/')[1].split('/')[0].strip()
            
            if 'actual_persona_name">' in res.text:
                nickname = res.text.split('actual_persona_name">')[1].split('</span>')[0].strip()
            
            log_only(f"Perfil identificado: {nickname} (ID: {url_id})")
        else:
            log_only(f"Status {res.status_code} ao buscar perfil", 'warning')
    except Exception as e:
        log_only(f"Erro ao buscar dados do perfil: {e}", 'error')
    
    return url_id, nickname

def change_steam_photo():
    log_only("=" * 60)
    log_only("Iniciando Steam Auto Avatar Changer")
    log_only("=" * 60)
    
    print_console("[Iniciando Steam Auto Avatar Changer]".center(os.get_terminal_size().columns))
    
    config = load_config()
    caminho_fotos = config.get('caminho_fotos')
    
    print(f"\n🔍 Procurando fotos em: {caminho_fotos}")
    log_only(f"Procurando fotos em: {caminho_fotos}")
    
    if not os.path.isdir(caminho_fotos):
        print(f"❌ Diretório não encontrado: {caminho_fotos}")
        log_only(f"Diretório não encontrado: {caminho_fotos}", 'error')
        return False
    
    dict_cookies = load_cookies(COOKIES_FILE)
    if not dict_cookies:
        print("❌ Erro ao carregar cookies")
        log_only("Erro ao carregar cookies", 'error')
        return False
    
    steam_id_64 = dict_cookies.get('steamLoginSecure', '').split('%7C%7C')[0]
    sess_id = dict_cookies.get('sessionid')
    
    if not steam_id_64 or not sess_id:
        print("❌ Cookies inválidos ou expirados.")
        log_only("Cookies inválidos ou expirados", 'error')
        return False
    
    log_only(f"Steam ID autenticado: {steam_id_64}")
    
    session = requests.Session()
    for name, value in dict_cookies.items():
        session.cookies.set(name, value, domain='steamcommunity.com')
    
    display_id, profile_name = fetch_profile_data(session, steam_id_64)
    
    try:
        photos = [f for f in os.listdir(caminho_fotos) if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if not photos:
            print("❌ Nenhuma imagem encontrada no diretório.")
            log_only("Nenhuma imagem encontrada no diretório", 'error')
            return False
        
        print_console(f"📊 Encontradas {len(photos)} imagens no diretório")
        log_only(f"Encontradas {len(photos)} imagens no diretório")
        
        chosen_photo = os.path.join(caminho_fotos, random.choice(photos))
        chosen_photo_name = os.path.basename(chosen_photo)
        
        log_only(f"Foto selecionada: {chosen_photo_name}")
    except Exception as e:
        print(f"❌ Erro ao listar fotos: {e}")
        log_only(f"Erro ao listar fotos: {e}", 'error')
        return False
    
    if not validate_file_size(chosen_photo):
        log_only("Arquivo rejeitado: tamanho excede o limite", 'error')
        return False
    
    print(f"👤 [ID] {steam_id_64}")
    print(f"📸 [Avatar] {chosen_photo_name}")
    print(f"🎮 [Usuário] {profile_name}")
    log_only(f"Iniciando upload - Foto: {chosen_photo_name}, Steam ID: {steam_id_64}, Usuário: {profile_name}")
    
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
            log_only("Processo concluído com sucesso!")
            return True
        else:
            if response:
                log_only(f"Upload falhou (HTTP {response.status_code})", 'error')
            return False
    
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {chosen_photo}")
        log_only(f"Arquivo não encontrado: {chosen_photo}", 'error')
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        log_only(f"Erro durante o upload: {e}", 'error')
        return False
    finally:
        log_only("=" * 60)

if __name__ == "__main__":
    change_steam_photo()
