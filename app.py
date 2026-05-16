import os # For å kunne bruke miljøvariabler fra .env-filen
import random # For å kunne velge et tilfeldig begrep fra databasen
from dotenv import load_dotenv # For å kunne laste miljøvariabler fra en .env-fil

# For å kunne lage en Flask-app, håndtere HTTP-forespørsler, og administrere brukerøkter
from flask import Flask, render_template, request, redirect, flash, url_for, session 

from flask_mysqldb import MySQL # For å kunne koble til og kommunisere med en MySQL-database
from werkzeug.security import check_password_hash, generate_password_hash # For å kunne hashe passord og sjekke hashede passord ved innlogging
from MySQLdb import IntegrityError # For å kunne håndtere unntak som oppstår ved databaseoperasjoner, spesielt for å fange opp duplikatoppføringer

app = Flask(__name__) # Oppretter en ny Flask-applikasjon

load_dotenv() # Lastes eksplisitt for å garantere portabilitet med .env-filen

app.secret_key = os.getenv("SECRET_KEY") #'din_hemmelige_nøkkel'
app.config['MYSQL_HOST'] = os.getenv("DB_HOST") # 'localhost' eller IP-adressen til MySQL-serveren
app.config['MYSQL_USER'] = os.getenv("DB_USER") # 'root' eller en annen MySQL-bruker med passende rettigheter
app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD") # 'passord' eller det faktiske passordet for MySQL-brukeren
app.config['MYSQL_DB'] = os.getenv("DB_NAME") # 'din_database' eller navnet på den MySQL-databasen du vil bruke

mysql = MySQL(app) #

datainfo = {} #en ordbok som skal inneholde data som skal sendes fra backend til frontend, som for eksempel
tilfeldigbegrep_id = None # En global variabel for å lagre ID-en til det tilfeldige begrepet som vises på index-siden. Denne variabelen vil bli oppdatert hver gang index-siden lastes, og brukes senere i lagre_svar-funksjonen for å knytte brukerens svar til det riktige begrepet i databasen.
bruker_id = None # En global variabel for å lagre ID-en til den innloggede brukeren. Denne variabelen vil bli oppdatert ved innlogging og brukes senere i lagre_svar-funksjonen for å knytte brukerens svar til riktig bruker i databasen.

@app.route('/') # Definerer en rute for rot-URL-en ("/") som vil håndtere HTTP GET-forespørsler. Når en bruker besøker denne URL-en, vil funksjonen home() bli kalt.
def home():
    return render_template('login.html') # Når home()-funksjonen kalles, vil den returnere HTML-siden "login.html" som ligger i "templates"-mappen. Denne siden vil bli vist til brukeren når de besøker rot-URL-en.

