from flask import Flask, render_template, request, redirect, url_for, session, flash 
import mysql.connector 
from decimal import Decimal
from datetime import datetime
import logging
import uuid

app = Flask(__name__)
app.secret_key = 'Sarvesh@123'  

db_config = {
    'user': 'root',
    'password': 'Sarvesh@123',
    'host': 'localhost',
    'database': 'ledger_db'
}
@app.route('/')
def login():
    return render_template('pages-login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form['username']
    password = request.form['password']
    
    session['username'] = username
    return redirect(url_for('index'))

@app.route('/create_account')
def create_account():
    return render_template('pages-register.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    username = request.form['username']
    password = request.form['password']
    
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        
        flash('Account created successfully')
        return redirect(url_for('login'))

    except mysql.connector.Error as err:
        print(f"Error inserting user data: {err}")
        flash('Error inserting user data')
        return redirect(url_for('create_account'))

@app.route('/index')
def index():
    
    
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        query_accounts_receivable = "SELECT SUM(amount) FROM accounts_receivable"
        cursor.execute(query_accounts_receivable)
        total_receivable = cursor.fetchone()[0] or 0

        
        query_accounts_payable = "SELECT SUM(amount) FROM accounts_payable"
        cursor.execute(query_accounts_payable)
        total_payable = cursor.fetchone()[0] or 0

        query_monthly_receivable = "SELECT MONTH(date) AS month, SUM(amount) FROM accounts_receivable GROUP BY MONTH(date)"
        cursor.execute(query_monthly_receivable)
        monthly_receivable = cursor.fetchall()

        query_monthly_payable = "SELECT MONTH(ap_date) AS month, SUM(amount) FROM accounts_payable GROUP BY MONTH(ap_date)"
        cursor.execute(query_monthly_payable)
        monthly_payable = cursor.fetchall()

    
        query_due_dates = """
            SELECT 'Accounts Receivable' AS type, due_date FROM accounts_receivable
            UNION
            SELECT 'Accounts Payable' AS type, due_date FROM accounts_payable
        """
        cursor.execute(query_due_dates)
        due_dates = cursor.fetchall()

        cursor.close()
        cnx.close()

        def decimal_to_float(data):
            if isinstance(data, Decimal):
                return float(data)
            elif isinstance(data, (list, tuple)):
                return [decimal_to_float(item) for item in data]
            elif isinstance(data, dict):
                return {key: decimal_to_float(value) for key, value in data.items()}
            else:
                return data

        monthly_receivable_dict = {month: float(amount) for month, amount in monthly_receivable}
        monthly_payable_dict = {month: float(amount) for month, amount in monthly_payable}
        due_dates_dict = {type: [due_date.isoformat() for (type, due_date) in due_dates]}

        return render_template('index.html',
                               total_receivable=total_receivable,
                               total_payable=total_payable,
                               monthly_receivable=monthly_receivable_dict,
                               monthly_payable=monthly_payable_dict,
                               due_dates=due_dates_dict)

    except mysql.connector.Error as err:
        print(f"Error fetching data: {err}")
        return "Error fetching data"


@app.route('/messages')
def messages():
    return render_template('messages.html')

@app.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template('pages-terms&conditions.html')
@app.route('/accounts_receivable_form')
def accounts_receivable_form():
    return render_template('accounts_receivable_form.html')

@app.route('/add_accounts_receivable', methods=['POST'])
def add_accounts_receivable():
    date = request.form['date']
    description = request.form['description']
    amount = float(request.form['amount'])
    customer = request.form['customer']
    due_date = request.form['due_date']
    invoice_id = request.form.get('invoice_id', str(uuid.uuid4()))  
    
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        query = "INSERT INTO accounts_receivable (date, description, amount, customer, due_date, invoice_id) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (date, description, amount, customer, due_date, invoice_id))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        
        return redirect(url_for('finance_accounts_receivable'))

    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
        return f"Error inserting data: {err}"

@app.route('/finance_accounts_receivable')
def finance_accounts_receivable():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
    
        query = "SELECT date, description, amount, customer, due_date FROM accounts_receivable"
        cursor.execute(query)
    
        receivable_entries = cursor.fetchall()
    
        cursor.close()
        cnx.close()
    
        return render_template('finance_accounts_receivable.html', receivable_entries=receivable_entries)
    
    except mysql.connector.Error as err:
        print(f"Error fetching accounts receivable data: {err}")
        return "Error fetching data"

@app.route('/accounts_payable_form')
def accounts_payable_form():
    return render_template('accounts_payable_form.html')

@app.route('/add_accounts_payable', methods=['POST'])
def add_accounts_payable():
    date = request.form['date']
    description = request.form['description']
    amount = float(request.form['amount'])
    vendor = request.form['vendor']
    due_date = request.form['due_date']
    
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        query = "INSERT INTO accounts_payable (ap_date, description, amount, vendor, due_date) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (date, description, amount, vendor, due_date))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        
        return redirect(url_for('finance_accounts_payable'))

    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
        return "Error inserting data"

@app.route('/finance_accounts_payable')
def finance_accounts_payable():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
    
        query = "SELECT ap_date, description, amount, vendor, due_date FROM accounts_payable"
        cursor.execute(query)
    
        payable_entries = cursor.fetchall()
    
        cursor.close()
        cnx.close()
    
        return render_template('finance_accounts_payable.html', payable_entries=payable_entries)
    
    except mysql.connector.Error as err:
        print(f"Error fetching accounts payable data: {err}")
        return "Error fetching data"

@app.route('/finance_general_ledger')
def finance_general_ledger():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

    
        query_accounts_receivable = "SELECT date AS date, '' AS debit, amount AS credit, customer AS vendor_or_customer, due_date, '' AS balance FROM accounts_receivable"
        cursor.execute(query_accounts_receivable)
        receivable_entries = cursor.fetchall()

        
        query_accounts_payable = "SELECT ap_date, amount AS debit, '' AS credit, vendor, due_date, '' AS balance FROM accounts_payable"
        cursor.execute(query_accounts_payable)
        payable_entries = cursor.fetchall()

    
        max_length = max(len(receivable_entries), len(payable_entries))

        
        cursor.close()
        cnx.close()

        return render_template('finance_general_ledger.html',
                               receivable_entries=receivable_entries,
                               payable_entries=payable_entries,
                               max_length=max_length)

    except mysql.connector.Error as err:
        print(f"Error retrieving data: {err}")
        return "Error fetching data"

@app.route('/cash_management_form')
def cash_management_form():
    return render_template('cash_management_form.html')

@app.route('/add_cash_management', methods=['POST'])
def add_cash_management():
    date = request.form['date']
    description = request.form['description']
    cash_inflow = request.form['cash_inflow']
    cash_outflow = request.form['cash_outflow']

    print(f"Form Data: date={date}, description={description}, cash_inflow={cash_inflow}, cash_outflow={cash_outflow}")

    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        query = "INSERT INTO cash_management (date, description, cash_inflow, cash_outflow) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (date, description, cash_inflow, cash_outflow))
        cnx.commit()

        cursor.close()
        cnx.close()

        print("Data inserted successfully")
        return redirect(url_for('finance_cash_management'))

    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
        return "Error inserting data"

@app.route('/finance_cash_management')
def finance_cash_management():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        query = "SELECT date, description, cash_inflow, cash_outflow FROM cash_management"
        cursor.execute(query)

        cash_entries = cursor.fetchall()

        cursor.close()
        cnx.close()

        return render_template('finance_cash_management.html', cash_entries=cash_entries)

    except mysql.connector.Error as err:
        print(f"Error fetching cash management data: {err}")
        return "Error fetching data"

@app.route('/generate_bill/<int:bill_id>')
def generate_bill(bill_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        query = "SELECT ap_date, description, amount, vendor, due_date FROM accounts_payable WHERE id = %s"
        cursor.execute(query, (bill_id,))
        bill = cursor.fetchone()

        if bill:
            
            bill_data = {
                'ap_date': bill[0],
                'description': bill[1],
                'amount': bill[2],
                'vendor': bill[3],
                'due_date': bill[4]
            }
        else:
            return "Bill not found", 404

        cursor.close()
        cnx.close()

        return render_template('generate_bill.html', bill=bill_data)

    except mysql.connector.Error as err:
        print(f"Error fetching bill data: {err}")
        return "Error fetching data"

logging.basicConfig(level=logging.DEBUG)

@app.route('/generate_invoice/<int:invoice_id>')
def generate_invoice(invoice_id):
    try:
        logging.debug('Connecting to the database...')
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        logging.debug('Connected to the database.')

        query = "SELECT date, description, amount, customer, due_date, invoice_id FROM accounts_receivable WHERE invoice_id = %s"
        cursor.execute(query, (invoice_id,))
        invoice = cursor.fetchone()
        logging.debug(f'Executed query: {query}')

        if invoice:
            logging.debug(f'Invoice data: {invoice}')
        else:
            logging.debug('Invoice not found.')
            return "Invoice not found", 404

        cursor.close()
        cnx.close()

        logging.debug('Rendering template...')
        return render_template('generate_invoice.html', invoice=invoice)

    except mysql.connector.Error as err:
        logging.error(f"Error fetching invoice data: {err}")
        return f"Error fetching data: {err}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
