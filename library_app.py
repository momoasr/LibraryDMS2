# Library DMS web application - CMSC 495 group 3
# a web application to manage library database, allowing members and admins to log in and search the database.

from functools import wraps
import mysql.connector
from flask import *
import bcrypt
from datetime import date

host = 'localhost'
user = 'root'
db_password = 'db_password'
schema = 'library'

app = Flask(__name__)

app.config['SECRET_KEY'] = 'tempsecretkey'


class Book:
    def __init__(self, book_id, title, author, img_url):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.img_url = img_url
        self.genre = None


class Carousel:
    def __init__(self, books, category, next_set):
        self.books = books
        self.category = category


def authorized(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not session.get('card_number'):
            return render_template('login.html')
        return f(*args, **kwargs)

    return decorator


def authorized_admin(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not session.get('admin'):
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
        # min(card_number), max(card_number)
        sql_select_query = "select card_number from members"
        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        for row in records:
            card_number = row[0]
            if card_number == int(lcn):
                return True

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return False


def check_admin(employee_id):
    min_card = 0
    max_card = 0
    try:
        # connect to mysql database
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)
        # min(card_number), max(card_number)
        sql_select_query = "select admin_id from admin"
        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        for row in records:
            admin_id = row[0]
            if admin_id == int(employee_id):
                return True
            # min_card = row[0]
            # max_card = row[1]

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    # if min_card <= int(lcn) <= max_card:
    #     return True
    return False


def check_book(book_id):
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql_select_query = "select book_id from book"
        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        for row in records:
            book = row[0]
            if int(book) == int(book_id):
                return True

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return False


def update_book(book_id, title, author, genre):
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql = "UPDATE book SET title = %s, author = %s, genre = %s WHERE book_id = %s"
        val = (title, author, genre, book_id)

        cursor = connection.cursor()
        cursor.execute(sql, val)
        connection.commit()
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()


def delete_bookcopy(copy_id):
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        cursor = connection.cursor()
        cursor.execute("DELETE FROM bookcopy WHERE copy_id = %s", (copy_id,))
        connection.commit()

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()


def update_member(card_number, first_name, last_name, email_address, status):
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql = "UPDATE members SET first_name = %s, last_name = %s, email_address = %s, " \
              "status = %s WHERE card_number = %s"
        val = (first_name, last_name, email_address, status, card_number)

        cursor = connection.cursor()
        cursor.execute(sql, val)
        connection.commit()
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()


def delete_member(copy_id):
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)
        # delete the user's account from the database
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM members WHERE card_number = %s", (copy_id,))
        cursor.execute(
            "DELETE FROM memberpass WHERE card_number = %s", (copy_id,))
        connection.commit()

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()


def rent_bookcopy(copy_id):
    card_number, first_name, last_name, birth_date, email, status, copy_id, title = pull_records(
        session['card_number'])
    if not copy_id:
        return False
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql = "UPDATE bookcopy SET checkout_status = %s WHERE copy_id = %s"
        val = ('rented', copy_id)
        cursor = connection.cursor()
        cursor.execute(sql, val)
        connection.commit()
        sql = "UPDATE checkout SET checkout_date = %s WHERE copy_id = %s"
        val = (date.today(), copy_id)
        cursor.execute(sql, val)
        connection.commit()
        sql = "UPDATE members SET copy_id = %s WHERE card_number = %s"
        val = (copy_id, session['card_number'])
        cursor.execute(sql, val)
        connection.commit()
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()
    return True


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


def pull_password_admin(employee_id):
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        # the below line is the select statement to pull the members records based on the LCN
        sql_select_query = "select hashedpw from adminpass where admin_id = " + \
            str(employee_id)
        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        for row in records:
            admin_password = row[0]

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()
    return admin_password


def pull_records(lcn):
    print(lcn)
    try:
        # connect to mysql database
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        # the below line is the select statement to pull the members records based on the LCN
        sql_select_query = "select m.card_number, m.first_name, m.last_name, m.birth_date, m.email_address, m.status, " \
                           "m.copy_id, bk.title" \
                           " from members m " \
                           "left outer join bookcopy b " \
                           "on m.copy_id = b.copy_id " \
                           "left outer join book bk " \
                           "on b.book_id = bk.book_id " \
                           "where m.card_number = " + str(lcn)
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
            title = row[7]

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return card_number, first_name, last_name, birth_date, email, status, copy_id, title


