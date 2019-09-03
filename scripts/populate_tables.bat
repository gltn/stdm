REM create database for relevant authority
echo off
REM parameters
SET DB_NAME=flts
SET PG_VERSION=11
SET PG_PORT=5335
SET PG_USER=postgres
SET PG_HOST=localhost
SET SCR="%USERPROFILE%\.qgis2\python\plugins\stdm\scripts\populate_tables.sql"
SET STDM_HOME="%USERPROFILE%\.qgis2\python\plugins\stdm"

echo.
SET PSQL_DIR="C:\Program Files\PostgreSQL\%PG_VERSION%\bin\"
REM SET PSQL_DIR="C:\Program Files (x86)\PostgreSQL\%PG_VERSION%\bin\"
echo %PSQL_DIR%
cd /d %PSQL_DIR%
echo Attempting to populate tables...
psql.exe -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -d %DB_NAME% -a -f %SCR%
cd %STDM_HOME%
echo Done
