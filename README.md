# Steam Auto Avatar Changer 📸

Um script Python para mudar automaticamente sua foto de perfil do Steam, selecionando uma imagem aleatória de uma pasta local.

## 🚀 Características

- **Upload Automatizado:** Faz upload de avatares diretamente nos servidores Steam
- **Seleção Aleatória:** Escolhe uma imagem aleatória de qualquer pasta
- **Suporte a HD Portátil:** Funciona com HD externo, pendrive, etc.
- **Integração de Perfil:** Detecta automaticamente seu SteamID e apelido através dos cookies da sessão
- **Busca Recursiva (Opcional):** Pode procurar em subpastas também

## 🛠️ Pré-requisitos

- Python 3.x
- Biblioteca `requests`

```bash
pip install requests
```

## 📋 Guia de Configuração

### 1. **Copie o arquivo de cookies Steam**

1. No seu navegador (Chrome, Edge ou Firefox), instale uma extensão de gerenciamento de cookies (ex: **Cookie-Editor**)
2. Acesse o site do Steam: https://steamcommunity.com
3. Faça login na sua conta
4. Vá ao seu perfil
5. Use a extensão para **copiar os cookies em formato Netscape (.txt)**
6. Cole o conteúdo no arquivo **`scookie.txt`** dentro da pasta do projeto

### 2. **Configure o caminho das fotos**

Edite o arquivo **`config.json`** e configure o caminho das suas fotos:

#### 📁 Exemplos de caminhos

**Windows - HD Interno:**
```json
{
    "photos_path": "C:\\Users\\SeuUser\\Pictures",
    "recursive_search": false
}
```

**Windows - HD Portátil (E:):**
```json
{
    "photos_path": "E:\\Meus Avatares",
    "recursive_search": false
}
```

**Windows - Pendrive:**
```json
{
    "photos_path": "F:\\Avatares",
    "recursive_search": false
}
```

**Windows - Rede:**
```json
{
    "photos_path": "\\\\Computador\\Compartilhado\\Avatares",
    "recursive_search": false
}
```

**Linux/Mac - HD Interno:**
```json
{
    "photos_path": "/home/user/Pictures",
    "recursive_search": false
}
```

**Linux/Mac - HD Portátil:**
```json
{
    "photos_path": "/media/user/HD_Externo/Avatares",
    "recursive_search": false
}
```

### 3. **Habilitar busca recursiva (opcional)**

Se suas fotos estão em subpastas, altere para `true`:

```json
{
    "photos_path": "E:\\Avatares",
    "recursive_search": true
}
```

## ▶️ Como Executar

### Modo Visível (com log no console)

```bash
python SAAC.py
```

### Modo Silencioso (background)

**Windows:**
```bash
cscript.exe silent.vbs
```

## 📝 Estrutura de Arquivos

```
SAAC/
├── SAAC.py              # Script principal
├── config.json          # Configuração (edite aqui!)
├── scookie.txt          # Seus cookies Steam (mantenha privado!)
├── silent.vbs           # Script para executar em background (Windows)
├── exec.bat             # Script batch (Windows)
└── saac.log             # Log de execução
```

## 🔒 Segurança

⚠️ **IMPORTANTE:** 
- Nunca compartilhe seu arquivo `scookie.txt` - ele contém seus cookies de autenticação
- Mantenha o arquivo em local seguro
- Se suspeitar que seus cookies foram comprometidos, delete-os e obtenha novos

## 📸 Onde encontrar avatares

Você pode encontrar a coleção de avatares que eu utilizo no meu perfil do Pinterest:
*   **Pinterest:** [akaimxntis](https://www.pinterest.com/akaimxntis/) > [1:1](https://br.pinterest.com/Akaimxntis/11/)

**Formatos suportados:** PNG, JPG, JPEG, BMP

## 📱 Automação Avançada

### Raycast (Mac)

Crie um script Raycast que execute o `SAAC.py` com um atalho de teclado

### Unified Remote (Smartphone)

Configure um botão personalizado que aponte para `silent.vbs` ou `exec.bat`

### Windows Task Scheduler

Agende a execução automática em horários específicos

## 🐛 Solução de Problemas

**Erro: "Diretório não encontrado"**
- Verifique se o caminho no `config.json` está correto
- Se é um HD portátil, verifique se está conectado
- Tente usar o caminho absoluto completo

**Erro: "Sem permissão para acessar"**
- Verifique as permissões da pasta
- Tente executar como administrador

**Erro: "Nenhuma imagem encontrada"**
- Coloque arquivos de imagem (PNG, JPG, JPEG, GIF, BMP) na pasta
- Se usar `recursive_search: true`, as imagens podem estar em subpastas

**Erro: "Session ID não encontrado"**
- Seus cookies estão expirados
- Obtenha novos cookies e atualize o `scookie.txt`

## 📊 Log de Execução

Cada execução gera um log em `saac.log` com todos os detalhes da operação.

## 📄 Licença

Este projeto está disponível para uso pessoal.

---

**Última atualização:** maio/2026
