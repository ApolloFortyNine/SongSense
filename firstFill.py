from fill import Fill
import time

"""
with open('C:/path/numbers.txt') as f:
    lines = f.read().splitlines()
"""

with open('scanned') as f:
    lines = f.read().split(' ')
filler = Fill()

count = 0
count_all = 0
start = time.time()
true_start = time.time()
for name in lines:
    if not filler.in_db(name):
        filler.fill_data(name)
        count += 1
        count_all += 1

    print(name)
    time_passed = (time.time() - start)
    if time_passed <= 60 and (count >= 120):
        print("Throttle")
        time.sleep(60 - time_passed)
        print("Go")
        count = 0
        start = time.time()
    elif time_passed > 60:
        count = 0
        start = time.time()
print((time.time() - true_start) / count_all)

