import time
import datetime
with open('loop_test_start.txt', 'a') as f:
        f.write(datetime.datetime.now().isoformat())
		
while True:
    with open('loop_test_running.txt', 'a') as f:
        f.write(datetime.datetime.now().isoformat() + '\n')
    print(datetime.datetime.now().isoformat())
    time.sleep(1)
    