# def book_search(**criteria):
#     search_type = criteria['type']
#     value = criteria['value']
#     try:
#         connection = mysql.connector.connect(host=host, database=schema, user=user, password=db_password)
#
#         sql_select_query = "select distinct b.title, b.author, b.genre, bc.media_type, b.book_id, bc.copy_id " \
#                            "from book b inner join bookcopy bc on b.book_id = bc.book_id " \
#                            "where ucase(b." + search_type + ") like '%" + value + "%'"
#
#         cursor = connection.cursor()
#         cursor.execute(sql_select_query)
#         records = cursor.fetchall()
#
#         books = []
#         for row in records:
#             title = row[0]
#             author = row[1]
#             genre = row[2]
#             media_type = row[3]
#             book_id = row[4]
#             copy_id = row[5]
#             books.append(Book(int(book_id), title, author, genre, ''))
#             # books.append([title, author, genre, media_type, book_id, copy_id])
#             # print('title: ' + title + ' author: ' + author + ' genre: ' + genre + ' type: ' + media_type)
#
#     except mysql.connector.Error as error:
#         print("Failed {}".format(error))
#
#     finally:
#         if connection.is_connected():
#             connection.close()
#
#     return books


def book_records(**criteria):
    search_type = criteria['type']
    value = criteria['value']
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql_select_query = "select distinct b.title, b.author, b.genre, bc.media_type, b.book_id, bc.copy_id " \
                           "from book b inner join bookcopy bc on b.book_id = bc.book_id " \
                           "where ucase(b." + search_type + ") like '%" + \
            value + "%' and bc.checkout_status = 'available'"

        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        books = []
        for row in records:
            title = row[0]
            author = row[1]
            genre = row[2]
            media_type = row[3]
            book_id = row[4]
            copy_id = row[5]
            books.append([title, author, genre, media_type, book_id, copy_id])
            # print('title: ' + title + ' author: ' + author + ' genre: ' + genre + ' type: ' + media_type)

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return books


def member_records(**criteria):
    search_type = criteria['type']
    value = criteria['value']
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql_select_query = "select * from members " \
                           "where ucase(" + search_type + \
            ") like '%" + value + "%'"

        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        _members = []
        for row in records:
            card_number = row[0]
            first_name = row[1]
            last_name = row[2]
            birth_date = row[3]
            email = row[4]
            status = row[5]
            copy_id = row[6]
            _members.append([card_number, first_name, last_name,
                            birth_date, email, status, copy_id])
            # print('title: ' + title + ' author: ' + author + ' genre: ' + genre + ' type: ' + media_type)

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return _members


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
        card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
            lcn)
        # print(card_number, first_name, last_name, email)
        # print(first, last, email_entered)
        # and dob_entered == dob:
        if (first == first_name) and (last == last_name) and (email_entered == email):
            return True
    return False


def authenticate_PW(password):
    common_pws = ('password', 'password123', 'password1',
                  '12345', '12345678', '111111')
    for pw in common_pws:
        if password == pw:
            return False
    if len(password) < 7:
        return False
    return True

# HELPERS
def find(arr, cat):
    for x in arr:
        if x.category == cat:
            return x

# END HELPERS


@app.route('/', methods=['GET'])
def home():
    search_value = request.args.get('search')
    search_value = '' if search_value is None else search_value
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        cars = []

        cursor = connection.cursor()
        cursor.callproc('getBooksByAllGenres', [search_value])

        for result in cursor.stored_results():
            allResults = result.fetchall()
            for i, row in enumerate(allResults):
                img_path = url_for('static', filename='images/')
                img_url = f'{img_path}{row[0]}.png'
                bItem = Book(row[0], row[1], row[2], img_url)

                if len(cars):
                    local_cat = find(cars, row[3])
                    if local_cat:
                        local_cat.books.append(bItem)
                    else:
                        bList = [bItem]
                        cars.append(Carousel(bList, row[3], False))
                else:
                    bList = [bItem]
                    cars.append(Carousel(bList, row[3], False))

        for car in cars:
            if len(car.books) < 4:
                car.next_set = True
    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return render_template('home.html', carousels=cars, search_value=search_value)


