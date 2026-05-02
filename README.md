# Steam Auto Avatar Changer 📸

A Python script to automatically change your Steam profile picture by selecting a random image from a local folder.

## 🚀 Features
*   **Automated Upload:** Uploads avatars directly to Steam servers.
*   **Random Selection:** Picks a random image from a specified directory.
*   **Profile Integration:** Automatically detects your SteamID and Nickname through session cookies.

## 🛠️ Prerequisites
*   Python 3.x
*   `requests` library
```bash
pip install requests
```
## Open the scookie.txt file.
*   Paste your Steam cookie in Netscape format.
*   Save and run the script.

## 📱 Remote Execution & Shortcuts
This project is optimized for quick access and automation:
*   **Raycast:** You can link the `silent.vbs` to a Raycast "Quicklink" or script command for instant execution via keyboard shortcuts.
*   **Unified Remote:** By pointing a custom button to the `exec.bat` or `silent.vbs`, you can trigger a random avatar change directly from your smartphone.
*   **Silent Mode:** The use of VBScript ensures that the update happens in the background without interrupting your gaming or workflow.

## 📸 Where to find avatars
You can find the collection of avatars I use on my Pinterest profile:
*   **Pinterest:** [akaimxntis](https://www.pinterest.com/akaimxntis/) > [1:1](https://br.pinterest.com/Akaimxntis/11/)

## Follow these steps to set up **SAAC** on your PC:

1. **Avatars Path:**
   * Open the `SAAC.py` file (you can use Notepad).
   * Locate the line PHOTOS_PATH and place the path to your profile picture folder between the quotation marks, keeping the 'r' before them (e.g., r'C:\Photos\Avatars\').
2. **Get Cookies:**
   * In your browser (Chrome, Edge, or Firefox), install a cookie management extension (e.g., **Cookie-Editor**).
   * Access the Steam website, log in, go to your profile, and use the extension to copy or export the values ​​in Netscape (.txt).
3. **Configure scookie.txt:**
   * Open the `scookie.txt` file in the project folder and paste the cookies inside.
4. **Run:**
   * Run `exec.bat` to see the logs or `silent.vbs` to run it in the background (invisible).
