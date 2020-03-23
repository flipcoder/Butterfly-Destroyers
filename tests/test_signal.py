#!/usr/bin/env python
import sys

sys.path.append("..")

from game.signal import Signal


def test_signal():

    s = Signal()
    hello = s.connect(lambda: print("hello ", end=""))

    s.connect(lambda: print("world"))
    assert len(s) == 2
    s()  # 'hello world'

    assert s.disconnect(hello)
    s()  # 'world'
    assert len(s) == 1

    s.clear()
    assert len(s) == 0


def test_signal_queue():

    # queued connection
    s = Signal()
    s.blocked += 1
    a = s.connect(lambda: print("queued"))
    assert len(s.queued) == 1
    s()  # nothing
    s.blocked -= 1
    for slot in s.queued:
        slot()
    s.queued = []
    s()  # "queued"

    # queued disconnection
    s.blocked += 1
    a.disconnect()
    assert len(s) == 1  # still attached
    assert len(s.queued) == 1
    s.blocked -= 1
    for q in s.queued:
        q()
    s.queued = []
    assert len(s) == 0

def test_signal_weak():
    
    s = Signal()
    w = s.connect(lambda: print("test"), weak=True)
    del w
    assert len(s) == 1
    s()
    assert len(s) == 0

    s = Signal()
    func = lambda: print('test')
    w = s.connect(func)
    del s # slot outlives signal?
    assert w.sig() == None # it works
    del w


