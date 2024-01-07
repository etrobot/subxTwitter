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

def insert_data(table_name, data):
    columns = ', '.join(data.keys())
    placeholders = ', '.join(':' + key for key in data.keys())
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, data)
    cursor.connection.commit()

def delete_data(table_name, condition):
    query = f"DELETE FROM {table_name} WHERE {condition}"
    cursor.execute(query)
    cursor.connection.commit()

def select_data(table_name, columns='*', condition=None,**kwargs):
    query = f"SELECT {columns} FROM {table_name}"
    if condition:
        query += f" WHERE {condition}"
        cursor.execute(query,kwargs)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    return result


def select_data_as_dataframe(table_name, columns='*', condition=None, **kwargs):
    query = f"SELECT {columns} FROM {table_name}"
    if kwargs:
        sql_query = f"{query} WHERE {condition}"
        cursor.execute(sql_query, kwargs)
    else:
        cursor.execute(query)

    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    return df


def update_data(table_name, condition,**kwargs):
    query = f"UPDATE {table_name} {condition}"
    cursor.execute(query, kwargs)
    cursor.connection.commit()


def setExpDate(table='users',days=7, email=None):
    expire_date = datetime.utcnow() + timedelta(days=days)
    sql = f"UPDATE {table} SET expire_date = :expire_date"
    params = {'expire_date': expire_date}
    if email:
        sql += " WHERE email = :email"
        params['email'] = email
    cursor.execute(sql, params)
    cursor.connection.commit()


if __name__=='__main__':
    setExpDate()
    pd.set_option('display.max_columns', None)
    df=select_data_as_dataframe('users')
    print(df)
