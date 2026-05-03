---

# Steam Auto Avatar Changer 📸

Um script Python para mudar automaticamente sua foto de perfil do Steam, selecionando uma imagem aleatória de uma pasta local.

## 🚀 Características

*   **Upload Automatizado:** Faz upload de avatares diretamente nos servidores Steam.
*   **Seleção Aleatória:** Escolhe uma imagem aleatória de qualquer pasta.
*   **Suporte a HD Portátil:** Funciona com HD externo, pendrive, etc.
*   **Integração de Perfil:** Detecta automaticamente seu SteamID e apelido através dos cookies da sessão.
*   **Modo Invisível:** Pode rodar totalmente em background sem abrir janelas de terminal.

## 🛠️ Pré-requisitos

*   Python 3.x.
*   Biblioteca `requests`.

```bash
pip install requests
```

## 📋 Guia de Configuração

### 1. **Copie o arquivo de cookies Steam**

1. No seu navegador, instale a extensão **Cookie-Editor**.
2. Acesse [steamcommunity.com](https://steamcommunity.com) e faça login.
3. Use a extensão para **exportar os cookies em formato Netscape (.txt)**.
4. Salve o conteúdo como **`scookie.txt`** na pasta do script.

### 2. **Configure o caminho das fotos**

Edite o arquivo **`config.json`** (criado automaticamente na primeira execução):

```json
{
    "caminho_fotos": "C:\\Caminho\\Para\\Suas\\Fotos"
}
```

## ▶️ Como Executar

### Modo Visível (com console)
```bash
python SAAC.py
```

### Modo Silencioso (Background no Windows)
Para rodar sem abrir janelas de terminal, utilize o `pythonw`:
```bash
pythonw.exe "C:\Caminho\Para\O\Projeto\SAAC.py"
```

## 📸 Onde encontrar avatares

Você pode encontrar a coleção de avatares que eu utilizo no meu perfil do Pinterest:
*   **Pinterest:** [akaimxntis](https://www.pinterest.com/akaimxntis/) > [1:1](https://br.pinterest.com/Akaimxntis/11/)

## 📝 Estrutura de Arquivos

```bash
SAAC/
├── SAAC.py          # Script principal traduzido
├── config.json      # Configuração de caminhos
└── scookie.txt      # Cookies da sessão Steam (Mantenha privado!)
```

## 🔒 Segurança

⚠️ **IMPORTANTE:** Nunca compartilhe seu arquivo `scookie.txt`, pois ele contém seus cookies de autenticação do Steam. Se os cookies vazarem, delete o arquivo e gere um novo após trocar sua senha do Steam.

## 📱 Automação Avançada

### Raycast (Windows)
*   **Link:** `pythonw.exe "C:\Caminho\Para\O\Projeto\SAAC.py"`.
*   **Open With:** Default (não requer PowerShell).

### Unified Remote (Smartphone)
No seu arquivo `remote.lua`, utilize a função `shell.execute` para rodar de forma invisível:
```lua
shell.execute("pythonw.exe", "\"C:\\Caminho\\Para\\O\Projeto\\SAAC.py\"")
```

## 🐛 Solução de Problemas

*   **Erro: "Sessão expirada":** Seus cookies pararam de funcionar. Exporte-os novamente do navegador.
*   **Erro: "Diretório não encontrado":** Verifique se o caminho no `config.json` utiliza barras duplas `\\`.

---
**Última atualização:** maio/2026.
