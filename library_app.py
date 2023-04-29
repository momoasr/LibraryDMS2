# Library DMS web application - CMSC 495 group 3
# a web application to manage library database, allowing members and admins to log in and search the database.

from functools import wraps
import mysql.connector
from flask import *
import bcrypt

host = 'localhost'
user = 'root'
db_password = 'MysqlDB1'
schema = 'library'

app = Flask(__name__)

app.config['SECRET_KEY'] = 'tempsecretkey'


class Book:
    def __init__(self, book_id, title, author, img_url):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.img_url = img_url


class Carousel:
    def __init__(self, books, category):
        self.books = books
        self.category = category


def authorized(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not session.get('email'):
            return render_template('login.html')
        return f(*args, **kwargs)

    return decorator


# generate the next unused library card number
def card_number_generator(max_card):
    card_number = max_card
    next_card = (card_number + 1)
    return next_card


# hash the password entered by the user
def hash_pw(pwd):
    bytepass = bytes(pwd, 'utf-8')
    salt = bcrypt.gensalt()
    hashedpw = bcrypt.hashpw(bytepass, salt)
    return hashedpw


# check if the number entered is in the database
def check_member(lcn):
    min_card = 0
    max_card = 0
    try:
        # connect to mysql database
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql_select_query = "select min(card_number), max(card_number) from members"
        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        for row in records:
            min_card = row[0]
            max_card = row[1]

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    if min_card <= int(lcn) <= max_card:
        return True
    return False


def pull_password(lcn):
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        # the below line is the select statement to pull the members records based on the LCN
        sql_select_query = "select hashedpw from memberpass where card_number = " + \
            str(lcn)
        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        for row in records:
            member_password = row[0]

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()
    return member_password


def pull_records(lcn):
    try:
        # connect to mysql database
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        # the below line is the select statement to pull the members records based on the LCN
        sql_select_query = "select * from members where card_number = " + \
            str(lcn)
        cursor = connection.cursor()
        # execute the select statement and fetch the results
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        # records are in a list of tuples so we can loop through the single returned row to pull fields
        for row in records:
            card_number = row[0]
            first_name = row[1]
            last_name = row[2]
            birth_date = row[3]
            email = row[4]
            status = row[5]
            copy_id = row[6]

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return card_number, first_name, last_name, birth_date, email


def book_records(**criteria):
    search_type = criteria['type']
    value = criteria['value']
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql_select_query = "select distinct b.title, b.author, b.genre, bc.media_type from book b " \
                           "inner join bookcopy bc on b.book_id = bc.book_id " \
                           "where ucase(b." + search_type + \
            ") like '%" + value + "%'"

        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        books = []
        for row in records:
            title = row[0]
            author = row[1]
            genre = row[2]
            media_type = row[3]
            books.append([title, author, genre, media_type])
            # print('title: ' + title + ' author: ' + author + ' genre: ' + genre + ' type: ' + media_type)

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return books


def report_allcopies():
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql_select_query = "select distinct bc.copy_id, b.title, b.author, b.genre, bc.media_type from book b " \
                           "inner join bookcopy bc on b.book_id = bc.book_id"

        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        books = []
        for row in records:
            copy_id = row[0]
            title = row[1]
            author = row[2]
            genre = row[3]
            media_type = row[4]
            books.append([copy_id, title, author, genre, media_type])
            # print('title: ' + title + ' author: ' + author + ' genre: ' + genre + ' type: ' + media_type)

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return books


def validate(lcn, first, last, email_entered):
    if check_member(lcn):
        card_number, first_name, last_name, dob, email = pull_records(lcn)
        print(card_number, first_name, last_name, email)
        print(first, last, email_entered)
        # and dob_entered == dob:
        if (first == first_name) and (last == last_name) and (email_entered == email):
            return True
    return False


@app.route('/', methods=['GET'])
def home():
    search_value = request.args.get('search')
    print(f'search: {search_value}')
    books = [
        Book(1001, 'Da Vinci Code,The', 'Brown, Dan', ''),
        Book(1002, 'Harry Potter and the Deathly Hallows', 'Rowling, J.K.', ''),
        Book(1003, 'Fifty Shades of Grey', 'Larsson, Stieg', ''),
        Book(1004, 'Time Traveler''s Wife,The', 'Niffenegger, Audrey', '')
    ]

    for b in books:
        img_path = url_for('static', filename='images/')
        b.img_url = f'{img_path}{b.book_id}.png'

    cars = [
        Carousel(books, 'Romance & Sagas'),
        Carousel(books, 'Young Adult Fiction')]

    return render_template('home.html', carousels=cars)


@app.route('/fetch-next-set', methods=['GET'])
def fetch_next_set():
    category = request.args.get('category')
    print(f'category: {category}')
    page = request.args.get('page')
    print(f'search: {page}')

    books = [
        Book(1049, 'Memoirs of a Geisha', 'Golden, Arthur', ''),
        Book(1056, 'Broker,The', 'Grisham, John', ''),
    ]
    for b in books:
        img_path = url_for('static', filename='images/')
        b.img_url = f'{img_path}{b.book_id}.png'
        
    return render_template('book_by_category.html', books=books)


@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


@app.route('/registerMbr', methods=['GET', 'POST'])
def registerMbr():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        dob = request.form['DOB']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 == password2:
            hashedpwd = hash_pw(password1)

            try:
                connection = mysql.connector.connect(
                    host=host, database=schema, user=user, password=db_password)

                # pull the last card number from the members table
                max_card_number = "select max(card_number) from members"
                cursor2 = connection.cursor()
                cursor2.execute(max_card_number)
                record = cursor2.fetchall()

                # check if there are existing card numbers and if so generate the next available number
                for row in record:
                    card = row[0]
                    if not card:
                        new_card = 1001
                    else:
                        new_card = card_number_generator(card)

                # insert statements to insert the data into the database tables
                insert_member = """INSERT INTO members (card_number, first_name, last_name, birth_date, email_address)
                                    VALUES (%s, %s, %s, %s, %s)"""
                insert_pw = """INSERT INTO memberpass (card_number, hashedpw)
                                                VALUES (%s, %s)"""

                insert_record = (new_card, first_name, last_name, dob, email)
                insert_record2 = (new_card, hashedpwd)

                cursor = connection.cursor()
                # execute both insert statements
                cursor.execute(insert_member, insert_record)
                cursor.execute(insert_pw, insert_record2)
                connection.commit()

                cursor.close()
                cursor2.close()

            except mysql.connector.Error as error:
                print("Failed {}".format(error))

            finally:
                if connection.is_connected():
                    connection.close()

            card_number, first_name, last_name, dob, email = pull_records(
                new_card)
            return render_template("welcome.html", card_number=card_number, first_name=first_name, last_name=last_name,
                                   email=email, dob=dob)
    return redirect('/register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route('/loginMbr', methods=['GET', 'POST'])
def loginMbr():
    if request.method == 'POST':
        if request.form['cardnumber']:
            if check_member(request.form['cardnumber']):
                lcn = request.form['cardnumber']
                password = request.form['password']
                byte_pass = bytes(password, 'UTF-8')
                if bcrypt.checkpw(byte_pass, bytes(pull_password(lcn), 'UTF-8')):
                    session['email'] = lcn
                    return redirect('/members')
            message = 'Incorrect Card Number or Password!'
            return render_template('login.html', message=message)
        message = 'Enter Card Number and Password!'
        return render_template('login.html', message=message)
    return render_template('Login.html')


@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        if request.form['cardnumber']:
            lcn = request.form['cardnumber']
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            email = request.form['email']
            password1 = request.form['password1']
            password2 = request.form['password2']

            if validate(lcn, first_name, last_name, email):
                if password1 == password2:
                    hashedpwd = hash_pw(password1)
                    string = hashedpwd.decode('utf-8')
                    try:
                        connection = mysql.connector.connect(
                            host=host, database=schema, user=user, password=db_password)

                        sql = "UPDATE memberpass SET hashedpw = %s WHERE card_number = %s"
                        val = (string, lcn)

                        cursor = connection.cursor()
                        cursor.execute(sql, val)
                        connection.commit()
                        cursor.close()

                    except mysql.connector.Error as error:
                        print("Failed {}".format(error))

                    finally:
                        if connection.is_connected():
                            connection.close()

                    message = 'Password updated successfully!'
                    return render_template('forgotPW.html', message=message)

                message = 'Passwords did not match!'
                return render_template('forgotPW.html', message=message)

            message = 'Invalid information entered!'
            return render_template('forgotPW.html', message=message)
        message = 'Make sure all fields are filled!'
        return render_template('forgotPW.html', message=message)
    return render_template('forgotPW.html')


@app.route('/adminlogin')
def adminlogin():
    return render_template('adminlogin.html')


@app.route('/loginAdm', methods=['GET', 'POST'])
def loginAdm():
    if request.method == 'POST':
        admin_id = request.form['employe_id']
        password = request.form['password1']
    byte_pass = bytes(password, 'UTF-8')
    if bcrypt.checkpw(byte_pass, bytes(pull_password(admin_id), 'UTF-8')):
        session['email'] = admin_id
        return redirect('/admin')
    return render_template('Login.html')


@app.route('/admin', methods=['GET', 'POST'])
@authorized
def admin():
    if request.method == 'POST':
        if request.form['value'] and request.form['criteria']:
            title_input = request.form['value']
            criteria_type = request.form['criteria']
            book_list = book_records(type=criteria_type, value=title_input)
            return render_template('admin.html', book_list=book_list)
    return render_template('admin.html')


@app.route('/members', methods=['GET', 'POST'])
@authorized
def members():
    if request.method == 'POST':
        if request.form['search'] and request.form['criteria']:
            title_input = request.form['search']
            criteria_type = request.form['criteria']
            print(criteria_type)
            book_list = book_records(type=criteria_type, value=title_input)
            card_number, first_name, last_name, dob, email = pull_records(
                session['email'])
            return render_template("welcome.html", card_number=card_number, first_name=first_name, last_name=last_name,
                                   email=email, dob=dob, book_list=book_list)
    card_number, first_name, last_name, dob, email = pull_records(
        session['email'])
    return render_template("welcome.html", card_number=card_number, first_name=first_name, last_name=last_name,
                           email=email, dob=dob)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
