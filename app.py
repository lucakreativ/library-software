from flask import Flask, render_template, request, redirect, session
import random
import time
import os

import get_data # --> get_data.py


random_string=""

for i in range(16):
    secret_integer=random.randint(0, 255)       #erzeugt zufällige ASCII - Zahl
    random_string+=(chr(secret_integer))        #wandelt es zu einem Buchstaben um und wird zum String hinzugefügt

app = Flask(__name__)                           #App wird initialisiert
app.secret_key=random_string                    #übergibt den Zufallsstring um die Client-Session sicher zu halten


max_time_in_m=10                                #setzt inaktivitätszeit
max_time_in_s=max_time_in_m*60                  #wird in Sekunden umgerechnet


@app.route("/")                                 #wenn nur die Domain aufgerufen wird
def home():                                     #wird ausgeführt, wenn @pp.route richtig ist
    if not check_login():                       #überprüft, ob man schon eingeloggt ist
        return (redirect("/login"))             #wenn nicht, dann wird man auf Login-Page weitergeleitet
    else:
        site=request.args.get("site")           #bekommt den Seiten-Parameter
        if site==None:                          #ohne Parameter
            all=False
            name=request.args.get("user")       #bekommt den Namen
            if name==None:
                name=""
                all=True
            table=get_data.book_by_user(name, all)                                  #bekommt Data von den Ausgeliehen Büchern+Namen --> get_data.py
            return render_template("main.html", name=name,                          #lädt die Hauptseite und übergibt Werte zum anzeigen
            tables=[table.to_html(escape=False)], titles = ['na', 'Ausgeliehen'])   #Tabelle wird in HTML umgewandelt und dann angezeigt


        elif site=="return_book":                       #Wenn Seite Buch zurückgeben aufgerufen wird
            ID=request.args.get("ID")                   #Wird Ausleih-ID abgefragt
            if ID==None:                                #Wenn keine mitgegeben wurde, wird man zur Hauptseite weitergeleitet
                return (redirect("/"))

            get_data.book_return(ID)                    #Buch wird zurückgegeben mit der Ausleih-ID --> get_data.py

            return(redirect("/"))
        
        elif site=="books":                             #Buchverwaltung wird aufgerufen
            search=request.args.get("search")           #Fragt den Buch-Parameter ab

            if search==None:                            #keine Such request
                data=get_data.print_books()             #bekommt alle Bücher
                return render_template("book.html", search="",                      #lädt die HTML-Seite und übergibt Werte zum anzeigen                 
                tables=[data.to_html(escape=False)], titles = ['na', 'Bücher'])     #Tabelle wird in HTML umgewandelt und dann angezeigt
                
            else:
                data=get_data.search_book(search)                                   #bekommt Bücher mit Inhalt von "search"
                return render_template("book.html", search=search,                  #lädt die HTML-Seite und übergibt die Werte
                tables=[data.to_html(escape=False)], titles = ['na', 'Bücher'])     #Tabelle wird in HTML umgewandelt und dann angezeigt


        elif site=="take_book":             #wenn Seite Buchausleihen aufgerufen wird
            ISBN=request.args.get("ISBN")   #bekommt ISBN
            user=request.args.get("user")   #bekommt den Namen
            para=request.args.get("para")   #bekommt Computer-Generierten Parameter
            username=session["user"]        #bekommt den angemeldeten Benutzer

            if user!=None and para=="1":                        #Buch soll ausgeliehen werden
                get_data.taking_book(ISBN, user, username)      #übergibt die Parameter --> get_data.py
                return(redirect("/"))                           #wird zu Hauptseite weitergeleitet

            elif para=="0": #Name soll Manuelle gespeichert werden
                return render_template("select_user_manuel.html", ISBN=ISBN, text="Geben sie bitte den Namen Manuell ein") #Lädt die Seite zum Namen manuell eingeben

            elif user!=None:                                            #Nutzer wurde mitgegeben
                names, bo = get_data.get_microsoft_names(ISBN, user)    #bekommt alle Namen an der Schule und übergibt, ob welche gefunden wurden --> get_data.py

                if bo==True:                                            #Wenn Namen gefunden wurden
                    return render_template("select_user.html", ISBN=ISBN, tables=[names.to_html(escape=False)], titles = ['na', 'Namen'])   #lädt HTML-Seite, übergibt Werte und wandelt Tabelle in HTML um
                else:                                                   #Wenn keine Gefunden wurden
                    return render_template("select_user_manuel.html", ISBN=ISBN, text="Leider konnten wir keinen mit dem Namen finden, bitte geben sie den Namen manuell ein.") #lädt HTML-Seite und übergibt "kein Name wurde gefunden"
                

            else:                                                           #Alle anderen Fälle
                if ISBN!=None:                                              #ISBN wurde übergeben
                    return render_template("taking_book.html", ISBN=ISBN)   #lädt Seite um den Namen einzugeben und ISBN wird angezeigt
                else:                                                       #keine ISBN wurde übergeben
                    return render_template("taking_book.html", ISBN="")     #lädt die Seite ohne die ISBN eingetragen

        elif site=="insert_book":                                   #Seite Buch hinzufügen wurde aufgerufen
            autor=request.args.get("autor")                         #bekommt den Autor
            ISBN=request.args.get("ISBN")                           #bekommt die ISBN
            titel=request.args.get("titel")                         #bekommt den Buch-Titel

            get_data.insert_book(ISBN, titel, autor)                #fügt das Buch zur Datenbank hinzu --> get_data.py
            return redirect("/?site=book_by_ISBN&ISBN=%s" % (ISBN)) #weiterleitung zu Buch editier-seite

        elif site=="keep_book":                 #Seite Buch verlängern wurde aufgerufen
            id=request.args.get("ID")           #holt die Ausleih-ID

            if id!=None:                        #ID wurde mitgegeben
                get_data.keep_taking(id)        #verlängert Buch bei ID --> get_data.py
                return (redirect("/"))          #weiterleitung zur Hauptseite
            else:                               #keine ID wurde mitgegeben
                return (redirect("/"))          #wird zur Haupseite weitergeleitet

        elif site=="book_by_ISBN":              #Spezifisches Buch wurde aufgerufen
            save=request.args.get("save")       #bekommt ob speicher soll
            id=request.args.get("ID")           #bekommmt ID
            ISBN=request.args.get("ISBN")       #bekommt ISBN
            Titel=request.args.get("Titel")     #bekommt Titel
            Autor=request.args.get("Autor")     #bekommt Autor

            if save=="1":                                           #soll gespeichert werden
                get_data.update_book(ISBN, Titel, Autor, id)        #Daten werden zum Buch gespeichert --> get_data.py
                redirect("/?site=book_by_ISBN&ISBN=%s" % (ISBN))    #Seite wird neu geladen

            data=get_data.book_by_ISBN(ISBN)                        #ruft Daten zum Buch ab --> get_data.py

            return render_template("book_by_ISBN.html", ISBN=data[0], Titel=data[1], Autor=data[2] , ID=data[3]) #lädt HTML-Seite und gibt Daten zum zeigen mit
        
        elif site=="insert":                        #Buch hinzufügen Seite
            return render_template("insert.html")   #laden der HTML-Seite

        elif site=="settings":                      #Einstllungen werden aufgerufen
            message=request.args.get("message")     #Nachricht die angezeigt werden soll wird geholt
            if message!=None:                       #Wenn es eine gibt
                if message=="0":                    #0=Erfolgreich
                    me="Passwort wurde erfolgreich geändert"
                elif message=="1":                  #1=Fehler
                    me="Altes Passwort stimmt nicht überein"
                elif message=="2":                  #2=Fehler
                    me="Die neuen Passwörter stimmen nicht überein"

                return render_template("settings.html", Message=me)     #laden der HTML-Seite mit der Nachricht

            else:                                                       #wenn keine mitgegeben wird
                return render_template("settings.html")                 #laden der HTML-Seite ohne Nachricht

        elif site=="protocol":                          #Protokoll wurde aufgerufen
            table=get_data.return_protokoll()           #bekommt Protokoll als HTML-Code
            return table                                #Wird auf der Seite angezeigt



        elif site=="logout":                #ausloggen wird aufgerufe
            session.clear()                 #alle Daten werden gelöscht
            return(redirect("/login"))      #wird zur Login-Seite weitergeleitet

        else:                               #keine gültige Seite wurde aufgerufen
            return("Seite nicht gefunden")  #404-Page wird angezeigt




