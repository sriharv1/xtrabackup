#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3
import pymysql
import pandas
db = pymysql.connect("zbxdevapp01.northamerica.cerner.net", "zabbix", "zabbix", "zabbix")
try:
     if db.open:
          # prepare a cursor object using cursor() method
          cursor = db.cursor()
          query = "SELECT COUNT(DISTINCT e.eventid) as EVENT_COUNT, e.eventid as Event_ID, hst.name as HostGroup_Name, upper(SUBSTRING_INDEX(h.host,'.',1)) as HostName, \
          h.name, FROM_UNIXTIME(e.clock,'%d-%m-%y') as time, t.priority, e.ns as Duration_ns, sum(e.ns)*1.66*POWER(10,-11) as duration_minutes, e.value, t.description, t.status, hstgr.groupid \
          FROM events e, hosts h, triggers t, functions f, items i, hosts_groups hstgr, hstgrp hst \
          WHERE h.hostid = i.hostid \
          AND i.itemid = f.itemid \
          AND h.hostid = hstgr.hostid \
          AND t.triggerid = f.triggerid \
          AND t.triggerid = e.objectid \
          AND hstgr.groupid = hst.groupid \
          AND t.priority > 3 \
          AND e.clock BETWEEN UNIX_TIMESTAMP(NOW()-INTERVAL 1 DAY) and UNIX_TIMESTAMP() \
          GROUP BY h.host, t.triggerid, t.description, t.expression, t.priority, h.name, hstgr.groupid, hst.name, time \
          ORDER BY Event_ID desc, h.host, t.description, t.triggerid;"

    # execute SQL query using execute() method.
          cursor.execute("SELECT VERSION()")

    # Fetch a single row using fetchone() method.
          data = cursor.fetchall()
          print("Database version : %s " % data)

         # Executing the actual query
          results = pandas.read_sql_query(query,db)
         # Saving the data to output.csv
          results.to_csv("output.csv", index=False)
except pymysql.InternalError as error:
     code, message = error.args
     print ("Error while connecting to MySQL ", code)

finally:
    if db.open:
         cursor.close()
         db.close()
         import pysftp

         myHostname = "yourserverdomainorip.com"
         myUsername = "root"
         myPassword = "12345"

         with pysftp.Connection(host=myHostname, username=myUsername, password=myPassword) as sftp:
             print "Connection succesfully stablished ... "

             # Define the file that you want to upload from your local directorty
             # or absolute "C:\Users\sdkca\Desktop\TUTORIAL2.txt"
             localFilePath = './TUTORIAL2.txt'

             # Define the remote path where the file will be uploaded
             remoteFilePath = '/var/integraweb-db-backups/TUTORIAL2.txt'

             sftp.put(localFilePath, remoteFilePath)

         # connection closed automatically at the end of the with-block