@app.route('/index') # Definerer en rute for URL-en "/index" som vil håndtere HTTP GET-forespørsler. Når en bruker besøker denne URL-en, vil funksjonen index() bli kalt.
def index():
    cur = mysql.connection.cursor() # Oppretter en ny databasekursor som lar oss utføre SQL-spørringer mot MySQL-databasen. Vi bruker mysql.connection.cursor() for å få tilgang til den aktive databaseforbindelsen og opprette en kursor som vi kan bruke til å sende SQL-kommandoer og hente resultater.
    cur.execute("SELECT COUNT(*) FROM begrep") # Utfører en SQL-spørring som teller det totale antallet rader i "begrep"-tabellen i databasen. Dette gir oss antall begreper som er lagret i databasen, og vi trenger dette for å kunne velge et tilfeldig begrep senere.
    antall_begrep = cur.fetchone()[0] # Henter det totale antallet begreper i databasen ved å utføre en SQL-spørring som teller antall rader i "begrep"-tabellen. Resultatet av spørringen er en tuple, og vi henter det første elementet (antallet) ved å bruke [0]. Dette tallet vil bli brukt senere for å velge et tilfeldig begrep fra databasen.
    
    global tilfeldigbegrep_id # Vi deklarerer at vi vil bruke den globale variabelen tilfeldigbegrep_id, slik at vi kan oppdatere den med ID-en til det tilfeldige begrepet som skal vises på index-siden. Dette gjør at vi senere kan referere til denne variabelen i lagre_svar-funksjonen for å knytte brukerens svar til det riktige begrepet i databasen.
    tilfeldigbegrep_id = random.randint(1, antall_begrep) # Velg en tilfeldig ID mellom 1 og antall_begrep. Dette vil være ID-en til det begrepet som skal vises på index-siden. Ved å bruke random.randint() kan vi sikre at vi får en gyldig ID som finnes i databasen, forutsatt at ID-ene i "begrep"-tabellen er sekvensielle og starter fra 1.   # tilfeldigbegrep_id = random.randint(1, antall_begrep) # Velg en tilfeldig ID mellom 1 og antall-begrep

    cur.execute("SELECT begrep, fagnavn, begrep_definisjon \
                FROM begrep, fag WHERE idbegrep = " + str(tilfeldigbegrep_id) + " and fag.idfag = fag_idfag; ")
    data = cur.fetchall() # Henter dataene for det tilfeldige begrepet
    datainfo['begrep'] = data[0][0] if data else "DHCP" # Setter begrepet i datainfo, eller "DHCP" hvis det ikke finnes
    datainfo['fag'] = data[0][1] if data else "Driftsstøtte" # Setter faget i datainfo, eller "Driftsstøtte" hvis det ikke finnes
    datainfo['definisjon'] = data[0][2] if data else "Denne definisjon skal oppdateres." # Setter definisjonen i datainfo, eller "Denne definisjon skal oppdateres." hvis det ikke finnes

    cur.execute("select idbruker from bruker where navn = %s", [session['username']]) # Utfører en SQL-spørring for å hente ID-en til den innloggede brukeren basert på deres brukernavn
    bruker_id = cur.fetchone()[0] # Henter ID-en til den innloggede brukeren

    cur.execute("SELECT bruker_definisjon FROM bruker_kan_begrep WHERE begrep_idbegrep = %s AND bruker_idbruker = %s", (tilfeldigbegrep_id, bruker_id))
    data = cur.fetchall() # Henter den eksisterende definisjonen for brukeren og det tilfeldige begrepet

    datainfo['forrigedefinisjon'] = data[0][0] if data else "" # Setter den eksisterende definisjonen i datainfo, eller en tom streng hvis det ikke finnes
    cur.close() # Lukker databasekursoren for å frigjøre ressurser og unngå potensielle minnelekkasjer. Det er god praksis å lukke kursoren når vi er ferdige med å bruke den, spesielt etter at vi har hentet all nødvendig data fra databasen.

    return render_template('index.html', **datainfo) #Når index()-funksjonen kalles, vil den returnere HTML-siden "index.html" som ligger i "templates"-mappen.

