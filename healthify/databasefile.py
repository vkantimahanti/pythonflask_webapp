from datetime import datetime
import pyodbc
from flask import jsonify, Response
from healthify import app
from healthify import login_manager
from flask_login import UserMixin


DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'DESKTOP-CTMO71K'
DATABASE_NAME = 'StudentRecords'
username = 'python_test'
password = 'python_test'


def get_db_connection():
    try:
        connection = pyodbc.connect(f"DRIVER={{{DRIVER_NAME}}};"
                                    f"SERVER={SERVER_NAME};"
                                    f"DATABASE={DATABASE_NAME};"
                                    f"UID={username};"
                                    f"PWD={password};")

        connection.autocommit = True;

        print('connected to db')

        return connection
    except pyodbc.Error as ex:
        print('Connection Failed', ex)



def getdata(query):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Unable to connect to the database "}), 500

    cursor = connection.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            desc = cursor.description
            column_names = [col[0] for col in desc]

        return [dict(zip(column_names, row)) for row in rows]
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


def checkdata(query):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Unable to connect to the database "}), 500

    print("query sent as input ",query)
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        row = len(cursor.fetchall())
        print(row)
        return row

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


def postdata(username, email, password):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Unable to connect to the database "}), 500

    cursor = connection.cursor()
    try:
        query = f"insert into StudentRecords.dbo.healthifyRegistration (username,email, password) values ('{username}','{email}','{password}');"
        cursor.execute(query)
        rows = cursor.fetchall()

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


def updatedata(query):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Unable to connect to the database "}), 500

    cursor = connection.cursor()
    try:
        cursor.execute(query)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


class UserClass(UserMixin):
    def __init__(self, username, email, picdetails,  id, active=True):
        self.username = username
        self.email = email
        self.picdetails = picdetails
        self.id = id
        self.active = active

    def is_active(self):
        return self.active


def check_db(user_id):
    # check the userid in db
    query = f"select username, email, picdetails, password from StudentRecords.dbo.healthifyRegistration where id='{user_id}'"
    users = getdata(query)
    for item in users:
        uname = item["username"]
        email = item["email"]
        picdetails = item["picdetails"]
        pwd = item["password"]
    userobject = UserClass(uname,email, picdetails, user_id, active=True)
    if userobject.id == user_id:
        return userobject
    else:
        return None


@login_manager.user_loader
def load_user(id):
    return check_db(id)