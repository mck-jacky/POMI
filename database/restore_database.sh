# CAUTION: shell script does not work if you are in the COMP3900 database in the terminal

dropdb COMP3900 2>/dev/null
createdb COMP3900

psql COMP3900 -f load_database.sql
