import requests
import os
import random

# --- CONFIGURAÇÕES ---
ARQUIVO_COOKIES = 'scookie.txt' 
CAMINHO_FOTOS = r'C:\Caminho\para\Fotos\de_Perfil\'
# ---------------------

def carregar_cookies(caminho):
    cookies = {}
    if not os.path.exists(caminho): return None
    with open(caminho, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('#') and line.strip():
                parts = line.split('\t')
                if len(parts) >= 7:
                    cookies[parts[5].strip()] = parts[6].strip()
    return cookies

def capturar_dados_perfil(session, steam_id):
    """Retorna (ID_da_URL, Nome_Nick)"""
    id_url = steam_id
    nick = steam_id
    try:
        res = session.get(f"https://steamcommunity.com/profiles/{steam_id}/", timeout=5)
        if res.status_code == 200:
            # Captura o ID da URL (ex: akaimxntis)
            if 'rel="canonical" href="https://steamcommunity.com/id/' in res.text:
                id_url = res.text.split('id/')[1].split('/')[0].strip()
            
            # Captura o Nick (ex: ᴉɐʞⱯ)
            if 'actual_persona_name">' in res.text:
                nick = res.text.split('actual_persona_name">')[1].split('</span>')[0].strip()
    except:
        pass
    return id_url, nick

def mudar_foto_steam():
    dict_cookies = carregar_cookies(ARQUIVO_COOKIES)
    if not dict_cookies:
        print("❌ Erro: Arquivo de cookies não encontrado.")
        return

    steam_id_64 = dict_cookies.get('steamLoginSecure', '').split('%7C%7C')[0]
    sess_id = dict_cookies.get('sessionid')

    session = requests.Session()
    for name, value in dict_cookies.items():
        session.cookies.set(name, value, domain='steamcommunity.com')

    # Puxa os dois nomes automaticamente
    id_exibicao, nome_perfil = capturar_dados_perfil(session, steam_id_64)

    fotos = [f for f in os.listdir(CAMINHO_FOTOS) if f.endswith(('.png', '.jpg', '.jpeg'))]
    if not fotos: return
    foto_escolhida = os.path.join(CAMINHO_FOTOS, random.choice(fotos))

    print(f"👤 Usuário identificado: {id_exibicao}")
    print(f"📸 Foto: {os.path.basename(foto_escolhida)}")
    
    payload = {
        "MAX_FILE_SIZE": "1048576",
        "type": "player_avatar_image",
        "sId": steam_id_64,
        "sessionid": sess_id,
        "doSub": "1"
    }

    headers = {"User-Agent": "Mozilla/5.0", "Referer": f"https://steamcommunity.com/profiles/{steam_id_64}/edit/avatar"}

    try:
        with open(foto_escolhida, 'rb') as f:
            files = {'avatar': (os.path.basename(foto_escolhida), f, 'image/jpeg')}
            response = session.post("https://steamcommunity.com/actions/FileUploader/", data=payload, files=files, headers=headers)
            
        if response.status_code == 200 and "error" not in response.text.lower():
            # --- SEU SEGUNDO PRINT ESPECÍFICO ---
            print(f"✅ Sucesso! Foto de {nome_perfil} alterada.")
        else:
            print(f"❌ Falha no upload para {id_exibicao}.")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    mudar_foto_steam()
