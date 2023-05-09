# Library DMS web application - CMSC 495 group 3
# a web application to manage library database, allowing members and admins to log in and search the database.

from functools import wraps
import mysql.connector
from flask import *
import bcrypt
from datetime import date
from enum import Enum

# update the below db_password with your personal MySQL password
host = 'localhost'
user = 'root'
db_password = 'MysqlDB1'
schema = 'library'

app = Flask(__name__)

app.config['SECRET_KEY'] = 'tempsecretkey'

# Book, Rented_Book, Carousel and Return_Book_Result used for display of books in home page carousel
class Book:
    def __init__(self, book_id, title, author, img_url):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.img_url = img_url
        self.genre = None

class Rented_Book:
    def __init__(self, copy_id, checkout_date, title, img_path, err_msg, can_return):
        self.copy_id = copy_id
        self.checkout_date = checkout_date
        self.title = title
        self.img_path = img_path
        self.err_msg = err_msg
        self.can_return = can_return

class Carousel:
    def __init__(self, books, category):
        self.books = books
        self.category = category
        self.page_count = None

class Return_Book_Result(Enum):
    SUCCESS = 1
    BOOK_NOT_PRESENT = 2
    ERROR = 3

#wrapper methods to restrict a user from un authorized routes
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

# check if the ID entered belongs to a registered Admin
def check_admin(employee_id):
    min_card = 0
    max_card = 0
    try:
        # connect to mysql database
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql_select_query = "select admin_id from admin"
        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()

        for row in records:
            admin_id = row[0]
            if admin_id == int(employee_id):
                return True

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()
    return False

# check if a book_id is in the book table in the database
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

# update the book table with entered title, author and genre
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

# delete the book copy of the entered copy_id
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

# update a member record in the members table with the entered arguments
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

# delet the member from the database with the entered ID
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

# update the bookcopy, checkout and members table with the entered ID. checkout_status set to 'rented', checkout_date
# set to todays date and members copy_id set to the entered Id number
def rent_bookcopy(copy_id):
    card_number, first_name, last_name, birth_date, email, status, mbr_copy_id, title = pull_records(
        session['card_number'])
    if mbr_copy_id:
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

# update the bookcopy, checkout and members table with the entered ID. checkout_status set to 'available', return_date
# set to todays date and members copy_id set to null
def return_bookcopy(copy_id):
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql = "UPDATE bookcopy SET checkout_status = %s WHERE copy_id = %s"
        val = ('available', copy_id)
        cursor = connection.cursor()
        cursor.execute(sql, val)
        connection.commit()
        sql = "UPDATE checkout SET return_date = %s WHERE copy_id = %s"
        val = (date.today(), copy_id)
        cursor.execute(sql, val)
        connection.commit()
        sql = "UPDATE members SET copy_id = %s WHERE card_number = %s"
        val = (None, session['card_number'])
        cursor.execute(sql, val)
        connection.commit()
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

# pull the hashed password for the entered member library card number
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

# pull the hashed password for the entered admin ID
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

# pull all members in the db for reporting
def pull_records(lcn):
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

# pull all book copies in the db based on entered search criteria
def book_records(**criteria):
    search_type = criteria['type']
    value = criteria['value']
    try:
        connection = mysql.connector.connect(
            host=host, database=schema, user=user, password=db_password)

        sql_select_query = "select distinct b.title, b.author, b.genre, bc.media_type, b.book_id, bc.copy_id, " \
                           "bc.checkout_status from book b inner join bookcopy bc on b.book_id = bc.book_id " \
                           "where ucase(b." + search_type + ") like '%" + str(value) + "%'"

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
            chk_status = row[6]
            books.append([title, author, genre, media_type, book_id, copy_id, chk_status])

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return books

# pull all members in the db based on entered search criteria
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

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return _members

# pull all book copies in the db for reporting
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

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()

    return books

# validate entered member information matches database records
def validate(lcn, first, last, email_entered):
    if check_member(lcn):
        card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
            lcn)
        if (first == first_name) and (last == last_name) and (email_entered == email):
            return True
    return False

# check that the password is not too short or too common
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

@app.template_filter('dateimeformat')
def dateimeformat(value, format='%a %b %d, %Y'):    
    return value.strftime(format)

# END HELPERS

# home page route
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
                        cars.append(Carousel(bList, row[3]))
                else:
                    bList = [bItem]
                    cars.append(Carousel(bList, row[3]))

        sql_query = "SELECT genre, CEILING(COUNT(genre)/4) FROM book GROUP BY genre"
        cursor.execute(sql_query)
        records = cursor.fetchall()
        for gr in records:
            car = find(cars, gr[0])
            if car:
                car.page_count = gr[1]
            
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

