import time
import datetime

import os.path, time
import subprocess, signal

__version__='2.0.0'

#5 minutes = 300 seconds
#25 hours = 90,000 seconds

#list of dictionaries containing data on files to watch
#if 'name_to_kill' is set then the process with the given name will be stopped
flock=[{'filename': 'loop_test_start.txt', 'interval':60, 'service_to_restart':'python_loop.service'},
       #{'filename': 'heartbeat_day.txt', 'interval':90000, 'name_to_kill':'python_loop.py'},
       ]

#grace period where for the first n seconds the script will not restart even if the file is old. Applies to all files
grace_period=10

#log file for the watchdog program
log_filename="watchdog_log.txt"


start_time=datetime.datetime.now()

#function to perform check of file age
def watchdog_check(file_to_watch, watchdog_threshold=300):

    running=1 #start with the assumption the code is running

    #get the time that the system has been up
    up_time=abs(datetime.datetime.now()-start_time)

    #initialise as empty
    last_modified_time=""

    #loop through and  try 10 times
    try_num=1
    num_tries=10

    while try_num < num_tries and last_modified_time=="":
        #try to get the time that the file was modified (we ignore the contents)
        try:
            last_modified_time=time.ctime(os.path.getmtime(file_to_watch))
            running=1
        except:
            log_msg("Error reading file")
            try_num=try_num+1
            running=0

    #import pdb; pdb.set_trace()
    #check if we are still in the grace period, if we are then do nothing, otherwise handle it.
    if up_time.seconds>grace_period:
        
        #if it wasn't possible to get the file modified time then restart the system
        if last_modified_time=="":
            print('Error getting last modified time')

            running=0

        #otherwise if we could get the file modified time, see how old it was
        else:
            #convert the time from a string to a datetime object
            last_modified_as_datetime=datetime.datetime.strptime(last_modified_time, "%a %b %d %H:%M:%S %Y")

            #get the time now
            datetime_now=datetime.datetime.now()

            #calculate the time difference
            time_diff=datetime_now - last_modified_as_datetime

            #if we have exceeded the threshold then restart
            if time_diff.total_seconds()>watchdog_threshold:
                running=0
            else:
                running=1

            #print status to screen. Don't log this as log files would be too big.
            print (str(file_to_watch) + ":\t Timediff: " + str(time_diff) + '\t Uptime: ' +str(up_time) + ' seconds.')
    else:
            print('Waiting for grace period to expire. (' + str(up_time.seconds)+'/'+str(grace_period)+'s)')
            running=1 #we won't kill the process yet
                               
    return running

#function that loops through each file and checks them
def watchdog():

    for item in flock:
        
        if 1:
            running=1
            running=watchdog_check(item['filename'], item['interval'])

            if not running==1:
                #handle stopped process

                #if we should restart the service, then do so:
                if 'service_to_restart' in item:
                    restart_service_linux(item['service_to_restart'])

                #restart_sys()
                
        else:
            log_msg("Watchdog error when handling " + item['filename'] )
            print("Error!")

    return
    

#function that handles restarting
def restart_sys():
    print("Restarting")
    log_msg("Error, no heartbeat detected, rebooting!")
    #restart()

    return

#function to restart a linux machine
def restart():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output=process.communicate()[0]
    print(output)
    
    return    

def restart_service_linux(proc_name):
    log_msg('Restarting service ' + proc_name)
    #if we're on linux
    try:
        if os.name == 'posix':
            command='sudo systemctl restart ' +proc_name
            #import pdb; pdb.set_trace()
            p = os.system(command)
    except:
        log_msg('Error encountered when restarting service: ' + command)
        
    return

def kill_process_linux_simple(proc_name):
    log_msg('Restarting service ' + proc_name)
    #if we're on linux
    if os.name == 'posix':
        p = subprocess.Popen(['pkill', '-f', proc_name], stdout=subprocess.PIPE)
        
    return

def kill_process_linux(proc_name):
    #using code from here: https://stackoverflow.com/a/2940878/6034413
    

    if os.name == 'posix':
        p = subprocess.Popen(['ps', '-x'], stdout=subprocess.PIPE)
        out, err = p.communicate()

        for line in out.splitlines():
            line_str=line.decode("utf-8") 
            #import pdb; pdb.set_trace()
            if proc_name in line_str:
                pid = int(line_str.split(None, 1)[0])
                os.kill(pid, signal.SIGKILL)
                print('Killed ' + str(pid))

        print('Done')

    else:
        print('Not a linux machine.')

    return
        
#function to append to a text file
def append_to_file(data, filename):
    
    with open(filename, "a") as myfile:
        myfile.write(data)
    return

#function to write messages to log file with a timestamp
def log_msg(message):

    
    time_stamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line_to_write = (time_stamp + " - " + message + "\n")
    append_to_file(line_to_write, log_filename)

    return


def main():

    print("Main function.")

    log_msg("Watchdog started.")

    #main program loop
    while 1:
        watchdog()
        time.sleep(1)

    return
    

if __name__=="__main__":
    main()
