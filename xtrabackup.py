import os,datetime,shutil,pipes

#docker run -it -v /Users/hv024036/Desktop/python:/scripts --name xtrabackup harsha_python:latest

DB_HOST = 'cernzbxapp101' #ie. localhost
DB_USER = 'bkpuser'
DB_USER_PASSWORD = 'bkpuser'
db = 'zabbix'
#DB_NAME = '/backup/dbnames.txt'
DATA_DIRECTORY = '/var/lib/mysql/'
BACKUP_PATH = '/var/lib/backups/percona/'

day = datetime.date.today().weekday()
print day
tday = day + 6  # (Checking whether logic is picking or not)
print tday
days = datetime.date.today()
print days

class Xtrabackup:

     def fullbackup(self, days):
          date = days
          TODAYBACKUPPATH = BACKUP_PATH + str(date)
          print TODAYBACKUPPATH
          try:
               # os.stat(TODAYBACKUPPATH)
               print os.stat(TODAYBACKUPPATH)
          except:
               os.mkdir(TODAYBACKUPPATH)
               print "Directory is created"

          dumpcmd = "xtrabackup --backup" + " --compress " + "--user " + DB_USER + " --password " + DB_USER_PASSWORD + " --target-dir " + TODAYBACKUPPATH + " --datadir " + DATA_DIRECTORY
          print (dumpcmd)
          #os.system(dumpcmd)
          # compcmd = "tar -zcvf " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".tar.gz " +  pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
          # #os.system(compcmd)
          # echo "compcmd"
          compcmd = "tar -zcvf " + pipes.quote(TODAYBACKUPPATH) + "/" + "zabbix"  + ".tar.gz " +  pipes.quote(TODAYBACKUPPATH)
          print (compcmd)

     def Incremental(self, day, days):
          date = days
          day = day
          daysago = datetime.datetime.now() - datetime.timedelta(days=day)
          print daysago.date()
          TODAYBACKUPPATH = BACKUP_PATH + str(date)
          print TODAYBACKUPPATH + " INCREMENTAL " + str(day)





if (day == 7):
     xf = Xtrabackup()
     xf.fullbackup(days)
else:
     xf = Xtrabackup()
     xf.Incremental(day, days)

# xtrabackup --backup --user=bkpuser --password=bkpuser --target-dir=/var/lib/backups/percona --datadir=/var/lib/mysql/









# class xtrabackup:
#
#      def __init__(self,full,inc):
#           self.full = full
#           self.inc = inc
#
#      def __init__