#checkout page route
@app.route('/checkout/<book_id>')
@authorized
def checkout(book_id):
    book_to_rent = None
    rented_book = None
    
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

        card_number = session['card_number']
        sql_rented_book = "SELECT CK.copy_id, CK.checkout_date, BK.title"\
            " FROM library.checkout CK " \
            " JOIN library.bookcopy BC " \
            " ON CK.copy_id = BC.book_id " \
            " JOIN library.book BK " \
            " ON CK.copy_id = BK.book_id " \
            " JOIN library.members MB " \
            " ON CK.copy_id = MB.copy_id " \
            " WHERE MB.card_number = " + str(card_number)

        cursor.execute(sql_rented_book)
        result = cursor.fetchall()
        if len(result):
            res = result[0]
            img_path = url_for('static', filename=f'images/{res[0]}.png')
            err_msg = None
            can_return = False
            if book_to_rent:
                if str(book_to_rent.book_id) == str(res[0]):
                    err_msg = 'You are already in possession of a copy of this book.'
                else:
                    err_msg = 'you have not returned the book in your possession.'
                    can_return = True

                print(f'msg: {err_msg}')
            rented_book = Rented_Book(res[0], res[1], res[2], img_path, err_msg, can_return)

    except mysql.connector.Error as error:
        print("Failed {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()
    
    return render_template('checkout.html', book_to_rent = book_to_rent, rented_book = rented_book)

# confirm checkout, make sure the book is available and that the user does not have a current rental
@app.route('/confirm_checkout', methods=['POST'])
@authorized
def confirm_checkout():
    book_id = request.form['book_id']
    book_list = book_records(type='book_id', value=book_id)
    card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(session['card_number'])
    if copy_id:
        message = 'You have not returned the book in your possession.'
        return redirect(url_for('checkout', book_id=book_id, message=message))
    if book_list[0][6] == 'rented':
        # redirect to the check out with a meaningful error message for the user
        message = 'This book is not available.'
        return redirect(url_for('checkout', book_id = book_id, message=message))

    title = book_list[0][0]
    rent_bookcopy(book_id)
    return render_template('welcome.html', title=title)
    # if the checkout succeeds, redirect to 'members' page with a success message

@app.route('/return-current-book', methods=['POST'])
def return_current_book():
    status_code = None

    card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
                session['card_number'])
    if copy_id:
        return_bookcopy(copy_id)
        card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
                session['card_number'])
        if not copy_id:
            status_code = 200
        else:
            status_code = 400          
    else:
        status_code = 404

    new_resp = { 
        'result': status_code
    }
    return new_resp, status_code

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

# route to regiter member
@app.route('/registerMbr', methods=['GET', 'POST'])
def registerMbr():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        dob = request.form['DOB']
        password1 = request.form['password1']
        password2 = request.form['password2']

        # check that the passwords entered are the same
        if password1 == password2:
            if not authenticate_PW(password1):
                # if the password fails authentication send a message
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

                # pull member records with card number and return them with the welcome template
                card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
                    new_card)
                return render_template("welcome.html", card_number=card_number, first_name=first_name,
                                       last_name=last_name,
                                       email=email, dob=dob)
        message = 'Passwords do not match!'
        return render_template('register.html', message=message)
    return redirect('/register')

# member login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # check for an entered card number
        if request.form['cardnumber']:
            # check if the entered number is a member
            if check_member(request.form['cardnumber']):
                lcn = request.form['cardnumber']
                password = request.form['password']
                byte_pass = bytes(password, 'UTF-8')
                # make sure entered password matches saved hashed password
                if bcrypt.checkpw(byte_pass, bytes(pull_password(lcn), 'UTF-8')):
                    session['card_number'] = lcn
                    return redirect('/members')
            # return template with appropriate message if filed login
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

# route for updating account info
@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        if request.form['cardnumber']:
            # pull entered info from the form for updating the database
            lcn = request.form['cardnumber']
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            email = request.form['email']
            dob = request.form['dob']

            try:
                connection = mysql.connector.connect(host=host, database=schema, user=user,
                                                     password=db_password)

                sql = "UPDATE members SET first_name = %s, last_name = %s, birth_date = %s, email_address = %s " \
                      "WHERE card_number = %s"
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

