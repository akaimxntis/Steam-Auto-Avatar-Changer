# Steam Auto Avatar Changer 📸

A Python script to automatically change your Steam profile picture by selecting a random image from a local folder.

## 🚀 Features

*   **Automated Upload:** Uploads avatars directly to Steam servers.
*   **Random Selection:** Picks a random image from any folder.
*   **Portable Storage Support:** Works with external HDDs, USB drives, etc.
*   **Profile Integration:** Automatically detects your SteamID and nickname via session cookies.
*   **Invisible Mode:** Can run fully in the background without opening terminal windows.

## 🛠️ Prerequisites

*   Python 3.x.
*   `requests` library.

```bash
pip install requests
```

## 📋 Setup Guide

### 1. **Copy Steam Cookies**

1.  In your browser, install the **Cookie-Editor** extension.
2.  Go to [steamcommunity.com](https://steamcommunity.com) and log in.
3.  Use the extension to **export cookies in Netscape format (.txt)**.
4.  Save the content as **`scookie.txt`** in the script folder.

### 2. **Configure Photo Path**

Edit the **`config.json`** file (automatically created on the first run):

```json
{
    "caminho_fotos": "C:/Path/To/Your/Photos"
}
```

## ▶️ How to Run

### Visible Mode (with console)
```bash
python SAAC.py
```

### Silent Mode (Background on Windows)
To run without opening terminal windows, use `silent.vbs`

## 📸 Where to Find Avatars

You can find the avatar collection I use on my Pinterest profile:
*   **Pinterest:** [akaimxntis](https://www.pinterest.com/akaimxntis/) > [1:1](https://br.pinterest.com/Akaimxntis/11/)

## 📝 File Structure

```text
SAAC/
├── SAAC.py          # Main script (translated)
├── config.json      # Path configuration
└── scookie.txt      # Steam session cookies (Keep it private!)
```

## 🔒 Security

⚠️ **IMPORTANT:** Never share your `scookie.txt` file, as it contains your Steam authentication cookies. If the cookies are leaked, delete the file and generate a new one after changing your Steam password.

## 📱 Advanced Automation

### Raycast (Windows)
*   **Link:** `pythonw.exe "C:\Path\To\The\Project\SAAC.py"`.
*   **Open With:** Default (PowerShell is not required).

### Unified Remote (Smartphone)
In your `remote.lua` file, use the `shell.execute` function to run invisibly:
```lua
shell.execute("pythonw.exe", "\"C:\\Path\\To\\The\\Project\\SAAC.py\"")
```

## 🐛 Troubleshooting

*   **Error: "Session expired":** Your cookies have stopped working. Export them again from the browser.
*   **Error: "Directory not found":** Ensure the path in `config.json` uses double backslashes `\\`.

---
**Last updated:** May/2026.
