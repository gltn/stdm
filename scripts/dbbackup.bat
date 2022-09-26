 @echo off
   for /f "tokens=1-4 delims=/-" %%i in ("%date%") do (
     set dow=%%i
     set month=%%j
     set year=%%k
   )
   echo DOW:%dow%
   echo DAY:%day%
   echo MONTH:%month%
   echo YEAR:%year%

   For /f "tokens=1-2 delims=/:" %%a in ("%TIME%") do (set currtime=%%a%%b)

   set datestr=%dow%%month%%year%%currtime%
   echo datestr is %datestr%

   set DATABASE_NAME=%1
   set PG_SERVER=%2
   set PG_PORT=%3
   set PG_USER=%4
   set PGPASSWORD=abc123
   set BACKUP_FOLDER=%5

   REM set BACKUP_FILE="%BACKUP_FOLDER%%DATABASE_NAME%_%datestr%.backup"
   set BACKUP_FILE=%BACKUP_FOLDER%
   echo backup file name is %BACKUP_FILE%
   echo on

   REM PAUSE

   "C:\Program Files\PostgreSQL\14\bin\pg_dump.exe" -h %PG_SERVER% -p %PG_PORT% -U %PG_USER% -F c -b -v -f %BACKUP_FILE% %DATABASE_NAME%

