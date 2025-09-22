import datetime

date = datetime.date(2025, 1, 2)

today = datetime.date.today()
#print(date)

time = datetime.time(12,30,0)

now = datetime.datetime.now()

now = now.strftime("%H:%M:%S")
#print(time)
#print(now)

target_date = datetime.datetime(2019,1,2,12,30,1)
current_date = datetime.datetime.now()

if current_date > target_date:
    print("The target date has passed")
else:
    print("Target date has not passed")