from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'many random bytes'
#database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'akin'

mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            data = cur.fetchone()
            if password == data[1]:  # Assuming 'password' is the second column in the query result
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('Index'))
            else:
                flash('Invalid password', 'Invalid Credentials')
        else:
            flash('Username not found', 'Invalid Credentials')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/')
def Index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', students=data)

@app.route('/search', methods=['GET'])
def search():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    query = request.args.get('query')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students WHERE name LIKE %s OR email LIKE %s", ('%' + query + '%', '%' + query + '%'))
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', students=data)

@app.route('/insert', methods=['POST'])
def insert():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == "POST":
        flash("Data Inserted Successfully")
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students (Sname, Cemail, contact) VALUES (%s, %s, %s)", (name, email, phone))
        mysql.connection.commit()
        return redirect(url_for('Index'))

@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('Index'))

@app.route('/update', methods=['POST'])
def update():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE students SET Sname=%s, Cemail=%s, contact=%s
        WHERE id=%s
        """, (name, email, phone, id_data))
        mysql.connection.commit()
        flash("Data Updated Successfully")
        return redirect(url_for('Index'))

if __name__ == '__main__':
    app.run(debug=True)
