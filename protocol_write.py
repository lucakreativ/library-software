from mysql.connector import MySQLConnection
from datetime import date, datetime, time
from read_config import read_db_config, read_logging              # --> read_config.py
import logging


logs=read_logging()
lev="logging."+logs["level"]
logging.basicConfig(level=lev, filename='log.log')

def re_connect():                                   #setzt eine neue Verbindung, wegen MySQL timeout
    dbconfig = read_db_config()                     #benutzt library Config-Reder für die Konfiguration
    conn = MySQLConnection(**dbconfig)              #verbindung zur Datenbank wird hergestellt
    cursor = conn.cursor()                          #setzt den Curser, der die Befehle ausführt

    return cursor, conn                             #gibt den Cursor und die Verbindung zurück


def write_in_ip_table(user, ip):                                                #schreibt Login-Daten + IP
    cursor, conn = re_connect()                                                 #bekommt MySQL Verbindungsdaten

    today=date.today()                                                          #bekommt den heutigen Tag
    now = datetime.now()                                                        #bekommt den heutigen Tag + Uhrzeit
    current_time=time(hour=now.hour, minute=now.minute, second=now.second)      #bekommt die Uhrzeit
    end=time(hour=0, minute=0, second=0)                                        #Endzeit, provisorisch

    cursor.execute("""INSERT INTO LoginIP (Benutzername, IP, Datum, Anfangsuhrzeit, Enduhrzeit) VALUES (%s, %s, %s, %s, %s)""", (user, ip, today, current_time, end))#übergibt Benutzername, IP, Datum, Uhrzeit und Enduhrheit
    conn.commit()                                                               #speichert Änderungen

def write_in_protocol_table(type, name, user, param):               #schreibt in das Protokoll
    cursor, conn = re_connect()                                     #bekommt MySQL Verbindungsdaten

    cursor.execute("""SELECT max(ProtokollID) FROM Protokoll""")    #bekommt Protokoll-ID
    id=cursor.fetchall()[0][0]                                      #speichert sie
    if id==None:                                                    #Tabelle ist leer
        id=0
    else:                                                           #Tabelle ist nicht leer
        id+=1

    type=int(type)                                                  #Typ vom 
    if type==2:
        now = datetime.now()                                        #Datum + Uhrzeit
        text="%s leiht %s von %s" % (name, param, now)              #vorgefertigter Sting


    cursor.execute("""INSERT INTO Protokoll (ProtokollID, Art, Text, gebucht, Datum) VALUES (%s, %s, %s, %s, %s)""", (id, int(type), str(text), str(user), now))#übergibt Protokoll-ID, Typ, vorgefertigter String, Verleihname, Datum
    conn.commit()                                                   #speichert Änderungen

    return id                                                       #übergibt Protokoll-ID