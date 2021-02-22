#!/usr/bin/env python3

import threading as thread

class Thread:
    @staticmethod
    def start(group = None, target = None, name = None, args = (), kwargs = {}):
        thread.Thread(group = group, target = target, name = name, args = args, kwargs = kwargs).run()

        
def Lock():
    return thread.Lock()
