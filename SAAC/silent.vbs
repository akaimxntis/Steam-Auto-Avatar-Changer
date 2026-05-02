Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c exec.bat", 0
Set WshShell = Nothing
