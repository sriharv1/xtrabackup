import os,datetime,shutil,pipes,time

#docker run -it -v /Users/hv024036/Desktop/python:/scripts --name xtrabackup harsha_python:latest

DB_HOST = 'cernzbxapp101' #ie. localhost
DB_USER = 'bkpuser'
DB_USER_PASSWORD = 'bkpuser'
db = 'zabbix'
#DB_NAME = '/backup/dbnames.txt'
DATA_DIRECTORY = '/Users/hv024036/Desktop/python'
BACKUP_PATH = '/Users/hv024036/Desktop/python/percona'
cleanup = 2
#wday = datetime.date.today().weekday()
wday = 5
print wday
days = datetime.date.today()
print days

class Xtrabackup:

     def fullbackup(self, days):
          date = days
          TODAYBACKUPPATH = BACKUP_PATH + "/" + str(date)
          print TODAYBACKUPPATH
          try:
               # os.stat(TODAYBACKUPPATH)
               print os.stat(TODAYBACKUPPATH)
          except:
               os.mkdir(TODAYBACKUPPATH)
               print "Directory is created"

          dumpcmd = "xtrabackup --backup" + " --compress " + "--user " + DB_USER + " --password " + DB_USER_PASSWORD + " --target-dir=" + TODAYBACKUPPATH + " --datadir=" + DATA_DIRECTORY
          print dumpcmd
          #os.system(dumpcmd)
          xf.cleanup(cleanup)


     def Incremental(self, wday, days):
          date = days
          wday = wday
          # daysago = datetime.datetime.now() - datetime.timedelta(days=wday)
          # base_path = daysago.date()
          # print daysago.date()
          if (wday==0):
               daysago = datetime.datetime.now() - datetime.timedelta(days=1)
               inc_date = daysago.date()
               TODAYBACKUPPATH = BACKUP_PATH + "/" + str(inc_date) + "/inc" + str(wday)
               BASE_DIR = BACKUP_PATH + "/" + str(inc_date)
               dumpcmd = "xtrabackup --backup" + " --compress " + "--user " + DB_USER + " --password " + DB_USER_PASSWORD + " --target-dir=" + TODAYBACKUPPATH + " --incremental-basedir=" + BASE_DIR
               print BASE_DIR
               print dumpcmd
          else:
               daysago = datetime.datetime.now() - datetime.timedelta(days=wday + 1)
               inc_date = daysago.date()
               print inc_date
               TODAYBACKUPPATH = BACKUP_PATH + "/" + str(inc_date) + "/inc" + str(wday)
               BASE_DIR = BACKUP_PATH + "/" + str(inc_date) + "/inc" + str(wday-1)
               dumpcmd = "xtrabackup --backup" + " --compress " + "--user " + DB_USER + " --password " + DB_USER_PASSWORD + " --target-dir=" + TODAYBACKUPPATH + " --incremental-basedir=" + BASE_DIR
               print dumpcmd
               print TODAYBACKUPPATH
               print BASE_DIR

     def cleanup(self, cleanup):
          cleanup = cleanup
          print cleanup
          now = time.time()
          os.chdir(BACKUP_PATH)
          try:
               for folder, directory, files in os.walk(BACKUP_PATH):
                    for i in directory:
                         print i + " is directory"
                         if (os.path.isdir(i)):
                              if (os.path.getmtime(i)) < now - cleanup * 86400:
                                   #print(time.ctime(os.path.getmtime(i)), end= ' ')
                                   print(time.ctime(os.path.getmtime(i)))
                                   print(i)
                              else:
                                   print "No old files to delete"
                              #shutil.rmtree(i)
                    for j in files:
                         if (os.path.isfile(j)):
                              if (os.path.getmtime(j)) < now - cleanup * 86400:
                                   #print(time.ctime(os.path.getmtime(j)), end = ' ')
                                   print(time.ctime(os.path.getmtime(j)))
                                   print(j)
                                   #os.remove(j)
          except OSError as e:
               print ("Error: %s - %s." % (e.filename, e.strerror))



if (wday == 5):
     xf = Xtrabackup()
     xf.fullbackup(days)
else:
     xf = Xtrabackup()
     xf.Incremental(wday, days)





# xtrabackup --backup --user=bkpuser --password=bkpuser --target-dir=/var/lib/backups/percona --datadir=/var/lib/mysql/









# class xtrabackup:
#
#      def __init__(self,full,inc):
#           self.full = full
#           self.inc = inc
#
#      def __init__
