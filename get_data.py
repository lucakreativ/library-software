from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from datetime import date
import time
import os
import hashlib
import sys
import pandas as pd




inactive_time_m=0.1
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
    

#Bücher werden hinzugefügt
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
    
    html_table=data.to_html()
        
    return html_table



def book_return(ID):
    cursor.execute("DELETE FROM Ausleihen WHERE ID=%s" % (ID))
    conn.commit()


def taking_book(ISBN, Name):
    today=date.today()
    cursor.execute("INSERT INTO Ausleihen (Schülername, ISBN, Datum, Verlängert, ProtokollID) VALUES (%s, %s, %s, %s, %s)", (Name, int(ISBN), today, 0, 0))
    conn.commit()


    

#Datenbank nimmt nur Varchar an, wird als Bytes aber gesendet
def new_user(Benutzername, EMail, Passwort, Typ):
    
    hash=hash_password(Passwort)
    cursor.execute("""INSERT INTO Benutzer (Benutzername, E_Mail, Passwort, Typ) VALUES (%s, %s, %s, %s)""", (Benutzername, EMail, hash[0:1], Typ))
    conn.commit()


def hash_password(hash):
    i=0
    while i <1000:
        i+=1
        hash=hashlib.sha512(str(hash).encode("utf-8")).hexdigest()
    
    return hash


def login(username, password):
    cursor.execute("SELECT * FROM Benutzer WHERE Benutzername=%s" % (username))
    inhalt=cursor.fetchall()
    print(inhalt)







ISBN="123456"
Titel="Mon der Kuck"
Autor="Lu"
Name="ekun"
#insert_book(ISBN, Titel, Autor)
#book_return("", True)
#taking_book(ISBN, "Kevin Günter")


#book_by_user("", True)

new_user("Burek-Test", "burek@schiller.d", "pass", "Personal")
#login("Heribert", "test")