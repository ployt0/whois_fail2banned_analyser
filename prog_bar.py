"""
This demo can be easily inlined for reuse. I'd make it a function but it
needs tight integration or a call back which would spoil/bloat the demo.
"""

import sys,time

cnt = 33
bar_len = 40
for i in range(cnt + 1):
    time.sleep(0.1)
    prcnt_done = i/float(cnt)
    steps_done = int(prcnt_done * bar_len)
    steps_left = bar_len - steps_done
    sys.stdout.write(
        f'\r{int(prcnt_done * 100.0):>3}% [' + '█' * steps_done + ' ' * steps_left + ']')
    sys.stdout.flush()
print()