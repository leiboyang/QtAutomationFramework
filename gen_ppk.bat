@echo off
"C:\Program Files\TortoiseGit\bin\puttygen.exe" "C:\Users\Bob\.ssh\id_ed25519" -o "C:\Users\Bob\.ssh\id_ed25519.ppk"
echo PPK conversion done
if exist "C:\Users\Bob\.ssh\id_ed25519.ppk" (
    echo PPK file created successfully!
) else (
    echo PPK file creation FAILED
)
