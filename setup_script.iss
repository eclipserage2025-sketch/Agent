; Inno Setup Script for AI Litecoin Miner
[Setup]
AppName=AI Litecoin Miner
AppVersion=3.0
DefaultDirName={autopf}\AI Litecoin Miner
DefaultGroupName=AI Litecoin Miner
UninstallDisplayIcon={app}\AI-Litecoin-Miner.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=AI_Litecoin_Miner_Setup

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\AI-Litecoin-Miner\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AI Litecoin Miner"; Filename: "{app}\AI-Litecoin-Miner.exe"; Parameters: "--gui"
Name: "{group}\{cm:UninstallProgram,AI Litecoin Miner}"; Filename: "{unindisplay}"
Name: "{autodesktop}\AI Litecoin Miner"; Filename: "{app}\AI-Litecoin-Miner.exe"; Parameters: "--gui"; Tasks: desktopicon

[Run]
Filename: "{app}\AI-Litecoin-Miner.exe"; Parameters: "--gui"; Description: "{cm:LaunchProgram,AI Litecoin Miner}"; Flags: nowait postinstall skipifsilent
