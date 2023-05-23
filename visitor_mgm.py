from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    table_name = "Day_" + datetime.now().strftime("%Y_%m_%d")
    c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (name TEXT, contact TEXT, purpose TEXT, check_in DATETIME, check_out DATETIME)")
    c.execute(f"SELECT COUNT(*) FROM {table_name} WHERE check_out IS NULL")
    checkin_count = c.fetchone()[0]
    c.execute(f"SELECT COUNT(*) FROM {table_name} WHERE check_out IS NOT NULL")
    checkout_count = 0
    checkout_count = c.fetchone()[0]
    conn.close()
    return render_template('index.html', checkin_count=checkin_count, checkout_count=checkout_count)


@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    contact = request.form['contact']
    purpose = request.form['purpose']
    check_in = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    

    if is_visitor_checked_in(contact):
        message = "Visitor has already checked in."
    else:
       table_name = "Day_" + datetime.now().strftime("%Y_%m_%d")
       c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (name TEXT, contact TEXT, purpose TEXT, check_in DATETIME, check_out DATETIME)")
       c.execute(f"INSERT INTO {table_name} (name, contact, purpose, check_in) VALUES (?, ?, ?, ?)", (name, contact, purpose, check_in))
       conn.commit()
       message = "Visitor registered successfully."
    table_name = "Day_" + datetime.now().strftime("%Y_%m_%d")
    c.execute(f"SELECT COUNT(*) FROM {table_name} WHERE check_out IS NULL")
    checkin_count = c.fetchone()[0]
    c.execute(f"SELECT COUNT(*) FROM {table_name} WHERE check_out IS NOT NULL")
    checkout_count = c.fetchone()[0]
    conn.close()
    return render_template('index.html', checkin_count=checkin_count, checkout_count=checkout_count, message=message)
    
@app.route('/checkout', methods=['POST'])
def checkout():
    contact = request.form['contact']
    check_out = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
       

    if not is_visitor_checked_in(contact):
        message = "Visitor has not checked in or has already checked out."
    else:
       table_name = "Day_" + datetime.now().strftime("%Y_%m_%d")
       c.execute(f"UPDATE {table_name} SET check_out = ? WHERE contact = ? AND check_out IS NULL",          (check_out, contact))
       conn.commit()
       message = "Visitor checked out successfully."
    table_name = "Day_" + datetime.now().strftime("%Y_%m_%d")
    c.execute(f"SELECT COUNT(*) FROM {table_name} WHERE check_out IS NULL")
    checkin_count = c.fetchone()[0]
    c.execute(f"SELECT COUNT(*) FROM {table_name} WHERE check_out IS NOT NULL")
    checkout_count = c.fetchone()[0]
    conn.close()
    return render_template('index.html',checkin_count=checkin_count, checkout_count=checkout_count, message=message)



@app.route('/list_visitors', methods=['GET', 'POST'])
def list_visitors():
    if request.method == 'POST':
        selected_table = request.form['table']
        conn = sqlite3.connect('visitors.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM {selected_table}")

        visitors = c.fetchall()
        c.execute(f"SELECT COUNT(*) FROM {selected_table} WHERE check_out IS NULL")
        checkin_count = c.fetchone()[0]
        c.execute(f"SELECT COUNT(*) FROM {selected_table} WHERE check_out IS NOT NULL")
        checkout_count = c.fetchone()[0]
        conn.close()
        return render_template('visitors.html', checkin_count=checkin_count, checkout_count=checkout_count, visitors=visitors)

    # Retrieve all table names (days)
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = c.fetchall()
    conn.close()

    return render_template('list_visitors.html', tables=tables)




def is_visitor_checked_in(contact):
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    table_name = "Day_" + datetime.now().strftime("%Y_%m_%d")
    c.execute(f"SELECT * FROM {table_name} WHERE contact = ? AND check_out IS NULL", (contact,))
    result = c.fetchone()
    conn.close()
    return result is not None

if __name__ == '__main__':
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visitors
                 (name TEXT, contact TEXT, purpose TEXT, check_in DATETIME, check_out DATETIME)''')
    conn.commit()
    conn.close()

    app.run()