# route for member who forgot password
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

            # make sure the entered info matches the database info
            if validate(lcn, first_name, last_name, email):
                # Make sure passwords match
                if password1 == password2:
                    # hash password
                    hashedpwd = hash_pw(password1)
                    string = hashedpwd.decode('utf-8')
                    try:
                        connection = mysql.connector.connect(host=host, database=schema, user=user,
                                                             password=db_password)

                        # update the database with the new password
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

                    # send the appropriate message back
                    message = 'Password updated successfully!'
                    return render_template('forgotPW.html', message=message)
                message = 'Passwords did not match!'
                return render_template('forgotPW.html', message=message)
            message = 'Invalid information entered!'
            return render_template('forgotPW.html', message=message)
        message = 'Make sure all fields are filled!'
        return render_template('forgotPW.html', message=message)
    return render_template('forgotPW.html')

# administrator login route
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        if request.form['employe_id']:
            # check that the employee Id exists in the database
            if check_admin(request.form['employe_id']):
                admin_id = request.form['employe_id']
                password = request.form['password1']
                byte_pass = bytes(password, 'UTF-8')
                # check that the entered password matches the saved hashed password
                if bcrypt.checkpw(byte_pass, bytes(pull_password_admin(admin_id), 'UTF-8')):
                    session['admin'] = admin_id
                    return redirect('/admin')
    return render_template('adminLogin.html')

# admin portal route
@app.route('/admin', methods=['GET', 'POST'])
@authorized_admin
def admin():
    if request.method == 'POST':
        # depending on which action is taken on the admin page perform the appropriate action
        if request.form['value'] and request.form['criteria']:
            search_value = request.form['value']
            drop_down = request.form['criteria']
            book_list = book_records(type=drop_down, value=search_value)
            # return book list by search
            return render_template('admin.html', book_list=book_list)
        elif request.form['value2'] and request.form['criteria2']:
            search_value = request.form['value2']
            drop_down = request.form['criteria2']
            member_list = member_records(type=drop_down, value=search_value)
            # return member list by search
            return render_template('admin.html', member_list=member_list)
        if 'update' in request.form:
            book_id = request.form['update']
            # send to book edit page with select book ID
            return render_template('bookedit.html', book_id=book_id)
        elif 'delete' in request.form:
            copy_id = request.form['delete']
            # delete selected book and return message
            delete_bookcopy(copy_id)
            message = 'Copy Successfully Deleted'
            return render_template('admin.html', message=message)
        if 'update2' in request.form:
            card_number = request.form['update2']
            # send to member edit page with selected card number
            return render_template('memberedit.html', card_number=card_number)
        elif 'delete2' in request.form:
            card_number = request.form['delete2']
            # delete selected member and return message
            delete_member(card_number)
            message = 'Member Successfully Deleted'
            return render_template('admin.html', message=message)
        elif 'mbr_report' in request.form:
            member_list = member_records(type='first_name', value='')
            # return an all member report list
            return render_template('admin.html', member_list=member_list)
        elif 'copy_report' in request.form:
            book_list = book_records(type='title', value='')
            # return an all copy report list
            return render_template('admin.html', book_list=book_list)
        else:
            return render_template('admin.html')

    return render_template('admin.html')

# route to get info from book edit page and update the database
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

# rout to get member info from member edit page and update the databse
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

# route for members page
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
            # return list of books searched by entered criteria
            return render_template("welcome.html", card_number=card_number, first_name=first_name, last_name=last_name,
                                   email=email, dob=dob, status=status, book_list=book_list, title=title)
        # if rental button is selected
        if 'rent' in request.form:
            copy_id = request.form['rent']
            # update the database with the rented book
            rent_bookcopy(copy_id)
            card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
                session['card_number'])
            return render_template("welcome.html", card_number=card_number, first_name=first_name, last_name=last_name,
                                   email=email, status=status, dob=dob, title=title)
        # if return button is selected
        if 'return' in request.form:
            card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
                session['card_number'])
            # check if the member has a book rented
            if copy_id:
                # update the database with that return
                return_bookcopy(copy_id)
                card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
                    session['card_number'])
                return render_template("welcome.html", card_number=card_number, first_name=first_name,
                                       last_name=last_name,
                                       email=email, status=status, dob=dob, title=title)
    card_number, first_name, last_name, dob, email, status, copy_id, title = pull_records(
        session['card_number'])
    return render_template("welcome.html", card_number=card_number, first_name=first_name, last_name=last_name,
                           email=email, dob=dob, status=status, title=title)

# route to delete member profile
@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    card_number = session['card_number']
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

