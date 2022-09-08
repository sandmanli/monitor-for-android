@echo off

set ResultPath=C:\tmp\ActionsResult
for /f "skip=1 tokens=1 delims=." %%x in ('wmic os get localdatetime') do if not defined mydate set mydate=%%x
set ResultPath=%ResultPath%\%mydate%
if not exist %ResultPath% ( md %ResultPath% )
exe\adb.exe pull /data/local/tmp/monitor_run.log %ResultPath%\
exe\adb.exe pull /data/local/tmp/test %ResultPath%\
echo.
echo pullÍê³É£¬´æ´¢µ½=%ResultPath%
start explorer %ResultPath%
pause >nul
