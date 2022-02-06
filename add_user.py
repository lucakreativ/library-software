import sys
from mysql.connector import MySQLConnection, Error
from read_config import read_db_config
from hash_pass import hash_password

dbconfig = read_db_config()
conn = MySQLConnection(**dbconfig)
cursor = conn.cursor()

type="Personal"

if len(sys.argv)!=4:
    print("zu much/zu less arguments")

username=sys.argv[1]
EMail=sys.argv[2]
password=sys.argv[3]

print("Username: "+username)
print("EMail: "+EMail)
print("Password: "+password)

hash=hash_password(password)
print("Hash: "+ hash)
cursor.execute("""INSERT INTO Benutzer (Benutzername, EMail, Passwort, Typ) VALUES (%s, %s, %s, %s)""", (username, EMail, hash, type))
conn.commit()

print("success")