@app.route('/lagre-svar', methods=['POST']) # Definerer en rute for URL-en "/lagre-svar" som vil håndtere HTTP POST-forespørsler. Når en bruker sender inn et skjema på index-siden, vil denne funksjonen bli kalt for å lagre brukerens svar i databasen.
def lagre_svar():
    # Hent data fra formen
    valg = request.form['mastery'] # Henter valget fra skjemaet
    bruker_def = request.form['bruker_definisjon'] if request.form.get('bruker_definisjon') else "" # Henter brukerdefinisjonen fra skjemaet, eller setter den til en tom streng hvis den ikke er sendt inn

    # Lagre svaret i databasen
    cur = mysql.connection.cursor()
    cur.execute("select idbruker from bruker where navn = %s", [session['username']])
    bruker_id = cur.fetchone()[0]

    try: # Prøver å sette inn en ny rad i "bruker_kan_begrep"-tabellen med brukerens svar. Hvis det allerede finnes en rad for denne brukeren og dette begrepet, vil det kaste en IntegrityError på grunn av den unike begrensningen på kombinasjonen av bruker_idbruker og begrep_idbegrep.
        cur.execute("""
            INSERT INTO bruker_kan_begrep (bruker_idbruker, begrep_idbegrep, valg, bruker_definisjon) 
            VALUES (%s, %s, %s, %s)
        """, (bruker_id, tilfeldigbegrep_id, str(valg), bruker_def))
        mysql.connection.commit() # Hvis innsettingen er vellykket, committer vi transaksjonen for å lagre endringene i databasen. Dette gjør at den nye raden med brukerens svar blir permanent lagret i "bruker_kan_begrep"-tabellen.
        print("Suksess: Ny rad opprettet.")

    except IntegrityError as e: # Fanger opp IntegrityError som oppstår når det er en duplikatoppføring (dvs. når det allerede finnes en rad for denne brukeren og dette begrepet). Vi sjekker feilkoden for å bekrefte at det er en duplikatoppføring, og hvis det er tilfelle, ruller vi tilbake den feilede transaksjonen og utfører en UPDATE i stedet for å sette inn en ny rad.
        # Sjekker om feilkoden er 1062 (Duplicate entry)
        if e.args[0] == 1062:
            print("Duplicate entry funnet, kjører UPDATE i stedet.")
            # Vi må rulle tilbake den feilede transaksjonen før vi prøver på nytt
            mysql.connection.rollback() 
            
            cur.execute("""
                UPDATE bruker_kan_begrep 
                SET valg = %s, bruker_definisjon = %s 
                WHERE bruker_idbruker = %s AND begrep_idbegrep = %s
            """, (str(valg), bruker_def, bruker_id, tilfeldigbegrep_id))
            mysql.connection.commit()
        else:
            # Hvis det er en annen type IntegrityError, sender vi den videre
            raise e

    cur.close()
    return redirect(url_for('index')) # Etter at svaret er lagret (enten ved å sette inn en ny rad eller oppdatere en eksisterende), omdirigerer vi brukeren tilbake til index-siden for å vise det neste begrepet.

@app.route('/registrer')
def login_page():
    return render_template('registrer.html') # Når login_page()-funksjonen kalles, vil den returnere HTML-siden "registrer.html" som ligger i "templates"-mappen. Denne siden vil bli vist til brukeren når de besøker URL-en "/registrer". På denne siden kan brukeren fylle ut et skjema for å registrere en ny konto.

@app.route('/auth', methods=['POST'])
def auth():
    bruker = request.form['bruker']
    passord_forsok = request.form['passord']

    cur = mysql.connection.cursor()
    cur.execute("SELECT passord FROM bruker WHERE navn = %s", [bruker])
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[0], passord_forsok):# Sjekker om brukeren finnes og om det oppgitte passordet matcher det hashede passordet i databasen
        session['user_id'] = user[0] # Lagrer brukerens ID i økten for å holde dem innlogget
        session['username'] = bruker # Lagrer brukernavnet i økten for å kunne vise det i grensesnittet eller bruke det senere
        return redirect(url_for('index')) # Hvis innloggingen er vellykket, omdirigerer brukeren til index-siden
    else:
        return render_template('login.html') # Hvis innloggingen mislykkes, returnerer vi dem til login-siden. Vi kan også legge til en feilmelding her for å informere brukeren om at innloggingen mislyktes.

@app.route('/lagre', methods=['POST'])
def lagre(): # Denne funksjonen håndterer POST-forespørsler til URL-en "/lagre". Den brukes til å lagre en ny bruker i databasen når de registrerer seg. Funksjonen henter data fra registreringsskjemaet, hasher passordet, og lagrer deretter den nye brukeren i "bruker"-tabellen i MySQL-databasen.
    # 1. Hent data fra formen
    navn = request.form['navn']
    passord = request.form['passord'] # Her er passordet i klartekst enn så lenge

    # 2. HASHING: Vi gjør om passordet til en uleselig streng
    # 'pbkdf2:sha256' er standardmetoden
    hash_passord = generate_password_hash(passord)

    cur = mysql.connection.cursor()
    # 3. Lagre hash_passord i stedet for det ekte passordet
    cur.execute("INSERT INTO bruker (navn, passord) VALUES (%s, %s)", 
                (navn, hash_passord))
    
    mysql.connection.commit()
    cur.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Fjerner alle data fra økten, inkludert bruker_id og username, for å logge ut brukeren
    return redirect(url_for('home')) # Etter at økten er ryddet, omdirigerer vi brukeren tilbake til hjem-siden (login-siden)

if __name__ == '__main__':
    app.run(debug=True)