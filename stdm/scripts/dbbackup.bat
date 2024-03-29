 @echo off

 REM **************************
 REM DB Backup Script
 REM **************************

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
   set PGPASSWORD=%5
   set BACKUP_FOLDER=%6
   set PG_DB_DUMP_TOOL=%7
   set BACKUP_FILENAME=%8

   REM set log_file=%BACKUP_FOLDER%\backit.log

   REM set BACKUP_FILE="%BACKUP_FOLDER%\%DATABASE_NAME%_%datestr%.backup"
   echo backup file name is %BACKUP_FILENAME%
   echo on

   REM PAUSE

   %PG_DB_DUMP_TOOL% -h %PG_SERVER% -p %PG_PORT% -U %PG_USER% -F c -b -v -f %BACKUP_FILENAME% %DATABASE_NAME%

   timeout /t 3

