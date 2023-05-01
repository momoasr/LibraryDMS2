# Library Database Management System - create_db file- CMSC 495 group 3

# run this file to create all tables and load the book and bookcopy tables with data from the
# bookdata.csv and bookcopydata.csv files

import mysql.connector
import pandas as pd
from datetime import datetime

host = 'localhost'
user = 'root'
db_password = 'Y&suMokonzi@2023'
schema = 'library'

try:
    connection = mysql.connector.connect(host=host,
                                         user=user,
                                         password=db_password)

    cursor = connection.cursor()

    cursor.execute('CREATE DATABASE library')

except mysql.connector.Error as error:
    print("Failed{}".format(error))

finally:
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")

# # create unfilled tables in database
# try:
#     connection = mysql.connector.connect(host=host,
#                                          database=schema,
#                                          user=user,
#                                          password=db_password)

#     cursor = connection.cursor()

#     # drop the memberpass table if it already exists so we can re-add
#     cursor.execute('DROP TABLE IF EXISTS memberpass;')

#     print('Creating memberpass table....')
#     # the below line creates the memberpass table and specifies the fields in the table
#     cursor.execute("CREATE TABLE memberpass (card_number int NOT NULL, hashedpw char(60),"
#                    "PRIMARY KEY (card_number))")

#     # drop the admin table if it already exists so we can re-add
#     cursor.execute('DROP TABLE IF EXISTS admin;')

#     print('Creating admin table....')
#     # the below line creates the admin table and specifies the fields in the table
#     cursor.execute("CREATE TABLE admin (admin_id int NOT NULL, first_name varchar(255), last_name varchar(255),"
#                    "PRIMARY KEY (admin_id))")

#     # # drop the adminpass table if it already exists so we can re-add
#     cursor.execute('DROP TABLE IF EXISTS adminpass;')

#     print('Creating adminpass table....')
#     # the below line creates the adminpass table and specifies the fields in the table
#     cursor.execute("CREATE TABLE adminpass (admin_id int NOT NULL, hashedpw char(60),"
#                    "PRIMARY KEY (admin_id))")

#     # drop the members table if it already exists so we can re-add
#     cursor.execute('DROP TABLE IF EXISTS members;')

#     print('Creating members table....')
#     # the below line creates the book table and specifies the fields in the table
#     cursor.execute("CREATE TABLE members (card_number int NOT NULL, first_name varchar(255), last_name varchar(255),"
#                    "birth_date date, email_address varchar(255), status varchar(255), copy_id int,"
#                    "PRIMARY KEY (card_number))")

#     cursor.close()

# except mysql.connector.Error as error:
#     print("Failed {}".format(error))

# finally:
#     if connection.is_connected():
#         connection.close()
#         print("MySQL connection is closed")

# checkout = pd.read_csv('checkout.csv', index_col=False, delimiter=',')
# checkout.head()
# try:
#     connection = mysql.connector.connect(host=host, database=schema, user=user, password=db_password)
#     cursor = connection.cursor()
#     # drop the checkout table if it already exists so we can re-add
#     cursor.execute('DROP TABLE IF EXISTS checkout;')

#     print('Creating checkout table....')
#     # the below line creates the checkout table and specifies the fields in the table
#     cursor.execute("CREATE TABLE checkout (copy_id int NOT NULL, checkout_date date, return_date date,"
#                    "PRIMARY KEY (copy_id))")
#     # loop through the data from the csv file and enter each line as a row in the table
#     format_data = "%m/%d/%Y"
#     for i, row in checkout.iterrows():
#         record = (row[0], (datetime.strptime(row[1], format_data)).date(), (datetime.strptime(row[2], format_data)).date())
#         sql = "INSERT INTO checkout VALUES (%s,%s,%s)"
#         cursor.execute(sql, record)
#         connection.commit()
#         print(record)

#     print("Records inserted successfully into checkout table")
#     cursor.close()

# except mysql.connector.Error as error:
#     print("Failed to insert record into checkout table {}".format(error))

# finally:
#     if connection.is_connected():
#         connection.close()
#         print("MySQL connection is closed")

# # read bookdata csv file
# bookdata = pd.read_csv('bookdata.csv', index_col=False, delimiter=',')
# bookdata.head()
# # book table data insert
# try:
#     connection = mysql.connector.connect(host=host, database=schema, user=user, password=db_password)
#     cursor = connection.cursor()

#     # drop the book table if it already exists so we can re-add
#     cursor.execute('DROP TABLE IF EXISTS book;')

#     print('Creating book table....')
#     # the below line creates the book table and specifies the fields in the table
#     cursor.execute("CREATE TABLE book (book_id varchar(255) NOT NULL, title varchar(255), author varchar(255),"
#                    "genre varchar(255), PRIMARY KEY (book_id))")

#     # loop through the data from the csv file and enter each line as a row in the table
#     for i, row in bookdata.iterrows():
#         sql = "INSERT INTO book VALUES (%s,%s,%s,%s)"
#         cursor.execute(sql, tuple(row))
#         connection.commit()
#         print(tuple(row))

#     print("Records inserted successfully into book table")
#     cursor.close()

# except mysql.connector.Error as error:
#     print("Failed to insert record into book table {}".format(error))

# finally:
#     if connection.is_connected():
#         connection.close()
#         print("MySQL connection is closed")

# # read bookcopydata csv file
# bookcopydata = pd.read_csv('bookcopydata.csv', index_col=False, delimiter=',')
# bookcopydata.head()

# # bookcopy table data insert
# try:
#     connection = mysql.connector.connect(host=host,
#                                          database=schema,
#                                          user=user,
#                                          password=db_password)

#     cursor = connection.cursor()

#     # drop the bookcopy table if it already exists so we can re-add
#     cursor.execute('DROP TABLE IF EXISTS bookcopy;')

#     print('Creating bookcopy table....')
#     # the below line creates the bookcopy table and specifies the fields in the table
#     cursor.execute("CREATE TABLE bookcopy (copy_id varchar(255) NOT NULL, book_id varchar(255) NOT NULL, "
#                    "media_type varchar(255), checkout_status varchar(255),"
#                    "PRIMARY KEY (copy_id))")

#     # loop through the data from the csv file and enter each line as a row in the table
#     for i, row in bookcopydata.iterrows():
#         sql = "INSERT INTO bookcopy VALUES (%s,%s,%s,%s)"
#         cursor.execute(sql, tuple(row))
#         connection.commit()
#         print(tuple(row))

#     print("Records inserted successfully into bookcopy table")
#     cursor.close()

# except mysql.connector.Error as error:
#     print("Failed to insert record into bookcopy table {}".format(error))

# finally:
#     if connection.is_connected():
#         connection.close()
#         print("MySQL connection is closed")

