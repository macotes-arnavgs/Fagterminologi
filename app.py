import os
import random
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, flash, url_for, session 

from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from MySQLdb import IntegrityError

app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")
app.config['MYSQL_HOST'] = os.getenv("DB_HOST")
app.config['MYSQL_USER'] = os.getenv("DB_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("DB_NAME")

mysql = MySQL(app) #

datainfo = {}
tilfeldigbegrep_id = None
bruker_id = None

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/index')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM begrep")
    antall_begrep = cur.fetchone()[0]
    
    global tilfeldigbegrep_id
    tilfeldigbegrep_id = random.randint(1, antall_begrep)

    cur.execute("SELECT begrep, fagnavn, begrep_definisjon \
                FROM begrep, fag WHERE idbegrep = " + str(tilfeldigbegrep_id) + " and fag.idfag = fag_idfag; ")
    data = cur.fetchall()
    datainfo['begrep'] = data[0][0] if data else "DHCP"
    datainfo['fag'] = data[0][1] if data else "Driftsstøtte"
    datainfo['definisjon'] = data[0][2] if data else "Denne definisjon skal oppdateres."

    cur.execute("select idbruker from bruker where navn = %s", [session['username']])
    bruker_id = cur.fetchone()[0]

    cur.execute("SELECT bruker_definisjon FROM bruker_kan_begrep WHERE begrep_idbegrep = %s AND bruker_idbruker = %s", (tilfeldigbegrep_id, bruker_id))
    data = cur.fetchall()

    datainfo['forrigedefinisjon'] = data[0][0] if data else ""
    cur.close()

    return render_template('index.html', **datainfo)

@app.route('/lagre-svar', methods=['POST'])
def lagre_svar():
    valg = request.form['mastery']
    bruker_def = request.form['bruker_definisjon'] if request.form.get('bruker_definisjon') else ""

    cur = mysql.connection.cursor()
    cur.execute("select idbruker from bruker where navn = %s", [session['username']])
    bruker_id = cur.fetchone()[0]

    try:
        cur.execute("""
            INSERT INTO bruker_kan_begrep (bruker_idbruker, begrep_idbegrep, valg, bruker_definisjon) 
            VALUES (%s, %s, %s, %s)
        """, (bruker_id, tilfeldigbegrep_id, str(valg), bruker_def))
        mysql.connection.commit()
        print("Suksess: Ny rad opprettet.")

    except IntegrityError as e:
        if e.args[0] == 1062:
            print("Duplicate entry funnet, kjører UPDATE i stedet.")
            mysql.connection.rollback() 
            
            cur.execute("""
                UPDATE bruker_kan_begrep 
                SET valg = %s, bruker_definisjon = %s 
                WHERE bruker_idbruker = %s AND begrep_idbegrep = %s
            """, (str(valg), bruker_def, bruker_id, tilfeldigbegrep_id))
            mysql.connection.commit()
        else:
            raise e

    cur.close()
    return redirect(url_for('index'))

@app.route('/registrer')
def login_page():
    return render_template('registrer.html')

@app.route('/auth', methods=['POST'])
def auth():
    bruker = request.form['bruker']
    passord_forsok = request.form['passord']

    cur = mysql.connection.cursor()
    cur.execute("SELECT passord FROM bruker WHERE navn = %s", [bruker])
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[0], passord_forsok):
        session['user_id'] = user[0]
        session['username'] = bruker
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

@app.route('/lagre', methods=['POST'])
def lagre():
    navn = request.form['navn']
    passord = request.form['passord']

    hash_passord = generate_password_hash(passord)

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO bruker (navn, passord) VALUES (%s, %s)", 
                (navn, hash_passord))
    
    mysql.connection.commit()
    cur.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)