from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
 
app = Flask(__name__)
app.secret_key = 'your_secret_key'
 
# Initialize DB and admin user
def init_db():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            dob TEXT,
            join_date TEXT,
            asset TEXT,
            role TEXT,
            certification TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    c.execute("SELECT * FROM admins WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                  ('admin', generate_password_hash('dev@1234')))
    conn.commit()
    conn.close()
 
init_db()
 
@app.route('/')
def home():
    if 'admin' in session:
        return redirect('/dashboard')
    return render_template('login.html')
 
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("SELECT password FROM admins WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and check_password_hash(result[0], password):
        session['admin'] = username
        return redirect('/dashboard')
    return 'Invalid credentials', 401
 
@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect('/')
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("SELECT * FROM employees")
    employees = c.fetchall()
    conn.close()
    return render_template('dashboard.html', employees=employees)
 
@app.route('/add', methods=['POST'])
def add():
    if 'admin' not in session:
        return redirect('/')
    data = (
        request.form['name'],
        request.form['dob'],
        request.form['join_date'],
        request.form['asset'],
        request.form['role'],
        request.form['certification']
    )
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO employees (name, dob, join_date, asset, role, certification)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()
    return redirect('/dashboard')
 
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['dob'],
            request.form['join_date'],
            request.form['asset'],
            request.form['role'],
            request.form['certification'],
            id
        )
        c.execute('''
            UPDATE employees SET name=?, dob=?, join_date=?, asset=?, role=?, certification=?
            WHERE id=?
        ''', data)
        conn.commit()
        conn.close()
        return redirect('/dashboard')
    else:
        c.execute("SELECT * FROM employees WHERE id=?", (id,))
        employee = c.fetchone()
        conn.close()
        return render_template('edit.html', employee=employee)
 
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("DELETE FROM employees WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')
 
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
