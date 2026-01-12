from datetime import datetime

def str_to_timestamp(date: str):
  dt = datetime.strptime(date, '%a %b %d %H:%M:%S %z %Y')
  return dt.strftime('%Y%m%d%H%M')