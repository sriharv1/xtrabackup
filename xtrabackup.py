#!/usr/bin/env python

####  Following Xtrabackup script is used to perform 
####  fullbackup's , Incremental backup's ,Table level backup, Cleanup & Restore of backup's
####   Usage of Xtrabackup can be found below
#### print "xtrabackup.py <full> for full backup"
#### print "xtrabackup.py <Inc> for Incremental backup, Make sure to have full backup before triggering for incremental backup"
#### print "xtrabackup.py <fullrestore> for preparing the backup for the restore. Please have the date"
####  print "xtrabackup.py <datacopy> for copying data which was prepared by using fullrestore and got failed copy back to data directory"
#### print "xtrabackup.py <tablebackup> for backing up the tables"
#### print "xtrabackup.py <tableprepare> for preparing the tables for restore"
#### print "xtrabackup.py -h" for help

### Modules used for automating
import os,datetime,shutil,time,subprocess,sys

####### Variables that need to be filled before running the script first time
if len(sys.argv) == 1:
     print "Please provide arguments to the backup else type \'xtrabackup.py -h\' on how to use script "
     exit()
else:
     TYPEOF_BKP = sys.argv[1]
#TYPEOF_BKP = str(raw_input("please enter your choice: "))
DB_USER = 'bkpuser'
DB_USER_PASSWORD = 'bkpuser'
DB_DATABASES = 'zabbix'
BKP_CLEANUP = 200
DATA_DIRECTORY = '/var/lib/mysql'
BACKUP_PATH = '/var/lib/backups'
EMAIL = 'sriharsha.vallabaneni@cerner.com'
backuplog = '/usr/local/bin/xtrabackup.log'
days = datetime.date.today()

