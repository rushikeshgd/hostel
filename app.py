from flask import Flask, render_template, request, redirect, flash, session
import sqlite3
from datetime import datetime

app = Flask(__name__)

app.secret_key = "hostel_secret_key"


# =========================
# DATABASE CREATE
# =========================

def init_db():

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    # STUDENT TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # ADMIN TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # COMPLAINT TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        category TEXT,
        complaint TEXT,
        status TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():
    return render_template("home.html")


# =========================
# STUDENT REGISTER PAGE
# =========================

@app.route('/student_register')
def student_register_page():
    return render_template("student_register.html")


# =========================
# STUDENT REGISTER
# =========================

@app.route('/register', methods=['POST'])
def register():

    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO students(username, password)
    VALUES(?, ?)
    """, (username, password))

    conn.commit()
    conn.close()

    flash("Registration Successful")

    return redirect('/student_login')


# =========================
# STUDENT LOGIN PAGE
# =========================

@app.route('/student_login')
def student_login_page():
    return render_template("student_login.html")


# =========================
# STUDENT LOGIN
# =========================

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM students
    WHERE username=? AND password=?
    """, (username, password))

    user = cursor.fetchone()

    if user:

        session['student'] = username

        cursor.execute("""
        SELECT * FROM complaints
        WHERE username=?
        """, (username,))

        complaints = cursor.fetchall()

        conn.close()

        flash("Login Successful")

        return render_template(
            "student_dashboard.html",
            username=username,
            complaints=complaints
        )

    else:

        conn.close()

        flash("Invalid Username or Password")

        return redirect('/student_login')


# =========================
# STUDENT DASHBOARD
# =========================

@app.route('/student_dashboard')
def student_dashboard():

    if 'student' not in session:
        return redirect('/student_login')

    username = session['student']

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM complaints
    WHERE username=?
    """, (username,))

    complaints = cursor.fetchall()

    conn.close()

    return render_template(
        "student_dashboard.html",
        username=username,
        complaints=complaints
    )


# =========================
# SUBMIT COMPLAINT
# =========================

@app.route('/complaint', methods=['POST'])
def complaint():

    if 'student' not in session:
        return redirect('/student_login')

    username = session['student']

    category = request.form['category']

    # IF OTHER CATEGORY
    if category == "Other":
        category = request.form['other_category']

    complaint_text = request.form['complaint']

    status = "Pending"

    date = datetime.now().strftime("%d-%m-%Y %H:%M")

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO complaints(username, category, complaint, status, date)
    VALUES(?, ?, ?, ?, ?)
    """, (username, category, complaint_text, status, date))

    conn.commit()
    conn.close()

    flash("Complaint Submitted Successfully")

    return redirect('/student_dashboard')


# =========================
# ADMIN LOGIN PAGE
# =========================

@app.route('/admin_login')
def admin_login_page():
    return render_template("admin_login.html")


# =========================
# ADMIN LOGIN
# =========================

@app.route('/admin_login_form', methods=['POST'])
def admin_login():

    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM admins
    WHERE username=? AND password=?
    """, (username, password))

    admin = cursor.fetchone()

    if admin:

        session['admin'] = username

        cursor.execute("""
        SELECT * FROM complaints
        """)

        complaints = cursor.fetchall()

        conn.close()

        flash("Admin Login Successful")

        return render_template(
            "admin_dashboard.html",
            complaints=complaints
        )

    else:

        conn.close()

        flash("Invalid Admin Username or Password")

        return redirect('/admin_login')


# =========================
# ADMIN DASHBOARD
# =========================

@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect('/admin_login')

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    search = request.args.get('search')

    if search:

        cursor.execute("""
        SELECT * FROM complaints
        WHERE username LIKE ?
        """, ('%' + search + '%',))

    else:

        cursor.execute("""
        SELECT * FROM complaints
        """)

    complaints = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        complaints=complaints
    )


# =========================
# RESOLVE COMPLAINT
# =========================

@app.route('/resolve/<int:id>', methods=['POST'])
def resolve(id):

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE complaints
    SET status=?
    WHERE id=?
    """, ("Resolved", id))

    conn.commit()
    conn.close()

    flash("Complaint Resolved")

    return redirect('/admin_dashboard')


# =========================
# PENDING COMPLAINT
# =========================

@app.route('/pending/<int:id>', methods=['POST'])
def pending(id):

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE complaints
    SET status=?
    WHERE id=?
    """, ("Pending", id))

    conn.commit()
    conn.close()

    flash("Complaint Marked Pending")

    return redirect('/admin_dashboard')


# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.clear()

    flash("Logged Out Successfully")

    return redirect('/')


@app.route('/create_admin')
def create_admin():

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO admins(username, password)
    VALUES(?, ?)
    """, ("admin", "admin123"))

    conn.commit()
    conn.close()

    return "Admin Created"

#RUN APP

init_db()

app.run(debug=True)