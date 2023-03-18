# import pandas module 
import pandas as pd 
import pytz
import datetime
from datetime import datetime,timedelta
import datetime as dt


timezone = pytz.timezone("EST")
now = datetime.now(timezone) + dt.timedelta(days=1)
now = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)

if now.month < 10 and now.day >= 10:
    sow = str(now.year)+'.0'+str(now.month)+'.'+str(now.day)
elif now.day < 10 and now.month < 10:
    sow = str(now.year)+'.0'+str(now.month)+'.0'+str(now.day)
elif now.day < 10 and now.month >= 10:
    sow = str(now.year)+'.'+str(now.month)+'.0' +str(now.day)
else:
    sow = str(now.year)+'.'+str(now.month)+'.'+str(now.day)

# making dataframe 
csv=[r'C:\Users\19178\Desktop\Trading Scripts\New Try with New Knowledge\ffc_new_events.csv']
df = pd.read_csv(r'C:\Users\19178\Desktop\Trading Scripts\New Try with New Knowledge\ffc_new_events.csv')
df.columns=["Weekday","Start_Time",'Dime',"Symbol","Impact","Title","1","2","3"]

df[['Start_Time', 'Date','Time']] = df['Start_Time'].str.split(' ', 2, expand=True)    

df = df.drop(['Start_Time', 'Weekday', 'Dime', 'Title', "1","2","3"], axis=1)   
# output the dataframe

df = df.drop(df[df.Date != sow].index)
df = df.drop(df[df.Impact == ' low'].index)

#df.to_csv (r'C:\Users\19178\Desktop\Trading Scripts\New Try with New Knowledge\fc_new_events.csv', index = False, header=True)

print(df)

