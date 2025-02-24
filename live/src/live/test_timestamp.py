import pytz
import datetime

def time_stamp(message):
    timestamp = message['exchange_timestamp'] / 1000  # Convert ms to sec
    utc_time = datetime.datetime.utcfromtimestamp(timestamp)
    timezone = pytz.timezone('Asia/Kolkata')  # UTC+5:30
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

# Test input
test_message = {'exchange_timestamp': 1700000000000}  # Example timestamp
print(time_stamp(test_message))
