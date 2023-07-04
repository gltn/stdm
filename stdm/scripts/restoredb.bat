 @echo off

 REM ***********************
 REM Restore DB Script
 REM ***********************

   set DATABASE_NAME=%1
   set PG_SERVER=%2
   set PG_PORT=%3
   set PG_USER=%4
   set PGPASSWORD=%5
   set PG_RESTOREDB_TOOL=%6
   set BACKUP_FILENAME="%7"
   set SCRIPT_FOLDER=%8

   set log_file=%SCRIPT_FOLDER%restore.log
   echo %log_file%

   echo on

   REM PAUSE

  @REM  echo DATABASE_NAME=%DATABASE_NAME% >> %log_file%
  @REM  echo PG_SERVER=%PG_SERVER% >> %log_file%
  @REM  echo PG_PORT=%PG_PORT% >> %log_file%
  @REM  echo PG_USER=%PG_USER% >> %log_file%
  @REM  echo PASSWORD=%PGPASSWORD% >> %log_file%
  @REM  echo RESTORE TOOL=%PG_RESTOREDB_TOOL% >> %log_file%
  @REM  echo BACKUP FILENAME=%BACKUP_FILENAME% >> %log_file%
  @REM  echo SCRIPT FOLDER=%SCRIPT_FOLDER% >> %log_file%

  set rest_cmd=%PG_RESTOREDB_TOOL% -h %PG_SERVER% -p %PG_PORT% -U %PG_USER% -d %DATABASE_NAME% --clean %BACKUP_FILENAME%

  REM echo "" >> %log_file%
  REM echo %rest_cmd% >>%log_file%

 %rest_cmd% 

 timeout /t 3

