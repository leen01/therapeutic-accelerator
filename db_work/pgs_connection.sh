psql --host=database-1.cuaho2dof33c.us-east-1.rds.amazonaws.com \
--port=5432 --username=postgres --password \
--dbname=postgres

\copy fulltext from '/home/ubuntu/work/bucket/fulltext/final_full_text.csv' WITH DELIMITER ',' CSV;