class Xtrabackup():

     def fullbackup(self, days):
          date = days
          TODAYBACKUPPATH = BACKUP_PATH + "/" + str(date) + "/full/"
          ### Creating the backup path 
          if os.path.isdir(TODAYBACKUPPATH) == True:
               print "Backup path is exsisting please remove the directory : " +"\"" + TODAYBACKUPPATH + "\""
               mailcmd = "mailx -s " +  " \"Back up path is existing please remove the path\" " + EMAIL + " < " + backuplog
               os.system(mailcmd)
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
                    xf.cleanup(BKP_CLEANUP)
                    mailcmd = "mailx -s " +  " \"FULL Backup is Success\" " + EMAIL + " < " + backuplog
                    os.system(mailcmd)
               else:
                    mailcmd = "mailx -s " +  " \"FULL Backup is Failure\" " + EMAIL + " < " + backuplog
                    os.system(mailcmd)
                    exit()

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
                         mailcmd = "mailx -s " +  "\"Incremental Backup is Success\"" + EMAIL + "<" + backuplog
                         os.system(mailcmd)
                    else:
                         mailcmd = "mailx -s " +  "\"Incremental Backup is Failure\"" + EMAIL + "<" + backuplog
                         os.system(mailcmd)
                         exit()
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
                         mailcmd = "mailx -s " +  "\"Incremental Backup is Success\"" + EMAIL + "<" + backuplog
                         os.system(mailcmd)
                    else:
                         mailcmd = "mailx -s " +  "\"Incremental Backup is Failure\"" + EMAIL + "<" + backuplog
                         os.system(mailcmd)
                         exit()

     def cleanup(self, BKP_CLEANUP):
          BKP_CLEANUP = BKP_CLEANUP
          print BKP_CLEANUP
          now = time.time()
          os.chdir(BACKUP_PATH)
          print BACKUP_PATH     ### Need to comment
          try:
               for folder,directory, files in os.walk(BACKUP_PATH):
                    for i in directory:
                         print i + " is directory"
                         if (os.path.isdir(i)):
                              if (os.path.getmtime(i)) < now - BKP_CLEANUP * 86400:
                                   print time.ctime(os.path.getmtime(i)),
                                   #print(time.ctime(os.path.getmtime(i)))
                                   print i ### Need to comment
                                   shutil.rmtree(i)
                              else:
                                   print "No old files to delete"
                              
                    for j in files:
                         if (os.path.isfile(j)):
                              if (os.path.getmtime(j)) < now - BKP_CLEANUP * 86400:
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
          dumpcmd = "xtrabackup --decompress" + " --target-dir=" + target
          retcode = os.system(dumpcmd)
          print "full restore is complete"
          if ( retcode == 0 ):
               print "successfull full decompress"
               if inc != 0:
                    print "successfull finding INC"
                    print inc
                    for i in range(int(inc)):
                         print i
                         target = d + "/inc" + str(int(i))
                         print target
                         dumpcmd = "xtrabackup --decompress --target-dir=" + target
                         print dumpcmd
                         #dumpcmd = "ls -l"    ##Need to remove
                         retcode = os.system(dumpcmd)
                         print "Restore inc" + str(i)   ## Need to remove
                         if ( retcode != 0 ):
                              mailcmd = "mailx -s " +  "\"Incremental Backup is Failure\"" + EMAIL + "<" + backuplog
                              os.system(mailcmd)
                              exit()
                    print "This many num of decompress is success: " + str(i)    ### Need to remove
                    ### Preparing & restoring the Full and Incremental backup by calling prepare(restday,inc) 
                    xf = Xtrabackup()
                    xf.prepare(restdays,inc)
               else:
                    ##### Preparing and restoring the full backup
                    xf = Xtrabackup()
                    xf.fullprepare(restdays)


     def prepare(self,restdays,inc):
          print "I am incremental restore"
          full = restdays
          inc = inc
          target = full + "/full"
          ### Format for preparing
          ### xtrabackup --prepare --target-dir=/data/compressed/
          dumpcmd = "xtrabackup --prepare --apply-log-only --target-dir=" + target
          retcode = os.system(dumpcmd)
          if ( retcode != 0 ):
               mailcmd = "mailx -s " +  "\"Failure of preparing full backup\"" + EMAIL + "<" + backuplog
               os.system(mailcmd)
               print "Failure of preparing full backup"   ### Need to send EMAIL
               exit()
          else:
               for i in range(int(inc)):
                    print i             ## Need to remove
                    if ( i == int(inc)-1):
                         #xtrabackup --prepare --target-dir=full --incremental-dir=/data/backups/inc2
                         dumpcmd = "xtrabackup --prepare --target-dir=" + target + " --incremental-dir=" + full + "/inc" +str(i)
                         print "prepare final inc" + str(i)
                         retcode = os.system(dumpcmd)
                         if retcode != 0:
                              mailcmd = "mailx -s " +  "\"Failure of preparing final Incremental backup\"" + EMAIL + "<" + backuplog
                              os.system(mailcmd)
                              print "Failure of preparing full backup"   ### Need to send EMAIL
                              exit()
                    else:
                         #xtrabackup --prepare --apply-log-only --target-dir=full --incremental-dir=/data/backups/inc1
                         dumpcmd = "xtrabackup --prepare --apply-log-only --target-dir=" + target + " --incremental-dir=" + full + "/inc" +str(i)
                         print "prepare inc" + str(i)
                         retcode = os.system(dumpcmd)
                         if retcode != 0:
                              mailcmd = "mailx -s " +  "\"Failure of preparing Incremental backup\"" + EMAIL + "<" + backuplog
                              os.system(mailcmd)
                              exit()
                         else:
                              xf = Xtrabackup()
                              xf.datacopy(restdays)                             

                    

     def fullprepare(self,restdays):
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
               xf = Xtrabackup()
               xf.datacopy(restdays)

     def datacopy(self,restdays):
          d = restdays
          target = d + "/full"               
          count = len(os.listdir(DATA_DIRECTORY))
          print count
          print DATA_DIRECTORY
          if count == 0:
               ## Restoring the backup to MYSQL data directory
               dumpcmd = "xtrabackup --copy-back --target-dir=" + target
               restcode = os.system(dumpcmd)
               if restcode == 0:
                    dumpcmd = "chown -R mysql:mysql " + DATA_DIRECTORY
                    retcode = os.system(dumpcmd)
                    if retcode == 0:
                         print "datacopy is success"

          else:
               mailcmd = "mailx -s " +  "\"Please do clean up mysql data directory\"" + EMAIL + "<" + backuplog
               os.system(mailcmd)
               print "Please do clean up mysql data directory path:"
                         
     def tablebackup(self,database,table,bckloc):
               table = table
               database = database 
               #tlist = tlist
               bckloc = bckloc
               print table
               print database        
               if os.path.isdir(bckloc) != True:
                    os.makedirs(bckloc)
                    os.chdir(bckloc)
                    print "Executed when backup path not exist"
                    f = open("table_bkp.txt","a+")
                    for i in range(len(table)):
                         f.write(table[i] +"\n")
                         print table[i]
                    f.close()
                    table_file = bckloc + "/" + "table_bkp.txt"
                    dumpcmd = "xtrabackup --backup --user=" + DB_USER + " --password=" + DB_USER_PASSWORD + " --target-dir=" + bckloc + " --tables-file=" + table_file
                    #dumpcmd = "pwd"
                    print "Executed when backup path not exist"
                    retcode = os.system(dumpcmd)
                    if retcode == 0:
                         mailcmd = "mailx -s " +  "\"Table Backup is Success\"" + EMAIL + "<" + backuplog
                         os.system(mailcmd)
                    else:
                         mailcmd = "mailx -s " +  "\"Table Backup Failed please verify the logs\"" + EMAIL + "<" + backuplog
                         os.system(mailcmd)
               else:
                    if len(os.listdir(bckloc)) == 0:
                         print "Executed when backup path exists"
                         os.chdir(bckloc)
                         f = open("table_bkp.txt","a+")
                         for i in range(len(table)):
                              f.write(table[i] +"\n")
                              print table[i]
                         f.close()
                         table_file = bckloc + "/" + "table_bkp.txt"
                         dumpcmd = "xtrabackup --backup --user=" + DB_USER + " --password=" + DB_USER_PASSWORD + " --target-dir=" + bckloc + " --tables-file=" + table_file
                         #dumpcmd = "pwd"
                         print "Executed when backup path exists"
                         retcode = os.system(dumpcmd)
                         if retcode == 0:
                              mailcmd = "mailx -s " +  "\"Table Backup is Success\"" + EMAIL + "<" + backuplog
                              os.system(mailcmd)
                         else:
                              mailcmd = "mailx -s " +  "\"Table Backup Failed please verify the logs\"" + EMAIL + "<" + backuplog
                              os.system(mailcmd)
                    else:
                         print "Files already existing please delete files/directories under " + bckloc


     def tableprepare(self,bckloc):

          bckloc = bckloc 
          #xtrabackup --prepare --export --target-dir=/path/to/partial/backup
          dumpcmd = "xtrabackup --prepare --export --target-dir=" + bckloc
          retcode = os.system(dumpcmd)
          if retcode == 0:
               mailcmd = "mailx -s " +  "\"Tableprepare restore is success\"" + EMAIL + "<" + backuplog
               os.system(mailcmd)
          else:    
               mailcmd = "mailx -s " +  "\"Tableprepare restore is Failure\"" + EMAIL + "<" + backuplog
               os.system(mailcmd)
               exit()


     def dataBase(self,databases):
          print "I am database backup"
          databases = databases
          days = datetime.date.today()
          print databases
          print days
          BKPLOC = BACKUP_PATH + "/" + str(days) + "/" + databases[0]
          if os.path.isdir(BKPLOC) != True:
               os.makedirs(BKPLOC)
               os.chdir(BKPLOC)
               f = open("table_bkp.txt","a+")
               for i in range(len(databases)):
                    f.write(databases[i] +"\n")
               f.close()
               table_file = BKPLOC + "/" + "table_bkp.txt"
               # dumpcmd = "xtrabackup --databases=\'" + databases[i] + "\' --user=" + DB_USER + " --password=" + DB_USER_PASSWORD + " --target-dir=" + BKPLOC
               dumpcmd = "xtrabackup --backup --user=" + DB_USER + " --password=" + DB_USER_PASSWORD + " --target-dir=" + BKPLOC + " --databases-file=" + table_file
               retcode = os.system(dumpcmd)
               if retcode != 0:
                    print "backup got failed"
                    mailcmd = "mailx -s " +  "\"database backup got failed\"" + EMAIL + " < " + backuplog
                    os.system(mailcmd)
                    print dumpcmd
                    
          else:
               mailcmd = "mailx -s " +  "\"Backup path existing\"" + EMAIL + " < " + backuplog
               os.system(mailcmd)
               print mailcmd
               exit()

     def databaseRestore(self,bkploc):
          bkploc = bkploc 
          print bkploc


