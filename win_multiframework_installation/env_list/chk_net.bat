@echo off
:loop
cls
Ping www.google.com -n 1 -w 1000 >nul 2>&1
if errorlevel 1 (
	echo You are not connected to the internet
	echo Please connect to the Internet and click any button to continue.
	pause >nul 2>&1
	goto loop
) else (
	echo You are connected to the internet
)
