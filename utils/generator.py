from datetime import datetime, timedelta
from uuid import uuid4


def get_current_time():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def add_date(start_date, duration):
    return (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=duration)).strftime('%Y-%m-%d')

def generate_id(prefix):    
    return prefix + "_" + uuid4().hex