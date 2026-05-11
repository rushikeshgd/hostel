from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

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

    # COMPLAINT TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        complaint TEXT,
        status TEXT
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

    conn.commit()
    conn.close()


# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():
    return render_template('index.html')


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

    return "Registration Successful"


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

        cursor.execute("""
        SELECT * FROM complaints
        WHERE username=?
        """, (username,))

        complaints = cursor.fetchall()

        conn.close()

        return render_template(
            "dashboard.html",
            username=username,
            complaints=complaints
        )

    else:

        conn.close()

        return "Invalid Username or Password"


# =========================
# SUBMIT COMPLAINT
# =========================

@app.route('/complaint', methods=['POST'])
def complaint():

    username = request.form['username']
    complaint = request.form['complaint']

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO complaints(username, complaint, status)
    VALUES(?, ?, ?)
    """, (username, complaint, "Pending"))

    conn.commit()
    conn.close()

    return "Complaint Submitted Successfully"


# =========================
# ADMIN REGISTER
# =========================

@app.route('/admin_register', methods=['POST'])
def admin_register():

    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect("hostel.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO admins(username, password)
    VALUES(?, ?)
    """, (username, password))

    conn.commit()
    conn.close()

    return "Admin Registration Successful"


# =========================
# ADMIN LOGIN
# =========================

@app.route('/admin_login', methods=['POST'])
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

        cursor.execute("""
        SELECT * FROM complaints
        """)

        complaints = cursor.fetchall()

        conn.close()

        return render_template(
            "admin_dashboard.html",
            complaints=complaints
        )

    else:

        conn.close()

        return "Invalid Admin Username or Password"


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

    return redirect('/')


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

    return redirect('/')


# =========================
# RUN APP
# =========================

init_db()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)