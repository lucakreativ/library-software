from mysql.connector import MySQLConnection, Error
import protocol_write
from read_config import read_db_config
from datetime import date
from datetime import datetime
from datetime import timedelta
import hashlib
import pandas as pd
import get_name_microsoft
import time



inactive_time_m=10 #setzt die maximale Inaktivitätszeit
inactive_time_s=inactive_time_m*60 #wird in Sekunden umgerechnet
start_time=[0]  #speicher für Login-Zeit
time_to_have=7*4 #wie lange ein Buch ausgeliehen werden darf
    
dbconfig = read_db_config() #benutzt library Config-Reder für die Konfiguration
conn = MySQLConnection(**dbconfig) #verbindung zur Datenbank wird hergestellt

cursor = conn.cursor() #setzt den Curser, der die Befehle ausführt





def print_all(table, table_name): #eine komplette Tabelle soll ausgegeben werden
    cursor.execute("SELECT * FROM "+table) #führt den Befehl aus
    data=cursor.fetchall()#übergibt die Daten

    data=pd.DataFrame(data, columns=table_name) #Tabelle wird mit Pandas erstellt und übergibt die Spalten-Namen
    
    html_table=data.to_html()#Tabelle wird in HTML-Code umgewandelt
        
    return html_table#übergibt die HTML-Tabelle

def print_books():#alle gespeicherten Bücher sollen angezeigt werden
    cursor.execute("SELECT ISBN, Titel, Autor FROM Bücher")#bekommt ISBN, Titel, Autor von Tabelle Bücher
    data=cursor.fetchall()#übergibt die Daten

    data=pd.DataFrame(data, columns=["ISBN", "Name", "Autor"])#Tabelle wird mit Pandas erstellt und übergibt die Spalten-Namen
    
    data["ISBN"]=data["ISBN"].apply(lambda x:'<a href="/?site=book_by_ISBN&ISBN={0}">{0}</a>'.format(x))#Link mit spezieller ISBN für die Veränderung der Buch-Daten

    return data#übergibt die Tabelle


def search_book(search_term): #suche nach Buch
    cursor.execute("SELECT ISBN, Titel, Autor FROM Bücher WHERE Titel LIKE '%"+search_term+"%' OR ISBN LIKE '%"+search_term+"%'")  #sucht nach ISBN oder Titel  


    data=cursor.fetchall()#übergibt die Daten

    data=pd.DataFrame(data, columns=["ISBN", "Name", "Autor"])#erstellt Tabelle mit den Spalten-Namen

    data["ISBN"]=data["ISBN"].apply(lambda x:'<a href="/?site=book_by_ISBN&ISBN={0}">{0}</a>'.format(x))#Link mit spezieller ISBN für die Veränderung der Buch-Daten
        
    return data#übergibt die Tabelle


def update_book(ISBN, Titel, Autor, id):#Daten vom Buch aktualisieren
    cursor.execute("""UPDATE Bücher SET ISBN='%s', Titel='%s', Autor='%s' WHERE ID='%s'""" % (ISBN, Titel, Autor, id))#übergibt Daten in der Datenbank
    conn.commit()#speichert Daten in Datenbank


def book_by_ISBN(ISBN):#bekommt Buchdaten für die Bearbeitung
    cursor.execute("SELECT ISBN, Titel, Autor, ID FROM Bücher WHERE ISBN='%s'" % (ISBN))#holt Daten aus Datenbank, per ISBN
    data=cursor.fetchall()[0]#bekommt 1st Element
    return data #übergibt Liste mit Informationen


def keep_taking_print(id):
    cursor.execute("SELECT Verlängert FROM Ausleihen WHERE ID=%d" % (int(id)))
    data=cursor.fetchall()[0][0]
    return data


def keep_taking(id):
    cursor.execute("UPDATE Ausleihen SET Verlängert=1 WHERE ID=%d" % (int(id)))
    conn.commit()


def insert_book(ISBN, Titel, Autor):
    cursor.execute("INSERT INTO Bücher (ISBN, Titel, Autor) VALUES (%s, %s, %s)", (ISBN, Titel, Autor))
    conn.commit()


def get_microsoft_names(ISBN, surname):
    names=get_name_microsoft.get_names_micro(surname)



    data=pd.DataFrame(names)
    data=data.rename(columns={0:"Namen"})

    for index in data.iterrows():
        num=index[0]
        name=data.iloc[num]["Namen"]

        data.at[num, "auswählen"]="""<form action="" method="get"><input type="hidden" name="site" value="take_book"><input type="hidden" name="para" value="1"><input type="hidden" name="ISBN" value="%s"><input type="hidden" name="user" value="%s"><input type="submit" value="auswäheln"></form>""" % (ISBN, name)


    if len(names)>0:
        return(data, True)
        
    else:
        return(data, False)


