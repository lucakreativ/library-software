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


def keep_taking(id):#verlängert Buch bei Ausleih-ID
    cursor.execute("UPDATE Ausleihen SET Verlängert=1 WHERE ID=%d" % (int(id)))#übergibt Daten zur Verlängerung
    conn.commit()#speichert Daten


def insert_book(ISBN, Titel, Autor):#fügt Buch hinzu
    cursor.execute("INSERT INTO Bücher (ISBN, Titel, Autor) VALUES (%s, %s, %s)", (ISBN, Titel, Autor))#übergibt ISBN, Titel und Autor der Datenbank
    conn.commit()#speichert Daten


def get_microsoft_names(ISBN, surname):
    names=get_name_microsoft.get_names_micro(surname) #bekommt alle Schüler bei Nachname/Teil

    data=pd.DataFrame(names)#Tabelle wird mit Pandas erstellt
    data=data.rename(columns={0:"Namen"})#ändert den Spalten-Namen

    for index in data.iterrows():#iteriert durch die Datenbenk
        num=index[0]#bekommt Tabellen-Nummer bei Index
        name=data.iloc[num]["Namen"]#bekommt Namen von der Tabelle

        data.at[num, "auswählen"]="""<form action="" method="get"><input type="hidden" name="site" value="take_book"><input type="hidden" name="para" value="1"><input type="hidden" name="ISBN" value="%s"><input type="hidden" name="user" value="%s"><input type="submit" value="auswäheln"></form>""" % (ISBN, name)#erstellt einen Knopf zum ausleihen auf den Schüler


    if len(names)>0:#Namen wurden gefunden
        return(data, True)#übergibt Namen und dass welche gefunden wurden
        
    else:#keine Namen wurden gefunden
        return(data, False)#übergibt leere Liste und dass keine gefunden wurden


def book_by_user(Name, all):#zeigt alle/von Nutzer ausgeliehenen Bücher an


    remove_row=[]#alle Einträge, die gelöscht werden sollen

    cursor.execute("SELECT Ausleihen.ID, Ausleihen.Schülername, Ausleihen.Datum, Bücher.Titel, Ausleihen.Verlängert, Ausleihen.ProtokollID FROM Ausleihen, Bücher WHERE Bücher.ISBN=Ausleihen.ISBN")#bekommt alle ausgeliehenen Bücher
    data=cursor.fetchall()#übergibt alle Daten


    data=pd.DataFrame(data, columns=["ID", "Name", "ausleih", "Titel", "Verlängert", "Protokoll-ID"])#ertsellt Tabelle mit Pandas und übergibt Spalten-Namen
    data.drop(data.columns[[5]], axis=1, inplace=True)#löscht unnötise Spalte

    data["unix"]=""#fügt Spalte mit ausleihzeit hinzu

    data["Verlängert"]=data["Verlängert"].replace(#ersetzt 1 mit "schon verlängert"
        to_replace=1,
        value="schon Verlängert"
    )

    data["Verlängert"]=data["Verlängert"].replace(#wandelt int in string um, sonst gibt es einen Bug
        to_replace=0,
        value="0"
    )
    data=data.drop_duplicates(subset=["ID"], keep="first")#löscht doppelte Einträge
    data=data.reset_index(drop=True)#vergibt neuen Index

    for index in data.iterrows():#iteriet durch die Datenbank
        num=index[0]#bekommt Tabellen-Nummer bei Index
        id=data.iloc[num]["ID"]#bekommt Ausleih-ID von Tabellen-Nummer

        if data.iloc[num]["Verlängert"]=="0":#wenn noch nicht verlängert wurde
            data.at[num, "Verlängert"]="""<form action="" method="get"><input type="hidden" name="site" value="keep_book"><input type="hidden" name="ID" value="%s"><input type="submit" value="verlängern"></form>""" % (str(id))#erstellt einen Knopf zum verlängern des Buchs

        if all==False:#wurde nach Name gesucht
            p_name=data.iloc[num]["Name"]#bekommt den Namen
            if Name not in p_name:#überprüft, ob es nicht der gesuchte Name ist
                remove_row.append(num)#fügt Reihe-Nummer hinzu, zum löschen

    data.drop(remove_row, inplace=True)#löschet allen Reihen in Liste

    data=data.reset_index(drop=True)#setzt den Index neu
    
    data["zurückgeben"]=""#fügt Tpalte hinzu

    for index in data.iterrows():#iteriet durch die angepasste Tabelle
        num=index[0]#bekommt Tabellen-Nummer bei Index
        id=data.iloc[num]["ID"]#Ausleih-Datei
        take_time=data.iloc[num]["ausleih"]#Ausleihdatum
        ver=data.iloc[num]["Verlängert"]#verlängert-Status
        start = datetime.strptime(str(take_time), "%Y-%m-%d")#wandelt String in Datetime um, zur Zeitrechnung
        enddate=start+timedelta(days=time_to_have)#Abgabezeitpunkt = Ausleihzeipunkt + Ausleihzeitraum (4 Wochen)

        if ver=="schon Verlängert":#wurde verlängert
            enddate=enddate+timedelta(days=time_to_have)#addiert nochmal 4 Wochen

        if enddate<datetime.now():#überprüft, ob das Buch überfällig ist
            cell="""<div id='to_late'><p>%s</p></div>""" % (enddate.strftime("%Y-%m-%d"))#ist überfällig, wird rot markiert und Abgabezeitpunkt angezeigt
        else:
            cell="""<div id='in_time'><p>%s</p></div>""" % (enddate.strftime("%Y-%m-%d"))#ist nicht überfällig, wird grün markiert und Abgabezeitpunkt angezeigt

        data.at[num, "ausleih"]=cell#wird in Spalte "ausleih" angezeigt

        unix=time.mktime(enddate.timetuple())#wandelt in Unix-Time um
        data.at[num, "unix"]=unix#wird in der Tabelle gespeichert

        data.at[num, "zurückgeben"]="""<form action="" method="get"><input type="hidden" name="site" value="return_book"><input type="hidden" name="ID" value="%s"><input type="submit" value="zurückgeben"></form>""" % (id)#fügt Knopf zum zurückgeben hinzu


    data=data.sort_values(by="unix")#sortiert die Tabelle nach Abgabazeitpunkt
    data=data.rename(columns={"ausleih":"Abgabe-Datum"})#umbenennen der Spalten
    data=data.reset_index(drop=True)#setzt den Index neu

    
    data.drop(columns=["unix", "ID"], inplace=True)#löschen unnötiger Spalten
        
    return data#gibt die Tabelle zurück


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