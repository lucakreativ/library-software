from flask import Flask, render_template, request, redirect, session
import time
import get_data


app = Flask(__name__)
app.secret_key="sshh"


max_time_in_m=10
max_time_in_s=max_time_in_m*60


@app.route("/")
def home():
    if not check_login():
        return (redirect("/login"))
    else:
        site=request.args.get("site")
        if site==None:
            all=False
            name=request.args.get("user")
            if name==None:
                name=""
                all=True
            table=get_data.book_by_user(name, all)
            return render_template("main.html", name=name,
            tables=[table.to_html(escape=False)], titles = ['na', 'Ausgeliehen'])


        elif site=="return_book":
            ID=request.args.get("ID")
            if ID==None:
                return (redirect("/"))

            get_data.book_return(ID)

            return(redirect("/"))
        
        elif site=="books":
            search=request.args.get("search")

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

            if autor!=None and ISBN!=None and titel!=None:
                get_data.insert_book(ISBN, titel, autor)
            else:
                return render_template("insert_book.html")

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
        

        elif site=="settings":
            message=request.args.get("message")
            if message!=None:
                if message=="0":
                    me="Passwort wurde erfolgreich geändert"
                elif message=="1":
                    me="Passwort stimmt nicht überein"
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
    if get_data.login(username, password)==True:

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


        
app.run()