def book_by_user(Name, all):


    remove_row=[]

    cursor.execute("SELECT Ausleihen.ID, Ausleihen.Schülername, Ausleihen.Datum, Bücher.Titel, Ausleihen.Verlängert, Ausleihen.ProtokollID FROM Ausleihen, Bücher WHERE Bücher.ISBN=Ausleihen.ISBN")
    data=cursor.fetchall()


    data=pd.DataFrame(data, columns=["ID", "Name", "ausleih", "Titel", "Verlängert", "Protokoll-ID"])
    data.drop(data.columns[[5]], axis=1, inplace=True)

    data["unix"]=""

    data["Verlängert"]=data["Verlängert"].replace(
        to_replace=1,
        value="schon Verlängert"
    )
    data=data.drop_duplicates(subset=["ID"], keep="first")
    data=data.reset_index(drop=True)

    for index in data.iterrows():
        num=index[0]
        id=data.iloc[num]["ID"]

        if data.iloc[num]["Verlängert"]==0:
            data.at[num, "Verlängert"]="""<form action="" method="get"><input type="hidden" name="site" value="keep_book"><input type="hidden" name="ID" value="%s"><input type="submit" value="verlängern"></form>""" % (str(id))

        if all==False:
            p_name=data.iloc[num]["Name"]
            if Name not in p_name:
                remove_row.append(num)

    data.drop(remove_row, inplace=True)

    data=data.reset_index(drop=True)
    


    for index in data.iterrows():
        num=index[0]
        take_time=data.iloc[num]["ausleih"]
        ver=data.iloc[num]["Verlängert"]
        start = datetime.strptime(str(take_time), "%Y-%m-%d")
        enddate=start
        enddate=start+timedelta(days=time_to_have)

        if ver=="schon Verlängert":
            enddate=enddate+timedelta(days=time_to_have)

        if enddate<datetime.now():
            cell="""<div id='to_late'><p>%s</p></div>""" % (enddate.strftime("%Y-%m-%d"))
        else:
            cell="""<div id='in_time'><p>%s</p></div>""" % (enddate.strftime("%Y-%m-%d"))

        data.at[num, "ausleih"]=cell

        unix=time.mktime(enddate.timetuple())
        data.at[num, "unix"]=unix


    data["zurückgeben"]=""

    for index in data.iterrows():
        num=index[0]
        id=data.iloc[num]["ID"]

        data.at[num, "zurückgeben"]="""<form action="" method="get"><input type="hidden" name="site" value="return_book"><input type="hidden" name="ID" value="%s"><input type="submit" value="zurückgeben"></form>""" % (id)


    data=data.sort_values(by="unix")
    data=data.rename(columns={"ausleih":"Abgabe-Datum"})
    data=data.reset_index(drop=True)

    
    data.drop(columns=["unix", "ID"], inplace=True)
        
    return data


def return_protokoll():
    cursor.execute("SELECT * FROM Protokoll")
    data=cursor.fetchall()

    data=pd.DataFrame(data, columns=["ID", "ProtokollID", "Art", "Text", "gebucht", "Datum"])
    html_table=data.to_html()

    return html_table


def book_return(ID):
    cursor.execute("DELETE FROM Ausleihen WHERE ID=%s" % (ID))
    conn.commit()


def taking_book(ISBN, Name, user):
    id=protocol_write.write_in_protocol_table(2, Name, user, ISBN)
    today=date.today()
    cursor.execute("INSERT INTO Ausleihen (Schülername, ISBN, Datum, Verlängert, ProtokollID) VALUES (%s, %s, %s, %s, %s)", (Name, int(ISBN), today, 0, id))
    conn.commit()


    

def new_user(Benutzername, EMail, Passwort, Typ):
    hash=hash_password(Passwort)
    cursor.execute("""INSERT INTO Benutzer (Benutzername, EMail, Passwort, Typ) VALUES (%s, %s, %s, %s)""", (Benutzername, EMail, hash, Typ))
    conn.commit()


def hash_password(hash):
    i=0
    while i <314:
        i+=1
        hash=hashlib.sha512(str(hash).encode("utf-8")).hexdigest()
    return hash


def change_password(username, old_pass, new1_pass, new2_pass):
    cursor.execute("""SELECT Passwort FROM Benutzer WHERE Benutzername = '%s'""" % (username))
    database_pass=cursor.fetchall()[0][0]
    
    old_hash=hash_password(old_pass)
    if old_hash==database_pass:
        if new1_pass==new2_pass:
            new_pass_hash=hash_password(new1_pass)
            cursor.execute("""UPDATE Benutzer SET Passwort = '%s' WHERE Benutzername = '%s'""" % (new_pass_hash, username))
            conn.commit()
            return 0 #success
        else:
            return 2 #not same password
    else:
        return 1 #incorrect password


def login(username, password_i, ip):
    try:
        cursor.execute("SELECT Passwort FROM Benutzer WHERE Benutzername = '%s'" % (username))
        
        password=cursor.fetchall()
        password=password[0][0]
        hash=hash_password(password_i)
        

        if str(password)==str(hash):
            protocol_write.write_in_ip_table(username, ip)

            return True
        else:
            return False
    except:
        return False