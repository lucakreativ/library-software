from flask import Flask, render_template, request, redirect, session
import time
import os
import random
import get_data


random_string=""

for i in range(16):
    secret_integer=random.randint(0, 255)   #erzeugt zufällige ASCII - Zahl
    random_string+=(chr(secret_integer))    #wandelt es zu einem Buchstaben um und wird zum String hinzugefügt

app = Flask(__name__)           #App wird initialisiert
app.secret_key=random_string    #übergibt den Zufallsstring um die Client-Session sicher zu halten


max_time_in_m=10                    #setzt inaktivitätszeit
max_time_in_s=max_time_in_m*60      #wird in Sekunden umgerechnet


@app.route("/")                             #wenn nur die IP-Adresse aufgerufen wird
def home():
    if not check_login():                   #überprüft, ob man schon eingeloggt ist
        return (redirect("/login"))         #wenn nicht, dann wird man auf Login-Page weitergeleitet
    else:
        site=request.args.get("site")       #bekommt den Seiten-Parameter
        if site==None:                      #Hauptseite
            all=False
            name=request.args.get("user")   #bekommt den Namen
            if name==None:
                name=""
                all=True
            table=get_data.book_by_user(name, all)                                  #bekommt Data von den Ausgeliehen Bücher+Namen
            return render_template("main.html", name=name,                          #lädt die Hauptseite und übergibt Werte zum anzeigen
            tables=[table.to_html(escape=False)], titles = ['na', 'Ausgeliehen'])   #Tabelle wird in HTML und dann angezeigt


        elif site=="return_book":           #Wenn Seite Buch zurückgeben aufgerufen wird
            ID=request.args.get("ID")       #Wird Ausleih-ID abgefragt
            if ID==None:                    #Wenn keine mitgegeben wurde, wird man zur Hauptseite weitergeleitet
                return (redirect("/"))

            get_data.book_return(ID)        #Buch wird zurückgegeben mit der Ausleih-ID

            return(redirect("/"))
        
        elif site=="books":                     #Buchverwaltung wird aufgerufen
            search=request.args.get("search")   #Fragt den Buch-Parameter ab

            if search==None:
                data=get_data.print_books()
                return render_template("book.html", search="",
                tables=[data.to_html(escape=False)], titles = ['na', 'Bücher'])
                
            else:
                data=get_data.search_book(search)
                return render_template("book.html", search=search,
                tables=[data.to_html(escape=False)], titles = ['na', 'Bücher'])


        elif site=="take_book":
            ISBN=request.args.get("ISBN")
            user=request.args.get("user")
            para=request.args.get("para")
            username=session["user"]

            if user!=None and para=="1":
                get_data.taking_book(ISBN, user, username)
                return(redirect("/"))

            elif para=="0":
                return render_template("select_user_manuel.html", ISBN=ISBN, text="Geben sie bitte den Namen Manuell ein")

            elif user!=None:
                names, bo = get_data.get_microsoft_names(ISBN, user)

                if bo==True:
                    return render_template("select_user.html", ISBN=ISBN, tables=[names.to_html(escape=False)], titles = ['na', 'Namen'])
                else:
                    return render_template("select_user_manuel.html", ISBN=ISBN, text="Leider konnten wir keinen mit dem Namen finden, bitte geben sie den Namen manuell ein.")
                

            else:
                if ISBN!=None:
                    return render_template("taking_book.html", ISBN=ISBN)
                else:
                    return render_template("taking_book.html", ISBN="")

        elif site=="insert_book":
            autor=request.args.get("autor")
            ISBN=request.args.get("ISBN")
            titel=request.args.get("titel")

            print(autor)
            print(ISBN)
            print(titel)
            get_data.insert_book(ISBN, titel, autor)
            return redirect("/?site=book_by_ISBN&ISBN=%s" % (ISBN))

        elif site=="keep_book":
            id=request.args.get("ID")

            if id!=None:
                get_data.keep_taking(id)
                return (redirect("/"))
            else:
                return (redirect("/"))

        elif site=="book_by_ISBN":
            save=request.args.get("save")
            id=request.args.get("ID")
            ISBN=request.args.get("ISBN")
            Titel=request.args.get("Titel")
            Autor=request.args.get("Autor")

            if save=="1":
                get_data.update_book(ISBN, Titel, Autor, id)
                redirect("/?site=book_by_ISBN&ISBN=%s" % (ISBN))

            data=get_data.book_by_ISBN(ISBN)

            return render_template("book_by_ISBN.html", ISBN=data[0], Titel=data[1], Autor=data[2] , ID=data[3])
        
        elif site=="insert":
            return render_template("insert.html")

        elif site=="settings":
            message=request.args.get("message")
            if message!=None:
                if message=="0":
                    me="Passwort wurde erfolgreich geändert"
                elif message=="1":
                    me="Altes Passwort stimmt nicht überein"
                elif message=="2":
                    me="Die neuen Passwörter stimmen nicht überein"

                return render_template("settings.html", Message=me)

            else:
                return render_template("settings.html")

        elif site=="protocol":
            table=get_data.return_protokoll()
            return table



        elif site=="logout":
            session.clear()
            return(redirect("/login"))

        else:
            return("Seite nicht gefunden")




@app.route("/save_setting", methods=["POST"])
def save_settting():
    if check_login():
        username=session["user"]
        old_pass=request.form.get("order")
        old_pass=request.form.get("old_pass")
        new1_pass=request.form.get("new1_pass")
        new2_pass=request.form.get("new2_pass")

        re=get_data.change_password(username, old_pass, new1_pass, new2_pass)

        return redirect("/?site=settings&message=%s" % (re))


@app.route('/login')
def login():
    return render_template("login.html")

@app.route("/loginf")
def loginf():
    return render_template("loginf.html")

@app.route("/validate", methods=["POST"])
def validate():
    check_login()
    username=request.form.get("username")
    password=request.form.get("password")
    ip_addr = request.environ['REMOTE_ADDR']
    if get_data.login(username, password, ip_addr)==True:

        session["login"]=2
        session["login_time"]=time.time()
        session["user"]=username

        return redirect("/")
    else:
        return redirect("/loginf")
    

def check_login():
    if session.get("login")==2:
        if check_inactivity()==True:
            return True
        else:
            return False

    else:
        return False

def check_inactivity():
    delta=time.time()-float(session.get("login_time"))
    if delta<max_time_in_s:
        return True
    else:
        return False


port=int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)