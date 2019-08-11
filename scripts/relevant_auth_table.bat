REM create database for relevant authority
echo off

SET DB_NAME=flts
SET TBL_NAME=cb_relevant_authority
SET PG_VERSION=11
SET PG_PORT=5433
SET PG_USER=postgres
SET PG_HOST=localhost
SET SCR="%USERPROFILE%\.qgis2\python\plugins\stdm\scripts\cb_relevant_authority.sql"

echo.
SET PSQL_DIR="C:\Program Files\PostgreSQL\%PG_VERSION%\bin\"
REM SET PSQL_DIR="C:\Program Files (x86)\PostgreSQL\%PG_VERSION%\bin\"
echo %PSQL_DIR%
cd /d %PSQL_DIR%
echo Attempting to create %TBL_NAME% database...
psql.exe -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -d %DB_NAME% -a -f %SCR%
echo Done