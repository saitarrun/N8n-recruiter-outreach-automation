' Recruiter Outreach Platform - Silent Windows Background Launcher
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
projectDir = fso.GetParentFolderName(scriptDir)

' Run start.bat silently in background (0 = hide window, False = don't wait)
WshShell.CurrentDirectory = projectDir
WshShell.Run "cmd /c """ & projectDir & "\start.bat""", 0, False
