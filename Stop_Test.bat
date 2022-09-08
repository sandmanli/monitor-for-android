@echo off
adb shell touch /data/local/tmp/stop
echo.
echo shell touch /data/local/tmp/stop
echo 已经创建stop，当前loop执行完成后脚本停止运行，稍等...
pause >nul
