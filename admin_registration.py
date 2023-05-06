import bcrypt
import mysql.connector

host = 'localhost'
user = 'root'
db_password = 'MysqlDB1'
schema = 'library'


def hash_pw(pwd):
    bytepass = bytes(pwd, 'utf-8')
    salt = bcrypt.gensalt()
    hashedpw = bcrypt.hashpw(bytepass, salt)
    return hashedpw


def admin_id_generator(max_nbr):
    admin_nbr = max_nbr
    next_nbr = (admin_nbr + 1)
    return next_nbr


first_name = input('Enter admin first name: ')
last_name = input('Enter admin last name: ')
password = input('Enter admin password: ')


hashedpwd = hash_pw(password)

try:
    connection = mysql.connector.connect(host=host, database=schema, user=user, password=db_password)

    # pull the last card number from the members table
    max_admin_number = "select max(admin_id) from admin"
    cursor2 = connection.cursor()
    cursor2.execute(max_admin_number)
    record = cursor2.fetchall()

    # check if there are existing numbers and if so generate the next available number
    for row in record:
        nbr = row[0]
        if not nbr:
            new_nbr = 1001
        else:
            new_nbr = admin_id_generator(nbr)

    # insert statements to insert the data into the database tables
    insert_admin = """INSERT INTO admin (admin_id, first_name, last_name)
                        VALUES (%s, %s, %s)"""
    insert_pw = """INSERT INTO adminpass (admin_id, hashedpw)
                                    VALUES (%s, %s)"""

    insert_record = (new_nbr, first_name, last_name)
    insert_record2 = (new_nbr, hashedpwd)

    cursor = connection.cursor()
    # execute both insert statements
    cursor.execute(insert_admin, insert_record)
    cursor.execute(insert_pw, insert_record2)
    connection.commit()

    cursor.close()
    cursor2.close()

except mysql.connector.Error as error:
    print("Failed {}".format(error))

finally:
    if connection.is_connected():
        connection.close()
        print('Admin user added.')
