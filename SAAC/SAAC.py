# -*- coding: utf-8 -*-
import requests
import os
import random
import json
import sys
from pathlib import Path

# --- CONFIGURAÇÃO ---
ARQUIVO_CONFIG = 'config.json'
ARQUIVO_COOKIES = 'scookie.txt'

def carregar_config():
    config_padrao = {
        "caminho_fotos": str(Path.home() / "Pictures")
    }
    
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                config = json.loads(conteudo)
                return config
        except Exception as e:
            print(f"[!] Erro ao ler {ARQUIVO_CONFIG}: {e}")
            salvar_config(config_padrao)
            return config_padrao
    else:
        salvar_config(config_padrao)
        print(f"[!] {ARQUIVO_CONFIG} criado. Configure o caminho das fotos nele.")
        print(f"[!] Caminho padrão definido: {config_padrao['caminho_fotos']}")
        return config_padrao

def salvar_config(config):
    try:
        with open(ARQUIVO_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Erro ao salvar {ARQUIVO_CONFIG}: {e}")

def carregar_cookies(caminho):
    cookies = {}
    if not os.path.exists(caminho):
        print(f"[!] Arquivo {ARQUIVO_COOKIES} não encontrado.")
        return None
    
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            for linha in f:
                if not linha.startswith('#') and linha.strip():
                    partes = linha.split('\t')
                    if len(partes) >= 7:
                        cookies[partes[5].strip()] = partes[6].strip()
        return cookies if cookies else None
    except Exception as e:
        print(f"[!] Erro ao carregar cookies: {e}")
        return None

def buscar_dados_perfil(sessao, steam_id):
    id_url = steam_id
    nickname = steam_id
    try:
        res = sessao.get(f"https://steamcommunity.com/profiles/{steam_id}/", timeout=5)
        if res.status_code == 200:
            if 'rel="canonical" href="https://steamcommunity.com/id/' in res.text:
                id_url = res.text.split('id/')[1].split('/')[0].strip()
            
            if 'actual_persona_name">' in res.text:
                nickname = res.text.split('actual_persona_name">')[1].split('</span>')[0].strip()
    except:
        pass
    return id_url, nickname

def mudar_foto_steam():
    config = carregar_config()
    caminho_fotos = config.get('caminho_fotos')
    
    print(f"\nProcurando fotos em: {caminho_fotos}")
    
    if not os.path.isdir(caminho_fotos):
        print(f"❌ Diretório não encontrado: {caminho_fotos}")
        return False
    
    dict_cookies = carregar_cookies(ARQUIVO_COOKIES)
    if not dict_cookies:
        print("❌ Erro ao carregar cookies")
        return False
    
    steam_id_64 = dict_cookies.get('steamLoginSecure', '').split('%7C%7C')[0]
    sess_id = dict_cookies.get('sessionid')
    
    if not steam_id_64 or not sess_id:
        print("❌ Cookies inválidos ou expirados.")
        return False
    
    sessao = requests.Session()
    for nome, valor in dict_cookies.items():
        sessao.cookies.set(nome, valor, domain='steamcommunity.com')
    
    id_exibicao, nome_perfil = buscar_dados_perfil(sessao, steam_id_64)
    
    try:
        fotos = [f for f in os.listdir(caminho_fotos) if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if not fotos:
            print("❌ Nenhuma imagem encontrada no diretório.")
            return False
        
        foto_escolhida = os.path.join(caminho_fotos, random.choice(fotos))
    except Exception as e:
        print(f"❌ Erro ao listar fotos: {e}")
        return False
    
    print(f"\n👤 [ID] {steam_id_64}")
    print(f"📸 [Avatar] {os.path.basename(foto_escolhida)}")
    print(f"🎮 [Usuário] {nome_perfil}")
    
    dados_upload = {
        "MAX_FILE_SIZE": "1048576",
        "type": "player_avatar_image",
        "sId": steam_id_64,
        "sessionid": sess_id,
        "doSub": "1"
    }
    
    cabecalhos = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://steamcommunity.com/profiles/{steam_id_64}/edit/avatar"
    }
    
    try:
        with open(foto_escolhida, 'rb') as f:
            arquivos = {'avatar': (os.path.basename(foto_escolhida), f, 'image/jpeg')}
            resposta = sessao.post(
                "https://steamcommunity.com/actions/FileUploader/",
                data=dados_upload,
                files=arquivos,
                headers=cabecalhos,
                timeout=10
            )
        
        print(f"\nConclusão: Cód. #{resposta.status_code}")
        
        if resposta.status_code == 200:
            res_minusculo = resposta.text.lower()
            if "error" not in res_minusculo:
                print("✅ Avatar alterado com sucesso!\n")
                return True
            else:
                print("❌ Falha ao fazer upload.\n")
                print(f"[DEBUG] Resposta: {resposta.text[:200]}")
                return False
        else:
            print(f"❌ Falha no upload (HTTP {resposta.status_code}).\n")
            return False
    
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False

if __name__ == "__main__":
    mudar_foto_steam()
