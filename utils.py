import pymysql

def get_connection():
    connection = pymysql.connect(
        host='localhost', user='root', password='', database='israel_chatu_emp_db')

    return connection
