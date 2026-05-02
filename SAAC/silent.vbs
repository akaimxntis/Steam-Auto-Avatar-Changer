Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strPath = fso.GetParentFolderName(WScript.ScriptFullName)

WshShell.Run Chr(34) & strPath & "\exec.bat" & Chr(34), 0

Set WshShell = Nothing
Set fso = Nothing
