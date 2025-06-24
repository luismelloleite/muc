[Setup]
AppName=Portaria MUC UFCAT
AppVersion=0.0.1
AppPublisher=UFCAT
DefaultDirName={autopf}\Portaria MUC UFCAT
DefaultGroupName=Portaria MUC UFCAT
OutputBaseFilename=Portaria_MUC_UFCAT_Setup
SetupIconFile=logo.ico
Compression=lzma
SolidCompression=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "dist\Portaria MUC UFCAT.exe"; DestDir: "{app}"
Source: ".env"; DestDir: "{app}"; Check: FileExists('.env')
Source: "logo.ico"; DestDir: "{app}"; Check: FileExists('logo.ico')

[Icons]
Name: "{group}\Portaria MUC UFCAT"; Filename: "{app}\Portaria MUC UFCAT.exe"
Name: "{autodesktop}\Portaria MUC UFCAT"; Filename: "{app}\Portaria MUC UFCAT.exe"

[Run]
Filename: "{app}\Portaria MUC UFCAT.exe"; Description: "Executar Portaria MUC UFCAT"; Flags: nowait postinstall