@echo off
echo Restructuring project...

REM Move all frontend files
move tsconfig.json frontend\ 2>nul
move next.config.mjs frontend\ 2>nul
move components.json frontend\ 2>nul
move postcss.config.mjs frontend\ 2>nul
move next-env.d.ts frontend\ 2>nul

REM Move root files to proper locations
move README.md .\ 2>nul
move ARCHITECTURE.md .\ 2>nul
move SUBMISSION.md .\ 2>nul
move setup.py .\ 2>nul

REM Clean up old directories
rmdir /s /q app 2>nul
rmdir /s /q components 2>nul
rmdir /s /q hooks 2>nul
rmdir /s /q lib 2>nul
rmdir /s /q public 2>nul
rmdir /s /q styles 2>nul

echo Done!