@app.route("/save_setting", methods=["POST"])       #Änderungen werden gepseichert und mit der Methode Post übergeben
def save_settting():                                #wird ausgeführt, wenn @app.route richtig ist
    if check_login():                               #überprüft, ob der Nutzer eingeloggt ist
        username=session["user"]                    #bekommt den angemeldeten Benutzer
        olrder=request.form.get("order")            #was geändert werden soll
        old_pass=request.form.get("old_pass")       #altes Passwort zu verifizierung
        new1_pass=request.form.get("new1_pass")     #neues Passwort
        new2_pass=request.form.get("new2_pass")     #neues Passwort wiederholung

        re=get_data.change_password(username, old_pass, new1_pass, new2_pass)   #Übergibt die Werte und bekommt message zurück

        return redirect("/?site=settings&message=%s" % (re))                    #wird zu Eintellungen weitergeleitet und message wird übergeben
    
    else:                                   #wenn man nicht eingeloggt ist
        return redirect("/login")           #wird man zur Login-Seite weitergeleitet


@app.route('/login')                        #Lgoin-Seite wurde aufgerufen
def login():                                #wird ausgeführt, wenn @app.route richtig ist
    return render_template("login.html")    #login-Seite wird angezeigt

@app.route("/loginf")                       #falsch eingeloggt
def loginf():                               #wird ausgeführt, wenn @app.route richtig ist
    return render_template("loginf.html")   #login-Seit wird angezeigt mit Error message