@app.route('/fetch-next-set', methods=['GET'])
def fetch_next_set():
    category = request.args.get('category')
    page = request.args.get('page')
    searchBox = request.args.get("searchBox")
    print(f'category: {category}, searchBox: {searchBox}, page: {page}')

    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        books = []

        cursor = connection.cursor()
        cursor.callproc('getBookByGenre', [category, page, searchBox])

        for result in cursor.stored_results():
            allResults = result.fetchall()
            for i, row in enumerate(allResults):
                img_path = url_for('static', filename='images/')
                img_url = f'{img_path}{row[0]}.png'
                bItem = Book(row[0], row[1], row[2], img_url)
                books.append(bItem)

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return render_template('book_by_category.html', books=books)

@app.route('/checkout/<book_id>')
def checkout(book_id):
    book_to_rent = None
    
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)
        
        sql_select_query = 'SELECT * FROM library.book WHERE book_id = ' + book_id
        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()
        if len(records) > 0:
            row = records[0]
            img_path = url_for('static', filename=f'images/{book_id}.png')
            book_to_rent = Book(row[0], row[1], row[2], img_path)
            book_to_rent.genre = row[3]

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()
    
    return render_template('checkout.html', book_to_rent = book_to_rent, img_path = img_path)

@app.route('/confirm_checkout', methods=['POST'])
def confirm_checkout():
    book_id = request.form['book_id']
    print(f'book_id: {book_id}')

    # TO DO: do the checkout here...
    # if the checkout fails, 
    # redirect to the check out with a meaningful error message for the user
    return redirect(url_for('checkout', book_id = book_id))
    # if the checkout succeeds, redirect to 'members' page with a success message

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
            if not authenticate_PW(password1):
                message = 'Your password is too common or too short, please enter another'
                return render_template('register.html', message=message)
            else:
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

                    insert_record = (new_card, first_name,
                                     last_name, dob, email)
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

                card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
                    new_card)
                return render_template("welcome.html", card_number=card_number, first_name=first_name,
                                       last_name=last_name,
                                       email=email, dob=dob)
        message = 'Passwords do not match!'
        return render_template('register.html', message=message)
    return redirect('/register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['cardnumber']:
            if check_member(request.form['cardnumber']):
                lcn = request.form['cardnumber']
                password = request.form['password']
                byte_pass = bytes(password, 'UTF-8')
                if bcrypt.checkpw(byte_pass, bytes(pull_password(lcn), 'UTF-8')):
                    session['card_number'] = lcn
                    return redirect('/members')
            message = 'Incorrect Card Number or Password!'
            return render_template('login.html', message=message)
        message = 'Enter Card Number and Password!'
        return render_template('login.html', message=message)
    return render_template('Login.html')


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')


@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        if request.form['cardnumber']:
            lcn = request.form['cardnumber']
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            email = request.form['email']
            dob = request.form['dob']

            try:
                connection = mysql.connector.connect(host=host, database=schema, user=user,
                                                     password=db_password)

                sql = "UPDATE members SET first_name = %s, last_name = %s, birth_date = %s, email_address = %s WHERE card_number = %s"
                val = (first_name, last_name, dob, email, lcn)

                cursor = connection.cursor()
                cursor.execute(sql, val)
                connection.commit()
                cursor.close()

            except mysql.connector.Error as error:
                print("Failed {}".format(error))

            finally:
                if connection.is_connected():
                    connection.close()

    return render_template('account.html')


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
                        connection = mysql.connector.connect(host=host, database=schema, user=user,
                                                             password=db_password)

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


@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        if request.form['employe_id']:
            if check_admin(request.form['employe_id']):
                admin_id = request.form['employe_id']
                password = request.form['password1']
                byte_pass = bytes(password, 'UTF-8')
                if bcrypt.checkpw(byte_pass, bytes(pull_password_admin(admin_id), 'UTF-8')):
                    session['admin'] = admin_id
                    return redirect('/admin')
    return render_template('adminLogin.html')


@app.route('/admin', methods=['GET', 'POST'])
@authorized_admin
def admin():
    if request.method == 'POST':
        if request.form['value'] and request.form['criteria']:
            search_value = request.form['value']
            drop_down = request.form['criteria']
            book_list = book_records(type=drop_down, value=search_value)
            return render_template('admin.html', book_list=book_list)
        elif request.form['value2'] and request.form['criteria2']:
            search_value = request.form['value2']
            drop_down = request.form['criteria2']
            member_list = member_records(type=drop_down, value=search_value)
            return render_template('admin.html', member_list=member_list)
        if 'update' in request.form:
            book_id = request.form['update']
            return render_template('bookedit.html', book_id=book_id)
        elif 'delete' in request.form:
            copy_id = request.form['delete']
            delete_bookcopy(copy_id)
            message = 'Copy Successfully Deleted'
            return render_template('admin.html', message=message)
        if 'update2' in request.form:
            card_number = request.form['update2']
            return render_template('memberedit.html', card_number=card_number)
        elif 'delete2' in request.form:
            card_number = request.form['delete2']
            delete_member(card_number)
            message = 'Member Successfully Deleted'
            return render_template('admin.html', message=message)
        elif 'mbr_report' in request.form:
            member_list = member_records(type='first_name', value='')
            return render_template('admin.html', member_list=member_list)
        elif 'copy_report' in request.form:
            book_list = book_records(type='title', value='')
            return render_template('admin.html', book_list=book_list)
        else:
            return render_template('admin.html')

    return render_template('admin.html')


@app.route('/book_edit', methods=['GET', 'POST'])
@authorized_admin
def book_edit():
    if request.method == 'POST':
        if request.form['book_id']:
            if check_book(request.form['book_id']):
                book_id = request.form['book_id']
                title = request.form['title']
                author = request.form['author']
                genre = request.form['genre']
                update_book(book_id, title, author, genre)
                message = 'book updated successfully!'
                return render_template('bookedit.html', message=message)
            message = 'Book ID entered does not exist!'
            return render_template('bookedit.html', message=message)
        message = 'Please enter book ID!'
        return render_template('bookedit.html', message=message)
    return render_template('bookedit.html')


@app.route('/member_edit', methods=['GET', 'POST'])
@authorized_admin
def member_edit():
    if request.method == 'POST':
        if request.form['card_number']:
            if check_member(request.form['card_number']):
                card_number = request.form['card_number']
                first_name = request.form['first_name']
                last_name = request.form['last_name']
                email_address = request.form['email_address']
                status = request.form['status']
                update_member(card_number, first_name,
                              last_name, email_address, status)
                message = 'Member has been updated successfully!'
                return render_template('memberedit.html', message=message)
            message = 'The Member ID entered does not exist!'
            return render_template('memberedit.html', message=message)
        message = 'Please enter member ID!'
        return render_template('memberedit.html', message=message)
    return render_template('memberedit.html')


@app.route('/members', methods=['GET', 'POST'])
@authorized
def members():
    if request.method == 'POST':
        if request.form['value'] and request.form['criteria']:
            search_value = request.form['value']
            drop_down = request.form['criteria']
            book_list = book_records(type=drop_down, value=search_value)
            card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
                session['card_number'])
            return render_template("welcome.html", card_number=card_number, first_name=first_name, last_name=last_name,
                                   email=email, dob=dob, status=status, book_list=book_list, title=title)
        if 'rent' in request.form:
            copy_id = request.form['rent']
            rent_bookcopy(copy_id)
            card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
                session['card_number'])
            return render_template("welcome.html", card_number=card_number, first_name=first_name, last_name=last_name,
                                   email=email, status=status, dob=dob, title=title)
    card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
        session['card_number'])
    return render_template("welcome.html", card_number=card_number, first_name=first_name, last_name=last_name,
                           email=email, dob=dob, status=status, title=title)


@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    card_number = session['card_number']
    # card_number = request.args.get('card_num', None)
    # print(card_number)
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        # delete the user's account from the database
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM members WHERE card_number = %s", (card_number,))
        cursor.execute(
            "DELETE FROM memberpass WHERE card_number = %s", (card_number,))
        connection.commit()

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    # redirect the user to the register page after their account has been deleted
    session.clear()
    return redirect(url_for('account_deleted'))


@app.route('/account_deleted', methods=['GET', 'POST'])
def account_deleted():
    return render_template('account_deleted.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)

