from mysql.connector import MySQLConnection
from read_config import read_db_config
from datetime import date, datetime, time


dbconfig = read_db_config()
conn = MySQLConnection(**dbconfig)
cursor = conn.cursor()

def write_in_ip_table(user, ip):
    today=date.today()
    now = datetime.now()
    current_time=time(hour=now.hour, minute=now.minute, second=now.second)
    end=time(hour=0, minute=0, second=0)

    cursor.execute("""INSERT INTO LoginIP (Benutzername, IP, Datum, Anfangsuhrzeit, Enduhrzeit) VALUES (%s, %s, %s, %s, %s)""", (user, ip, today, current_time, end))
    conn.commit()

def write_in_protocol_table(type, name, user, param):
    cursor.execute("""SELECT max(ProtokollID) FROM Protokoll""")
    id=cursor.fetchall()[0][0]
    if id==None:
        id=0
    else:
        id+=1

    type=int(type)
    if type==2:
        now = datetime.now()
        text="%s leiht %s von %s" % (name, param, now)


    cursor.execute("""INSERT INTO Protokoll (ProtokollID, Art, Text, gebucht, Datum) VALUES (%s, %s, %s, %s, %s)""", (id, int(type), str(text), str(user), now))
    conn.commit()

    return id