if TYPEOF_BKP == 'full':
     xf = Xtrabackup()
     xf.fullbackup(days)
elif TYPEOF_BKP == 'Inc':
     xf = Xtrabackup()
     xf.Incremental()
elif TYPEOF_BKP == 'cleanup':
     BKP_CLEANUP = int(input("No.of days before back up need to be deleted: "))
     xf = Xtrabackup()
     xf.cleanup(BKP_CLEANUP)

elif TYPEOF_BKP == 'fullrestore':
     userIn = raw_input("Is the back restore is going to perform on local node yes/no: ")
     if (userIn == 'yes' or userIn == 'y' or userIn == 'Y'):
          restdays = raw_input("please provide backup location <Eg: /var/lib/backups/(date)>: ")
          #restdays = datetime.datetime.strptime(userIn, "%d/%m/%y")
          inc = input("please provide the incremental backup's: ")
          #print restdays.date()
          xf = Xtrabackup()
          xf.restore(restdays,inc)
     elif (userIn == 'No' or userIn == 'n' or userIn == 'N'):
          print "Backup restore script and backup should be on local node, Please copy script and backup to local node"
          exit()

elif TYPEOF_BKP == 'datacopy':
     restdays = raw_input("please provide full backup location <Eg: /var/lib/backups/(date)>: ")
     xf = Xtrabackup()
     xf.datacopy(restdays)
          
