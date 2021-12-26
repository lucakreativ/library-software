from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from datetime import date
import hashlib
import pandas as pd




inactive_time_m=100
inactive_time_s=inactive_time_m*60
start_time=[0]
    
dbconfig = read_db_config()
conn = MySQLConnection(**dbconfig)
cursor = conn.cursor()





def print_all(table, table_name):
    cursor.execute("SELECT * FROM "+table)
    data=cursor.fetchall()

    data=pd.DataFrame(data, columns=table_name)
    
    html_table=data.to_html()
        
    return html_table


def print_books():
    cursor.execute("SELECT * FROM Bücher")
    data=cursor.fetchall()

    data=pd.DataFrame(data, columns=["ID", "ISBN", "Name", "Autor"])
    
    data["ISBN"]=data["ISBN"].apply(lambda x:'<a href="/?site=take_book&ISBN={0}">{0}</a>'.format(x))

    html_table=data.to_html(escape=False)
        
    return html_table
    

def keep_taking_print(id):
    cursor.execute("SELECT Verlängert FROM Ausleihen WHERE ID=%d" % (int(id)))
    inhalt=cursor.fetchall()
    print(inhalt)
    data=inhalt[0][0]
    return data


def keep_taking(id):
    cursor.execute("UPDATE Ausleihen SET Verlängert=1 WHERE ID=%d" % (int(id)))
    conn.commit()


def insert_book(ISBN, Titel, Autor):
    cursor.execute("INSERT INTO Bücher (ISBN, Titel, Autor) VALUES (%s, %s, %s)", (ISBN, Titel, Autor))
    conn.commit()


def book_by_user(Name, all):
    data=[]
    cursor.execute("SELECT * FROM Ausleihen")
    inhalt=cursor.fetchall()
    if all==False:
        for row in inhalt:
            if Name in row[1]:
                
                cursor.execute("SELECT * FROM Bücher WHERE ISBN=%s" % (row[2]))
                inhalt=cursor.fetchall()
                data.append(inhalt)
            
    else:
        cursor.execute("SELECT * FROM Ausleihen")
        data=cursor.fetchall()


    data=pd.DataFrame(data, columns=["ID", "Name", "ISBN", "Zeitpunkt des Ausleihen", "Verlängert", "Protokoll-ID"])
    data=data.drop("Protokoll-ID", 1)
    
    data["Verlängert"]=data["Verlängert"].apply(lambda x:'<a href="/?site=keep_book&id={0}">verlängern</a>'.format(x))

    data["Verlängert"]=data["Verlängert"].replace(
        to_replace="""<a href="/?site=keep_book&id=1">verlängern</a>""",
        value="schon Verlängert"
    )

    for index in data.iterrows():
        num=index[0]
        id=data.iloc[num]["ID"]

        if data.iloc[num]["Verlängert"]=="""<a href="/?site=keep_book&id=0">verlängern</a>""":
            data.at[num, "Verlängert"]="""<a href="/?site=keep_book&id=%s">verlängern</a>""" % (str(id))


    html_table=data.to_html(escape=False)
        
    return html_table


def book_return(ID):
    cursor.execute("DELETE FROM Ausleihen WHERE ID=%s" % (ID))
    conn.commit()


def taking_book(ISBN, Name):
    today=date.today()
    cursor.execute("INSERT INTO Ausleihen (Schülername, ISBN, Datum, Verlängert, ProtokollID) VALUES (%s, %s, %s, %s, %s)", (Name, int(ISBN), today, 0, 0))
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


def login(username, password_i):
    try:
        cursor.execute("SELECT Passwort FROM Benutzer WHERE Benutzername = '%s'" % (username))
        
        password=cursor.fetchall()
        password=password[0][0]
        hash=hash_password(password_i)
        

        if password==hash:
            return True
        else:
            return False
    except:
        return False