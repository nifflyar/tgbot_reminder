
# import datetime 
# from datetime import UTC


# # now = datetime.utcnow()
# date_today = now.date() # "02/03/2025"
# time_now = now.time().replace(second=0, microsecond=0)   # "14:00"

# print(date_today, time_now)


# now = datetime.datetime.now(UTC)
# dt_combined = datetime.datetime.combine(now.date(), now.time())
# shifted_dt = (dt_combined - datetime.timedelta(hours=int("5"))).year

# timme = datetime.time(hour=15, minute=15)

# dt = datetime.datetime.combine(datetime.datetime.today(), timme)
# shifted = (dt - datetime.timedelta(hours=5)).time()

# print(shifted)

# s = ["h","e","l","l","o"]

# for i in range(len(s)-2, -1, -1):
#     s.append(s.pop(i))

# now = datetime.datetime.utcnow()
# today = now.date()
# tomorrow = now.date() + datetime.timedelta(days=1)

# current = datetime.datetime.combine(today, datetime.time(hour=19, minute=0))
# end = datetime.datetime.combine(today, datetime.time(hour=5, minute=0))

# interval = datetime.timedelta(minutes=60)

# while current <= end:
#     run_time = current
#     if run_time >= now:
#         print(run_time)

#     # print(current, "|", run_time)
#     current+=interval

# async def myau():
#     tz = await select_timezone(user_id=1)
#     return tz
# tz = myau()