elif TYPEOF_BKP == 'database' or TYPEOF_BKP == 'databases':
     userIn = int(raw_input("please provide the no of databases: "))
     databases = []
     for i in range(userIn):
          list = str(raw_input("Provide the database name that need to backup: "))
          d = DATA_DIRECTORY + "/" + list
          if os.path.isdir(d) == True:
               databases.append(list)
          else:
               print "Database is not located, Please provide existing database: "
               exit()
     xf = Xtrabackup()
     xf.dataBase(databases)
     
elif TYPEOF_BKP == 'databaserestore':
     bkploc = str(input("Please provide database backup location: "))
     xf = Xtrabackup()
     xf.databaseRestore(bkploc)

elif TYPEOF_BKP == 'tablebackup':
     bckloc = str(raw_input("Please provide the backup location: "))
     database = raw_input("Please provide the database to which table belongs: ")
     totaltables = int(raw_input("Num of tables that need to be backup: "))
     table = []
     for a in range(totaltables):
          tlist = raw_input("Provide the tables that need to be backup: ")
          d = DATA_DIRECTORY + "/" + database + "/" + tlist + ".ibd"
          if os.path.isfile(d) == True:
               table.append(database + "." + str(tlist))
          else:
               print list + "Table doesnt exist"
               exit()
     xf = Xtrabackup()
     xf.tablebackup(database,table,bckloc)
elif TYPEOF_BKP == 'test':
     print "test"
     
elif TYPEOF_BKP == "-h":
     print "Usage of xtrabackup.py"
     print "xtrabackup.py <full> for full backup"
     print "xtrabackup.py <Inc> for Incremental backup, Make sure to have full backup before triggering for incremental backup"
     print "xtrabackup.py <fullrestore> for preparing the backup for the restore. Please have the date"
     print "xtrabackup.py <datacopy> for copying data which was prepared by using fullrestore and got failed copy back to data directory"
     print "xtrabackup.py <database> <database1> <database2> For database level backup's"
     print "xtrabackup.py <database> will prompt for databases that need to have backup's"
     print "xtrabackup.py <databaserestore> will prompt for preparing databases that need to perform restore"
     print "xtrabackup.py <tablebackup> for backing up the tables"
     print "xtrabackup.py <tableprepare> for preparing the tables for restore"

