from mysql.connector import MySQLConnection, Error
from read_config import read_db_config      # --> read_config.py
from hash_pass import hash_password         # --> hash_pass.py
import sys


dbconfig = read_db_config()                 #benutzt library Config-Reader für die Konfiguration
conn = MySQLConnection(**dbconfig)          #verbindung zur Datenbank wird hergestellt
cursor = conn.cursor()                      #setzt den Curor, der die Befehle ausführt

type="Personal"

if len(sys.argv)!=4:                        #fragt ab, ob nicht alle Argumente eingegeben wurden
    print("zu much/zu less arguments")      #gibt Fehlermeldung zurück

username=sys.argv[1]                        #bekommt den Nutzernamen
EMail=sys.argv[2]                           #bekommt E-Mail Adresse
password=sys.argv[3]                        #bekommt Passwort

print("Username: "+username)                #gibt Daten zur verifizierung aus
print("EMail: "+EMail)
print("Password: "+password)

hash_i=hash_password(password)              #hasht das Passwort
print("Hash: "+ hash_i)
cursor.execute("""INSERT INTO Benutzer (Benutzername, EMail, Passwort, Typ) VALUES (%s, %s, %s, %s)""", (username, EMail, hash_i, type))#speicher in Tabelle Nutzer den Benutzername, E-Mail, den Hash und den Typ des Kontos
conn.commit()                               #speichert änderungen

print("success")