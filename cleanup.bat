@echo off
rd /s /q "downloaded_images" 2>nul
del /f /q "messages.csv" 2>nul
del /f /q "messages_with_local_paths.json" 2>nul
echo 清理完成。
pause