from flask import Flask, render_template, request, redirect, flash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "secret123"

# Database Connection
def connect_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create Table
def create_table():
    conn = connect_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_table()

# Home Page
@app.route('/')
def index():
    conn = connect_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template("index.html", students=students)

# Add Student
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        age = request.form['age'].strip()

        # Validation
        if name == "" or email == "" or age == "":
            flash("All fields are required!")
            return redirect('/add')

        if not re.match(r'^[A-Za-z ]+$', name):
            flash("Name must contain letters only!")
            return redirect('/add')

        if not re.match(r'^\S+@\S+\.\S+$', email):
            flash("Invalid Email!")
            return redirect('/add')

        if not age.isdigit():
            flash("Age must be number!")
            return redirect('/add')

        try:
            conn = connect_db()
            conn.execute("INSERT INTO students(name,email,age) VALUES(?,?,?)",
                         (name, email, age))
            conn.commit()
            conn.close()
            flash("Student Added Successfully!")
            return redirect('/')
        except:
            flash("Email already exists!")
            return redirect('/add')

    return render_template("add.html")

# Edit Student
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = connect_db()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']

        try:
            conn.execute(
                "UPDATE students SET name=?, email=?, age=? WHERE id=?",
                (name, email, age, id)
            )
            conn.commit()
            flash("Updated Successfully!")
            return redirect('/')
        except:
            flash("Error Updating Record")

    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", student=student)

# Delete Student
@app.route('/delete/<int:id>')
def delete(id):
    try:
        conn = connect_db()
        conn.execute("DELETE FROM students WHERE id=?", (id,))
        conn.commit()
        conn.close()
        flash("Deleted Successfully!")
    except:
        flash("Delete Failed!")

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)