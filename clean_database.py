import sqlite3

con = sqlite3.connect('/opt/lnetd/web_app/database.db')
cursor = con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
all_tables = cursor.fetchall()

dont_delete = ['User','App_config']
delete_tables = [ table[0] for table in all_tables if table[0] not in dont_delete]
for table in delete_tables:
    qry = f'delete from {table};'
    cursor.execute(qry)
    con.commit()
