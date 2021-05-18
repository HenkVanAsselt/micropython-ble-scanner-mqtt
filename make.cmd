@echo off

rem -----------------------------------------------------------------------
rem Check command line parameters
rem -----------------------------------------------------------------------
if "%1"==""   goto usage
if "%1"=="?"  goto usage
if "%1"=="-?" goto usage
if "%1"=="-h" goto usage
if "%1"=="--help" goto usage
goto %1
goto _eof

:usage
echo -----------------------------------------------------------------
echo Micropython BLE Scanner MQTT - makefile
echo -----------------------------------------------------------------
echo make pylint        Run pylint on the whole source folder
echo make flake8        Run flake 8 on the whole source folder
echo make vulture       Find dead code
echo.
echo make pip           Install all (updated) requirements.
echo make clean         Clean up temporary file
echo.
echo make sphinx        Generate sphinx user documentation
echo make apidoc        Generate sphinx api documentation
echo make doxygen       Make doxygen documentation
echo.
goto _eof


rem --- Run pylint
:pylint
    pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" -r n -d E0611,R0201,C0301 --extension-pkg-whitelist=win32api --ignore=esp32shell_qt_design.py src
    goto _eof

rem --- Run flake8 
:flake8
    flake8 --exclude=bin,upython_sources,lib,tests,*_qt_design*,doc --max-line-length=140 --ignore=
    goto _eof

rem --- Run vulture to detect unused functions and/or variables
:vulture
    vulture.cmd
    goto _eof

rem --- Update Python libraries (using requirements.txt)
:pip
    python.exe -m pip install --upgrade pip
    pip install -r requirements.txt --upgrade
    goto _eof


rem --- Generate DOXYGEN documentation
:doxygen
    call doxygen 
    goto _eof
	
:show_doxygen
	rem "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" .\doc\doxygen\html\index.html
	start ./docs/doxygen/html/index.html
	goto _eof

:sphinx
    pushd docs & call make html & popd
    rem "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" .\doc\_build\html\index.html
	start ./docs/_build/html/index.html
    goto _eof
    
:apidoc
    sphinx-apidoc -o ./docs/_modules ./src/esp32
    goto _eof

:clean
    pushd src & rmdir /S /Q __pycache__ & popd
    pushd src & rmdir /S /Q .pytest_cache & popd
    pushd docs\doxygen & rmdir /S /Q html & popd
    pushd docs & make clean & popd

:_eof