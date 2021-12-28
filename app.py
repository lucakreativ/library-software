from flask import Flask, render_template, request, redirect, session
import time
import get_data


app = Flask(__name__)
app.secret_key="sshh"


max_time_in_m=100
max_time_in_s=max_time_in_m*60


@app.route("/")
def home():
    if not check_login():
        return (redirect("/login"))
    else:
        site=request.args.get("site")
        if site==None:

            all=False

            name=request.args.get("name")
            if name==None:
                all=True
            table=get_data.book_by_user(name, all)
            return render_template("main.html", tables=[table.to_html(escape=False)],
            titles = ['na', 'Ausgeliehen'])


        elif site=="book_by_user":
            all=False

            name=request.args.get("name")
            if name==None:
                all=True
            return (str(get_data.book_by_user(name, all)))

        elif site=="return_book":
            ID=request.args.get("ID")
            if ID==None:
                return (redirect("/"))

            get_data.book_return(ID)

            return(redirect("/"))
        
        elif site=="books":
            ISBN=request.args.get("ISBN")
            Titel=request.args.get("Titel")

            data=get_data.print_books()
            return data


        elif site=="take_book":
            ISBN=request.args.get("ISBN")
            user=request.args.get("user")
            username=session["user"]

            if user!=None:
                get_data.taking_book(ISBN, user, username)
                return("True")
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
            id=request.args.get("id")

            if id!=None:
                get_data.keep_taking(id)
                return "True"
            else:
                return (redirect("/?site=get_data.book_by_user"))




        else:
            return("Seite nicht gefunden")






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
            #print("Falsch, Zeit zu lang")
            return False

    else:
        #print("Falsch, keine Session vorhanden")
        return False

def check_inactivity():
    delta=time.time()-float(session.get("login_time"))
    if delta<max_time_in_s:
        return True
    else:
        return False


        
app.run()