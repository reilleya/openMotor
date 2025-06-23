[Setup]
AppName=openMotor
AppVersion=0.6.1
WizardStyle=modern
DefaultDirName={autopf}\openMotor
DefaultGroupName=openMotor
UninstallDisplayIcon={app}\openMotor.exe
Compression=lzma2
SolidCompression=yes
ChangesAssociations=yes

[Files]
Source: "../dist/openMotor/*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\openMotor"; Filename: "{app}\openMotor.exe"

[Registry]
; Associate .ric files with openMotor
Root: HKA; Subkey: "Software\Classes\.ric\OpenWithProgids"; ValueType: string; ValueName: "openMotor.ric"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\openMotor.ric"; ValueType: string; ValueName: ""; ValueData: "openMotor Motor File"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\openMotor.ric\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\resources\oMFile256.ico"
Root: HKA; Subkey: "Software\Classes\openMotor.ric\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\openMotor.exe"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\openMotor.exe\SupportedTypes"; ValueType: string; ValueName: ".ric"; ValueData: ""
