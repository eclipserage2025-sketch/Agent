; Inno Setup Script for AI-Litecoin-Miner-Ultra
[Setup]
AppName=AI-Litecoin-Miner-Ultra
AppVersion=1.0.0
DefaultDirName={pf}\AI-Litecoin-Miner-Ultra
DefaultGroupName=AI-Litecoin-Miner-Ultra
UninstallDisplayIcon={app}\AI-Litecoin-Miner-Ultra.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=AI-Litecoin-Miner-Ultra-Setup
PrivilegesRequired=admin

[Files]
Source: "dist\AI-Litecoin-Miner-Ultra\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AI-Litecoin-Miner-Ultra"; Filename: "{app}\AI-Litecoin-Miner-Ultra.exe"
Name: "{commondesktop}\AI-Litecoin-Miner-Ultra"; Filename: "{app}\AI-Litecoin-Miner-Ultra.exe"
; Add to Startup
Name: "{commonstartup}\AI-Litecoin-Miner-Ultra"; Filename: "{app}\AI-Litecoin-Miner-Ultra.exe"; Parameters: "--gui"

[Run]
Filename: "{app}\AI-Litecoin-Miner-Ultra.exe"; Description: "Launch AI Litecoin Miner Ultra"; Flags: nowait postinstall skipifsilent
