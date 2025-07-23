@echo off
echo Disconnecting old connections...
adb disconnect
echo Setting up connected device
adb tcpip 5555
echo Waiting for device to initialize
timeout 10

rem Extract the IP address dynamically from wlan0
FOR /F "tokens=2" %%G IN ('adb shell ip addr show wlan0 ^| find "inet " ') DO set ipfull=%%G
FOR /F "tokens=1 delims=/" %%G in ("%ipfull%") DO set DEVICE_IP=%%G

echo Connecting to device with dynamically obtained IP %DEVICE_IP%...
adb connect %DEVICE_IP%:5555

rem Check if the connection was successful
if %errorlevel% neq 0 (
    echo Failed to connect to device at %DEVICE_IP%.
) else (
    echo Successfully connected to %DEVICE_IP%.
)

rem Add a second device IP if needed
rem set SECONDARY_IP=192.168.1.128
rem adb connect %SECONDARY_IP%:5555
