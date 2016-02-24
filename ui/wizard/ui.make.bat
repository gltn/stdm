@echo off
if [%1]==[] goto usage

set src="%1"
set ext=.py

call set out=%%src:.ui=%ext%%%
call pyuic4.bat %src% -o %out%
copy /Y %out% ..\..\..\..\sandbox\
goto :eof

:usage
@echo Usage: %0 ^<ui_file.ui^>
exit /B 1
