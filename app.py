from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'apple_pie' 

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('todo.db')
        g.cursor = g.db.cursor()
    return g.db, g.cursor

# Close the SQLite connection at the end of each request
@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

@app.before_request
def before_request():
    get_db()

@app.route('/login', methods=['GET', 'POST'])
def login():

    db, cursor = g.db, g.cursor
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # find user in the database
        cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            # if user and password match db
            session['user_id'] = user[0]
            return redirect(url_for('tasks'))
        else:
            # invalidd login
            flash('Invalid username or password', 'error')

    return render_template('mainscreen/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    db, cursor = g.db, g.cursor
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # check availability
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already taken. Choose a different username.', 'error')
        else:
            # encrypt the password and add them to the db
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            db.commit()

            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('mainscreen/register.html')

@app.route('/')
def index():

    
    # checking loggin
    if 'user_id' not in session:
        return render_template('mainscreen/index.html')

    user_id = session['user_id']
    db, cursor = get_db()

    # find newest task
    cursor.execute("SELECT id, title, date_made, is_complete FROM tasks WHERE user_id = ? ORDER BY date_made DESC LIMIT 1", (user_id,))
    latest_task = cursor.fetchone()

    # find oldest task
    cursor.execute("SELECT id, title, date_made, is_complete FROM tasks WHERE user_id = ? AND is_complete = 0 ORDER BY date_made ASC LIMIT 1", (user_id,))
    oldest_active_task = cursor.fetchone()


    latest_task_with_names = {'id': latest_task[0], 'title': latest_task[1], 'date_made': latest_task[2], 'is_complete': latest_task[3]} if latest_task else None
    oldest_active_task_with_names = {'id': oldest_active_task[0], 'title': oldest_active_task[1], 'date_made': oldest_active_task[2], 'is_complete': oldest_active_task[3]} if oldest_active_task else None

    return render_template('mainscreen/index.html', latest_task=latest_task_with_names, oldest_active_task=oldest_active_task_with_names)


@app.route('/tasks')
def tasks():
    # checking login
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    db, cursor = get_db()   

    # all tasks to be added/found
    cursor.execute("SELECT id, title, date_made, is_complete FROM tasks WHERE user_id = ?", (user_id,))
    activetasks = cursor.fetchall()

    tasks_with_names = [{'id': id, 'title': title, 'date_made': date_made, 'is_complete': is_complete} for id, title, date_made, is_complete in activetasks]

    return render_template('mainscreen/alltasks.html', tasks=tasks_with_names)

@app.route('/add_task', methods=['POST'])
def add_task():

    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    db, cursor = get_db()

    title = request.form.get('title')
    date_made = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_complete = False

    cursor.execute("INSERT INTO tasks (user_id, title, date_made, is_complete) VALUES (?, ?, ?, ?)",
                   (user_id, title, date_made, is_complete))
    db.commit()

    referrer = request.form.get('referrer', url_for('index'))
    return redirect(referrer)

@app.route('/history')
def history():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    db, cursor = get_db()  

    cursor.execute("SELECT id, title, date_made FROM tasks WHERE user_id = ? AND is_complete = 1", (user_id,))
    completed_tasks = cursor.fetchall()

    return render_template('mainscreen/history.html', completed_tasks=completed_tasks)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)