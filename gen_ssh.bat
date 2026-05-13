@echo off
D:\APPAz\git\Git\usr\bin\ssh-keygen.exe -t ed25519 -C 941884293@qq.com -f C:\Users\Bob\.ssh\id_ed25519 -N ""
echo SSH key generation complete!
type C:\Users\Bob\.ssh\id_ed25519.pub
