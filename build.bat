@echo off
setlocal enabledelayedexpansion

:: Define paths
set "build_path=nsi_build"
set "input_path=nsi_inputfiles"
set "buildNumberFile=build_number.txt"

:: Ensure the build and input paths exist
if not exist "%build_path%" mkdir "%build_path%"
if not exist "%input_path%" mkdir "%input_path%"

:: Increment the build number
if not exist "%buildNumberFile%" echo 0 > "%buildNumberFile%"
set /p buildNumber=<"%buildNumberFile%"
set /a buildNumber+=1
echo !buildNumber! > "%buildNumberFile%"

:: Compile Python script
echo Compiling Python script...
pyinstaller --noconsole --onefile --distpath "%input_path%" --name telebot.exe main.py
if errorlevel 1 (
    echo Python compilation failed. Exiting...
    exit /b 1
) else (
    echo Python compilation successful.
)

:: Compile NSIS installer
echo Compiling NSIS installer...
makensis -DOUTFILE="%build_path%\telebot_setup_!buildNumber!.exe" -DBUILD_NUMBER=!buildNumber! build.nsi
if errorlevel 1 (
    echo NSIS compilation failed. Exiting...
    exit /b 1
) else (
    echo NSIS compilation successful.
)

:: Ask user to run the setup
set /p runSetup="Do you want to run the setup now? (y/n): "
if /i "%runSetup%"=="y" (
    echo Running the setup...
    start "" "%build_path%\telebot_setup_!buildNumber!.exe"
) else (
    echo Setup will not run.
)

echo Done.

endlocal
