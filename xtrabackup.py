#!/usr/bin/env python

import os,datetime,shutil,pipes,time,subprocess,sys

filename = sys.argv[1]
days = datetime.date.today()
filename = sys.argv[1]
DB_HOST = 'centosvm01' #ie. localhost
DB_USER = 'bkpuser'
DB_USER_PASSWORD = 'bkpuser'
db = 'zabbix'
cleanup = 2
DATA_DIRECTORY = '/var/lib/mysql'
BACKUP_PATH = '/var/lib/backups'
cleanup = 2
toaddr = 'sriharsha.vallabaneni@gmail.com'
days = datetime.date.today()



class Xtrabackup():

     def fullbackup(self, days):
          date = days
          TODAYBACKUPPATH = BACKUP_PATH + "/" + str(date) + "/full/"
          print TODAYBACKUPPATH
          print os.path.isdir(TODAYBACKUPPATH)
          if os.path.isdir(TODAYBACKUPPATH) == True:
               print "Backup path is exsisting please remove the directory : " +"\"" + TODAYBACKUPPATH + "\""
               exit()
          else:
               print "creating backup"
               os.makedirs(TODAYBACKUPPATH)
               dumpcmd = "xtrabackup --backup" + " --compress " + "--user " + DB_USER + " --password " + DB_USER_PASSWORD + " --target-dir=" + TODAYBACKUPPATH + " --datadir=" + DATA_DIRECTORY
               # dumpcmd = "ls -l"
               retcode = os.system(dumpcmd)
               print retcode
               if ( retcode == 0 ):
                    ## To clean up the old backup's
                    os.chdir(BACKUP_PATH)
                    f = open("backupstatus.txt", "w+")
                    f.write(TODAYBACKUPPATH)
                    f.close()
                    b = 0
                    with open("inc.txt",'w') as f:
                         f.write(str(b))              #writing a assuming it has been changed
                    print "Executing clean up"
                    xf.cleanup(cleanup)
                    print "Send email once after cleanup"
               else:
                    print "send email that full backup is Failure"

     def Incremental(self, days):
          date = days
          # daysago = datetime.datetime.now() - datetime.timedelta(days=wday)
          # base_path = daysago.date()
          # print daysago.date()
          os.chdir(BACKUP_PATH)
          if os.path.exists('backupstatus.txt') == True:
               f = open("backupstatus.txt","r")
               BASE_DIR = f.read()
               print BASE_DIR
               BASE_BACKUP = '/'.join(BASE_DIR.split('/')[:-2])
               print BASE_BACKUP
               # x = BASE_DIR.split('/')[:-1]
               # y = x[-1]
               # print x
               with open("inc.txt",'r') as f: #open a file in the same folder
                   a = f.readlines()            #read from file to variable a
               #use the data read
               b = int(a[0])                    #get integer at first position
               if b == 0:
                    TODAYBACKUPPATH = BASE_BACKUP + "/inc" + str(b) + "/"
                    print TODAYBACKUPPATH
                    os.makedirs(TODAYBACKUPPATH)
                    dumpcmd = "xtrabackup --backup" + " --compress " + "--user " + DB_USER + " --password " + DB_USER_PASSWORD + " --target-dir=" + TODAYBACKUPPATH + " --incremental-basedir=" + BASE_DIR
                    print "I am INC0 backup"
                    retcode = os.system(dumpcmd)
                    if ( retcode == 0 ):
                         ## To clean up the old backup's
                         os.chdir(BACKUP_PATH)
                         b = b+1                          #increment
                         with open("inc.txt",'w') as f:
                              f.write(str(b))              #writing a assuming it has been changed
                    else:
                         print "send email that full backup is Failure"
               else:
                    BASE_DIR = BASE_BACKUP + "/inc" + str(b-1) + "/"
                    TODAYBACKUPPATH = BASE_BACKUP + "/inc" + str(b) + "/"
                    print TODAYBACKUPPATH
                    os.makedirs(TODAYBACKUPPATH)
                    dumpcmd = "xtrabackup --backup" + " --compress " + "--user " + DB_USER + " --password " + DB_USER_PASSWORD + " --target-dir=" + TODAYBACKUPPATH + " --incremental-basedir=" + BASE_DIR
                    print BASE_DIR
                    print "I am INC" +str(b-1) + " backup"
                    retcode = os.system(dumpcmd)
                    if ( retcode == 0 ):
                         ## To clean up the old backup's
                         os.chdir(BACKUP_PATH)
                         b = b+1                          #increment
                         with open("inc.txt",'w') as f:
                              f.write(str(b))              #writing a assuming it has been changed
                    else:
                         print "send email that full backup is Failure"

     def restore(self,restore):
          restday = restore
          print restday

     def cleanup(self, cleanup):
          cleanup = cleanup
          print cleanup
          now = time.time()
          os.chdir(BACKUP_PATH)
          print BACKUP_PATH     ### Need to comment
          try:
               for folder, directory, files in os.walk(BACKUP_PATH):
                    for i in directory:
                         print i + " is directory"
                         if (os.path.isdir(i)):
                              if (os.path.getmtime(i)) < now - cleanup * 86400:
                                   print(time.ctime(os.path.getmtime(i)), )
                                   #print(time.ctime(os.path.getmtime(i)))
                                   print(i) ### Need to comment
                              else:
                                   print "No old files to delete"
                              #shutil.rmtree(i)
                    for j in files:
                         if (os.path.isfile(j)):
                              if (os.path.getmtime(j)) < now - cleanup * 86400:
                                   print(time.ctime(os.path.getmtime(j)), )
                                   #print(time.ctime(os.path.getmtime(j)))
                                   print(j)
                                   #os.remove(j)
          except OSError as e:
               print ("Error: %s - %s." % (e.filename, e.strerror))




if filename == 'full':
     xf = Xtrabackup()
     xf.fullbackup(days)
elif filename == 'Inc':
     xf = Xtrabackup()
     xf.Incremental(days)
elif filename == 'cleanup':
     xf = Xtrabackup()
     xf.cleanup()
elif filename == 'restore':
     userIn = raw_input("Type Date dd/mm/yy: ")
     restdays = datetime.datetime.strptime(userIn, "%d/%m/%y")
     print restdays.date()
     xf = Xtrabackup()
     xf.restore(restdays)
elif filename == "-h":
     print "Usage of xtrabackup"
     print "mysqlbackup <full> for full backup"
     print "mysqlbackup <Inc> for Incremental backup, Make sure to have full backup before triggering for incremental backup"
     print "mysqlbackup <restore> for preparing the backup for the restore. Please have the date"
