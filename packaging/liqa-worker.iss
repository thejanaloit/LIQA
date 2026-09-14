; LIQA Worker Inno installer (build with Inno Setup).
[Setup]
AppName=LIQA Worker
AppVersion=0.1.0
DefaultDirName={autopf}\LIQA
PrivilegesRequired=lowest
OutputBaseFilename=LIQA-Worker-Setup
[Files]
Source: "..\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion; Excludes: ".env,secrets,captures,vendor,.git"
[Icons]
Name: "{autoprograms}\LIQA Worker"; Filename: "py.exe"; Parameters: """{app}\apps\worker\api.py"""
[Run]
Filename: "powershell.exe"; Parameters: "-File ""{app}\scripts\register-logon-task.ps1"""; Flags: runasoriginaluser
[UninstallRun]
Filename: "powershell.exe"; Parameters: "-File ""{app}\scripts\wipe.ps1"""; Flags: runhidden
