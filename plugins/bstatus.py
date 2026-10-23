import datetime

JST = datetime.timezone(datetime.timedelta(hours=9))

def bstatus(bot):
    if not bot.is_ready():
        return ""
    ping = round(bot.latency * 1000)
    now = datetime.datetime.now(JST)
    current_hour = now.hour
    if 5 <= current_hour < 11:
        comment = "おはようございます"
    elif 11 <= current_hour < 18:
        comment =  "こんにちは"
    else:
        comment = "こんばんは"    
    status_text = f"Ping: {ping}ms | {comment}"
    return status_text