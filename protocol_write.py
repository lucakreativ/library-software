from logging import currentframe
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from datetime import date, datetime, time


import socket

dbconfig = read_db_config()
conn = MySQLConnection(**dbconfig)
cursor = conn.cursor()


h_name=socket.gethostname()

def write_in_ip_table(user):
    today=date.today()
    IP=socket.gethostbyname(h_name)
    now = datetime.now()
    current_time=time(hour=now.hour, minute=now.minute, second=now.second)
    end=time(hour=0, minute=0, second=0)

    cursor.execute("""INSERT INTO LoginIP (Benutzername, IP, Datum, Anfangsuhrzeit, Enduhrzeit) VALUES (%s, %s, %s, %s, %s)""", (user, IP, today, current_time, end))
    conn.commit()

def write_in_protocol_table(type, name, user, param):
    cursor.execute("""SELECT max(ProtokollID) FROM Protokoll""")
    id=int(cursor.fetchall()[0][0])
    id+=1

    type=int(type)
    if type==2:
        now = datetime.now()
        text="%s leiht %s von %s" % (name, param, now)


    cursor.execute("""INSERT INTO Protokoll (ProtokollID, Art, Text, gebucht, Datum) VALUES (%s, %s, %s, %s, %s)""", (id, int(type), str(text), str(user), now))
    conn.commit()

    return id