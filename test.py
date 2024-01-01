import datetime

import oracledb

cs='(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-sanjose-1.oraclecloud.com))(connect_data=(service_name=g6587d1fcad5014_subxtwitter_medium.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'
conn=oracledb.connect(
     user="ADMIN",
     password='Gnpw#0755#OC',
     dsn=cs)

# Create a cursor object
cursor = conn.cursor()

# Define the SQL query to create the 'users' table
# sql = """
# CREATE TABLE users (
#   email VARCHAR2(255) NOT NULL,
#   target_id VARCHAR2(255) NOT NULL,
#   lang VARCHAR2(10) NOT NULL,
#   mail_time TIMESTAMP NOT NULL,
#   expire_date TIMESTAMP NOT NULL,
#   PRIMARY KEY (email)
# )
# """

# sql='''
# alter table users
# modify( "timstamp"  TIMESTAMP NOT NULL)
# '''


# sql='''ALTER TABLE users ADD ( "lang" VARCHAR(10) NOT NULL)'''


# sql = """
# DELETE FROM users
# WHERE email = 'd361@qq.com'
# """

# Execute the query
# cursor.execute(sql)
#
# # Commit the changes
# conn.commit()

# # Close the cursor and connection when done
# cursor.close()
# conn.close()

# # Close the cursor and connection
# cursor.close()
# connection.close()

# Define the SQL query
# sql_query = """
# SELECT * FROM users
# WHERE email = 'd361@qq.com'
# """
sql_query = 'SELECT * FROM users'
# Execute the query
cursor.execute(sql_query)

# Fetch all rows from the result set
rows = cursor.fetchall()

# Print the results
for row in rows:
    print(row)

# # Define the values to be inserted
# email = 'd361@qq.com'
# id = '@elonmusk;'
# mail_time =  datetime.datetime.now()
# expire_date = datetime.datetime.now() + datetime.timedelta(days=90)
# lang='zh-CN'
#
# # Define the SQL query to insert the values into the 'users' table
# sql = """
# INSERT INTO users (email, target_id, mail_time, expire_date,lang)
# VALUES (:email, :target_id, :mail_time, :expire_date, :lang)
# """
#
# # Execute the query with the values as parameters
#cursor.execute(sql, email=email, target_id=target_id, mail_time=mail_time, expire_date=expire_date, lang=lang)

# Commit the changes to the database
conn.commit()

# Close the cursor and connection when done
cursor.close()
conn.close()
