import sys
from collections import Counter

c = Counter()

for line in (_.strip() for _ in sys.stdin):
    for pos, letter in enumerate(line):
        if letter == '1':
            c[pos] += 1

for key, val in c.most_common():
    print '%2s %7s' % (key, val)
