@echo off&&setlocal enabledelayedexpansion
chcp 936 >nul
cd  %~dp0


set scripts_path=/data/local/tmp
exe\adb.exe root
exe\adb.exe wait-for-device

exe\adb.exe push busybox %scripts_path%
exe\adb.exe shell chmod 755 %scripts_path%/busybox
exe\adb.exe push monitor.sh %scripts_path%
exe\adb.exe shell <command

echo 完成后台执行，任意键退出
pause >nul
exit
