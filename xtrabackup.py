#!/usr/bin/env python

import os,datetime,shutil,pipes,time,subprocess,sys

days = datetime.date.today()
#filename = sys.argv[1]
filename = str(raw_input("please enter your choice: "))
DB_HOST = 'centosvm01' #ie. localhost
DB_USER = 'bkpuser'
DB_USER_PASSWORD = 'bkpuser'
db = 'zabbix'
cleanup = 2
DATA_DIRECTORY = '/var/lib/mysql'
BACKUP_PATH = '/var/lib/backups'
cleanup = 2
email = 'sriharsha.vallabaneni@gmail.com'
backuplog = '/usr/local/bin/xtrabackup.log'
days = datetime.date.today()



class Xtrabackup():

     def fullbackup(self, days):
          date = days
          TODAYBACKUPPATH = BACKUP_PATH + "/" + str(date) + "/full/"
          ### Creating the backup path 
          if os.path.isdir(TODAYBACKUPPATH) == True:
               print "Backup path is exsisting please remove the directory : " +"\"" + TODAYBACKUPPATH + "\""
               exit()
          else:
               print "creating backup"
               os.makedirs(TODAYBACKUPPATH)
               ### Actual backup with compress
               dumpcmd = "xtrabackup --backup" + " --compress " + "--user " + DB_USER + " --password " + DB_USER_PASSWORD + " --target-dir=" + TODAYBACKUPPATH + " --datadir=" + DATA_DIRECTORY
               retcode = os.system(dumpcmd)
               print (retcode)
               if ( retcode == 0 ):
                    ## backupstatus.txt file will act as a reference for todays
                    os.chdir(BACKUP_PATH)
                    f = open("backupstatus.txt", "w+")
                    f.write(TODAYBACKUPPATH)
                    f.close()
                    ### Creating inc.txt which will act as reference for next incremental backup
                    b = 0
                    with open("inc.txt",'w') as f:
                         f.write(str(b))              
                    print "Executing clean up"        ### Need to remove 
                    xf.cleanup(cleanup)
                    mailcmd = "mailx -s" +  "\"FULL Backup is Success\"" + email + "<" + backuplog
                    os.system(mailcmd)
               else:
                    mailcmd = "mailx -s" +  "\"FULL Backup is Failure\"" + email + "<" + backuplog
                    os.system(mailcmd)

     def Incremental(self):
          # date = days
          # daysago = datetime.datetime.now() - datetime.timedelta(days=wday)
          # base_path = daysago.date()
          # print daysago.date()
          os.chdir(BACKUP_PATH)
          if os.path.exists('backupstatus.txt') == True:
               f = open("backupstatus.txt","r")
               BASE_DIR = f.read()
               print BASE_DIR   #### Need to remove
               BASE_BACKUP = '/'.join(BASE_DIR.split('/')[:-2])
               print BASE_BACKUP    ### Need to remove
               
               with open("inc.txt",'r') as f:   #open a file in the same folder
                   a = f.readlines()            #read from file to variable a
               b = int(a[0])                    #get integer at first position
               if b == 0:                        # if b = 0 indicate that this is INC0 which should use base dir as full backup
                    TODAYBACKUPPATH = BASE_BACKUP + "/inc" + str(b) + "/"
                    print TODAYBACKUPPATH   ### Need to remove
                    os.makedirs(TODAYBACKUPPATH)
                    dumpcmd = "xtrabackup --backup" + " --compress " + "--user " + DB_USER + " --password " + DB_USER_PASSWORD + " --target-dir=" + TODAYBACKUPPATH + " --incremental-basedir=" + BASE_DIR
                    retcode = os.system(dumpcmd)       ## dumpcmd will perform the actual INC0 backup  
                    if ( retcode == 0 ):
                         os.chdir(BACKUP_PATH)
                         b = b+1                          #increment the value and save it to inc.txt
                         with open("inc.txt",'w') as f:
                              f.write(str(b))              #writing a assuming it has been changed
                         mailcmd = "mailx -s" +  "\"Incremental Backup is Success\"" + email + "<" + backuplog
                         os.system(mailcmd)
                    else:
                         mailcmd = "mailx -s" +  "\"Incremental Backup is Failure\"" + email + "<" + backuplog
                         os.system(mailcmd)
               else:
                    BASE_DIR = BASE_BACKUP + "/inc" + str(b-1) + "/"
                    TODAYBACKUPPATH = BASE_BACKUP + "/inc" + str(b) + "/"
                    print TODAYBACKUPPATH  ### Need to remove
                    os.makedirs(TODAYBACKUPPATH) 
                    #### Will perform Incremental backups assuming previous inc backup as base_dir
                    dumpcmd = "xtrabackup --backup" + " --compress " + "--user " + DB_USER + " --password " + DB_USER_PASSWORD + " --target-dir=" + TODAYBACKUPPATH + " --incremental-basedir=" + BASE_DIR
                    retcode = os.system(dumpcmd)
                    if ( retcode == 0 ):
                         os.chdir(BACKUP_PATH)
                         b = b+1                          #increment
                         with open("inc.txt",'w') as f:
                              f.write(str(b))              #writing a assuming it has been changed
                         mailcmd = "mailx -s" +  "\"Incremental Backup is Success\"" + email + "<" + backuplog
                         os.system(mailcmd)
                    else:
                         mailcmd = "mailx -s" +  "\"Incremental Backup is Failure\"" + email + "<" + backuplog
                         os.system(mailcmd)

     def cleanup(self, cleanup):
          cleanup = cleanup
          print cleanup
          now = time.time()
          os.chdir(BACKUP_PATH)
          print BACKUP_PATH     ### Need to comment
          try:
               for folder,directory, files in os.walk(BACKUP_PATH):
                    for i in directory:
                         print i + " is directory"
                         if (os.path.isdir(i)):
                              if (os.path.getmtime(i)) < now - cleanup * 86400:
                                   print time.ctime(os.path.getmtime(i)),
                                   #print(time.ctime(os.path.getmtime(i)))
                                   print i ### Need to comment
                              else:
                                   print "No old files to delete"
                              #shutil.rmtree(i)
                    for j in files:
                         if (os.path.isfile(j)):
                              if (os.path.getmtime(j)) < now - cleanup * 86400:
                                   print time.ctime(os.path.getmtime(j)), 
                                   #print(time.ctime(os.path.getmtime(j)))
                                   print j
                                   #os.remove(j)
          except OSError as e:
               print ("Error: %s - %s." % (e.filename, e.strerror))

     def restore(self,restdays,inc):      #### Performing the restore of the database.
          d = restdays
          print d
          inc = inc
          ## decompressing Full backup
          target = d + "/full"
          print target
          ### Format for decompressing
          ### xtrabackup --decompress --target-dir=/data/compressed/
          dumpcmd = "xtrabackup --decompress" + "--target-dir=" + target
          # os.chdir(target)
          # dumpcmd = "ls -l"
          # print dumpcmd
          retcode = os.system(dumpcmd)
          if ( retcode == 0 ):
               if inc != 0:
                    for i in range(int(inc)+1):
                         target = d + "/inc" + str(i)
                         dumpcmd = "xtrabackup --decompress" + "--target-dir" + target
                         #dumpcmd = "ls -l"    ##Need to remove
                         retcode = os.system(dumpcmd)
                         print "Restore inc" + str(i)   ## Need to remove
                         if ( retcode != 0 ):
                              mailcmd = "mailx -s" +  "\"Incremental Backup is Failure\"" + email + "<" + backuplog
                              os.system(mailcmd)
                              print "Send failure decompress error for inc/" + str(i)      ### Need to remove
                              exit()
                    print "This many num of decompress is success: " + str(i)    ### Need to remove

                    ### Preparing & restoring the Full and Incremental backup by calling prepare(restday,inc) 
                    xf = Xtrabackup()
                    xf.prepare(restdays,inc)
               else:
                    ##### Preparing and restoring the full backup
                    print "No incremental backup"    ### Need to remove
                    xf = Xtrabackup()
                    xf.fullprepare(restdays)


     def prepare(self,restdays,inc):
          print "I am incremental restore"
          full = restdays
          inc = inc
          target = full + "/full"
          ### Format for preparing
          ### xtrabackup --prepare --target-dir=/data/compressed/
          print target
          dumpcmd = "xtrabackup --prepare --apply-log-only --target-dir=" + target
          retcode = os.system(dumpcmd)
          if ( retcode != 0 ):
               mailcmd = "mailx -s" +  "\"Failure of preparing full backup\"" + email + "<" + backuplog
               os.system(mailcmd)
               print "Failure of preparing full backup"   ### Need to send email
          else:
               for i in range(int(inc)+1):
                    print i             ## Need to remove
                    if ( i == int(inc)):
                         #xtrabackup --prepare --target-dir=full --incremental-dir=/data/backups/inc2
                         dumpcmd = "xtrabackup --prepare --target-dir=" + target + "--incremental-dir=" + full + "/inc" +str(i)
                         print "prepare final inc" + str(i)
                         print dumpcmd
                         retcode = os.system(dumpcmd)
                         if retcode != 0:
                              mailcmd = "mailx -s" +  "\"Failure of preparing final Incremental backup\"" + email + "<" + backuplog
                              os.system(mailcmd)
                              print "Failure of preparing full backup"   ### Need to send email

                    else:
                         #xtrabackup --prepare --apply-log-only --target-dir=full --incremental-dir=/data/backups/inc1
                         dumpcmd = "xtrabackup --prepare --apply-log-only --target-dir=" + target + "--incremental-dir=" + full + "/inc" +str(i)
                         print dumpcmd
                         print "prepare inc" + str(i)
                         retcode = os.system(dumpcmd)
                         if retcode != 0:
                              mailcmd = "mailx -s" +  "\"Failure of preparing Incremental backup\"" + email + "<" + backuplog
                              os.system(mailcmd)
                           
               count = len(os.listdir(BACKUP_PATH))
               print count
               if count == 0:
                    ## Restoring the backup to MYSQL data directory
                    dumpcmd = "xtrabackup --copy-back --target-dir=" + DATA_DIRECTORY
                    restcode = os.system(dumpcmd)
                    if restcode == 0:
                         dumpcmd = "chown -R mysql:mysql " + DATA_DIRECTORY     
               else:
                    mailcmd = "mailx -s" +  "\"Please do clean up mysql data directory\"" + email + "<" + backuplog
                    os.system(mailcmd)
                    print "Please do clean up mysql data directory path:"
                    

     def fullprepare(self,restdays):
          print " I am full restore"   ## Need to remove
          d = restdays
          print d             ## Need to remove
          target = d + "/full"
          print target    ## Need to remove
          ### Format for preparing
          ### xtrabackup --prepare --target-dir=/data/compressed/
          dumpcmd = "xtrabackup --prepare --target-dir=" + target
          os.chdir(target)
          print dumpcmd
          retcode = os.system(dumpcmd)
          if ( retcode != 0 ):
               print "Failure of preparing full backup"
          else:
               count = len(os.listdir(BACKUP_PATH))
               print count
               if count != 0:
                    mailcmd = "mailx -s" +  "\"Please do clean up mysql data directory\"" + email + "<" + backuplog
                    os.system(mailcmd)
                    print "Please do clean up mysql data directory path:"
               else:
                    dumpcmd = "xtrabackup --copy-back --target-dir=" + DATA_DIRECTORY
                    restcode = os.system(dumpcmd)
                    if restcode == 0:
                         #### Changing permission of the MYSQL base directory
                         dumpcmd = "chown -R mysql:mysql " + DATA_DIRECTORY
                         retcode = os.system(dumpcmd)
                         if retcode != 0:
                              mailcmd = "mailx -s" +  "\"Unable to change permission of the mysql data directory\"" + email + "<" + backuplog
                              os.system(mailcmd)
                              print "Unable to change permission of the mysql data directory:"
                         





if filename == 'full':
     xf = Xtrabackup()
     xf.fullbackup(days)
elif filename == 'Inc':
     xf = Xtrabackup()
     xf.Incremental()
elif filename == 'cleanup':
     xf = Xtrabackup()
     xf.cleanup(cleanup)
elif filename == 'restore':
     restdays = raw_input("please provide backup location: ")
     #restdays = datetime.datetime.strptime(userIn, "%d/%m/%y")
     inc = input("please provide the incremental backup's: ")
     #print restdays.date()
     xf = Xtrabackup()
     xf.restore(restdays,inc)
elif filename == "-h":
     print "Usage of xtrabackup"
     print "mysqlbackup <full> for full backup"
     print "mysqlbackup <Inc> for Incremental backup, Make sure to have full backup before triggering for incremental backup"
     print "mysqlbackup <restore> for preparing the backup for the restore. Please have the date"
