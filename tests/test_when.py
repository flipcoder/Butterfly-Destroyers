#!/usr/bin/env python
import sys
import math

sys.path.append("..")

from game.when import When

def test_when():
    class Counter:
        def __init__(self):
            self.x = 0
        def increment(self):
            print(self.x)
            self.x += 1
    
    c = Counter()
    s = When()
    slot = s.every(2, lambda: c.increment())
    assert slot.t == 2
    assert c.x == 0
    s.update(1)
    assert math.isclose(slot.t, 1)
    assert c.x == 0
    s.update(1)
    assert math.isclose(slot.t, 0) # wrap
    assert c.x == 1
    s.update(1)
    assert c.x == 1
    s.update(1)
    assert c.x == 2
