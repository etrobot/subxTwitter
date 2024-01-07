import pandas as pd
from datetime import datetime,timedelta
import oracledb

cs='(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-sanjose-1.oraclecloud.com))(connect_data=(service_name=g6587d1fcad5014_subxtwitter_medium.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'
conn=oracledb.connect(
     user="ADMIN",
     password='Gnpw#0755#OC',
     dsn=cs)

# Create a cursor object
cursor = conn.cursor()

def insert_data(cursor, table_name, data):
    columns = ', '.join(data.keys())
    placeholders = ', '.join(':' + key for key in data.keys())
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, data)
    cursor.connection.commit()

def delete_data(cursor, table_name, condition):
    query = f"DELETE FROM {table_name} WHERE {condition}"
    cursor.execute(query)
    cursor.connection.commit()

def select_data(cursor, table_name, columns='*', condition=None):
    query = f"SELECT {columns} FROM {table_name}"
    if condition:
        query += f" WHERE {condition}"
    cursor.execute(query)
    result = cursor.fetchall()
    return result
def select_data_as_dataframe(cursor, table_name, columns='*', condition=None):
    query = f"SELECT {columns} FROM {table_name}"
    if condition:
        query += f" WHERE {condition}"
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    return df

def update_data(cursor, table_name, data, condition):
    set_clause = ', '.join(f"{key} = :{key}" for key in data.keys())
    query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
    cursor.execute(query, data)
    cursor.connection.commit()


def setExpDate(cursor, table='users',days=7, email=None):
    expire_date = datetime.now() + timedelta(days=days)
    sql = f"UPDATE {table} SET expire_date = :expire_date"
    params = {'expire_date': expire_date}
    if email:
        sql += " WHERE email = :email"
        params['email'] = email
    cursor.execute(sql, params)
    cursor.connection.commit()
    conn.close()



setExpDate(cursor)
pd.set_option('display.max_columns', None)
df=select_data_as_dataframe(cursor,'users')
print(df)