@app.route("/validate", methods=["POST"])                   #überprüft die Anmeldedaten
def validate():                                             #wird ausgeführt, wenn @app.route richtig ist
    username=request.form.get("username")                   #bekommt user-name
    password=request.form.get("password")                   #bekommt Passwort
    ip_addr = request.environ['REMOTE_ADDR']                #bekommt IP-Adresse vom Client
    if get_data.login(username, password, ip_addr)==True:   #übergibt die Anmeldedaten und bekommt True/False zurück --> get_data.py

        session["login"]=2                                  #speichert Login-State
        session["login_time"]=time.time()                   #speichert Login-Zeit für inactivitäts-check
        session["user"]=username                            #speichert den Benutzername

        return redirect("/")                #wird zu Hauptseite weitergeleitet
    else:                                   #wenn Anmeldedaten Falsch sind
        return redirect("/loginf")          #wird zur Anmeldeseite weitergeleitet und Fehlermeldung angezeigt
    

def check_login():                      #überprüft login
    if session.get("login")==2:         #überprüft Login-Fortschritt
        if check_inactivity()==True:    #überprüft Inaktivität
            return True                 #nicht Inaktiv
        else:
            return False                #Inaktiv

    else:
        return False                    #nicht eingeloggt

def check_inactivity():                                 #überprüft Inaktivität
    delta=time.time()-float(session.get("login_time"))  #Zeit seit letzter Aktivität
    if delta<max_time_in_s:                             #Wenn unterschied geringer als max_inaktivitätszeit
        session["login_time"]=time.time()               #speichert letzte Aktivität (Zeit)
        return True
    else:
        return False


port=int(os.environ.get("PORT", 5000))      #konfiguriert den Port
app.run(host="0.0.0.0", port=port)          #konfiguriert die und startet die App