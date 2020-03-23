#!/usr/bin/env python

import weakref


class Slot:
    def __init__(self, func, sig):
        self.func = func
        self.sig = weakref.ref(sig)
        self.once = False

    def __call__(self, *args):
        func = self.func
        if isinstance(self.func, weakref.ref):
            func = func()
            if not func:
                self.disconnect()
                return None
        r = func(*args)
        if self.once:
            self.disconnect(self)
        return r

    def do(self, action, *args):
        func = self.func
        if isinstance(func, weakref.ref):
            func = func()
            if not func:
                return None
        return action(func, *args)

    def disconnect(self):
        sig = self.sig()
        if not sig:
            return None
        return sig.disconnect(self)

    def get(self):
        func = self.func
        if isinstance(func, weakref.ref):
            func = self.func()
        return func

    def __del__(self):
        self.disconnect()


class Signal:
    def __init__(self):
        self.slots = []
        self.blocked = 0
        self.queued = []

    def __len__(self):
        return len(self.slots)

    def __call__(self, *args):

        self.blocked += 1
        for slot in self.slots:
            if isinstance(slot, weakref.ref):
                wref = slot
                slot = wref()
                if slot is None:
                    self.disconnect(wref)  # we're blocked, so this will queue
            if slot is not None:
                slot(*args)
        self.blocked -= 1

        if self.blocked == 0:
            for func in self.queued:
                func()
            self.queued = []

    def do(self, func, *args):
        if self.blocked:
            self.queued.append(lambda func=func, args=args: self.do(func, *args))
            return None

        for slot in self.slots:
            slot.do(func, *args)

    def once(self, func):
        if self.blocked:
            self.queued.append(lambda func=func: self.once(func))
            return None

        slot = Slot(func, self)
        slot.once = True
        self.slots.append(slot)
        return slot

    def connect(self, func, weak=False):

        if self.blocked:
            # if we're blocked, then queue the call
            if isinstance(func, Slot):
                slot = func
            else:
                slot = Slot(func, self)
            wslot = weakref.ref(slot) if weak else slot
            self.queued.append(lambda wslot=wslot: self.slots.append(wslot))
            return slot

        # already a slot, add it
        if isinstance(func, Slot):
            slot = func  # already a slot
            self.slots.append(slot)
            return slot

        # make slot from func
        slot = Slot(func, self)
        wslot = weakref.ref(slot) if weak else slot
        self.slots.append(wslot)
        return slot

    def disconnect(self, slot):
        if self.blocked:
            self.queued.append(lambda slot=slot: self.disconnect(slot))
            return None

        if isinstance(slot, weakref.ref):
            # try to remove weak reference
            wref = slot
            slot = wref()
            for i in range(len(self.slots)):
                if slot:  # weakref dereffed?
                    if self.slots[i] is slot:
                        del self.slots[i]
                        return True
                if self.slots[i] is wref:
                    del self.slots[i]
                    return True

        elif isinstance(slot, Slot):
            # remove slot
            for i in range(len(self.slots)):
                if self.slots[i] is slot:
                    del self.slots[i]
                    return True
        else:
            # remove slot with slot==func
            for i in range(len(self.slots)):
                if self.slots[i].func is slot:
                    del self.slots[i]
                    return True
            return False

    def clear(self):
        if self.blocked:
            self.queued.append(lambda: self.clear())
            return None

        b = bool(len(self.slots))
        self.slots = []
        return b

    def sort(self, key=None):
        if self.blocked:
            self.queued.append(lambda: self.sort())
            return None

        if key is None:
            self.slots.sort()
            return self

        self.slots = sorted(self.slots, key=lambda x: key(x))
        return self

    def __del__(self):
        self.clear()
