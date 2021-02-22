#!/usr/bin/env python3

import os
import sys
import traceback
import time
import LogWrapper.src.LogThread as LogThread
from enum import Enum

class LogLevel(Enum):
    Info = 0
    Debug = 1
    Warning = 2
    Error = 3

__log_level__ = { LogLevel.Info : "Info", LogLevel.Debug : "Debug",
                  LogLevel.Warning : "Warning", LogLevel.Error : "Error" }
__log_dir__ = r".\log"
__log_path__ = __log_dir__ + r"\log_{}_{}.txt"
__single_msg_len__ = 80

log_level = __log_level__

'''
* How to use
  Create a new logger object first,
  I had been provide 5 methods like `console`, `info`, `debug`, `warning` and `error` to use,
  you could extent other kinds of log method what you need.
* Notice
  You need to call `close` or `Logger.closeAll` static method instead when a context end.
  I suggest you to use `Logger.closeAll` more frequently, because all logger object will
  managed by Logger instance.
* Where find log files
  Open current working dir, and all log files store in the sub dir name log.
'''
class Logger:
    instance = []
    file = []
    inst_cnt = 0
    lock = LogThread.Lock()

    def __init__(self, log_name, level: str=__log_level__[LogLevel.Info]):
        Logger.instance.append(self)
        self._level = level
        self._name = log_name
        self._date_fmt = time.strftime("%Y-%m-%d", time.localtime())
        self._date = self._date_fmt.replace('-', '')
        self._inst_idx = Logger.inst_cnt
        Logger.inst_cnt += 1
        if not os.path.exists(__log_dir__):
            os.mkdir(__log_dir__)
        path = __log_path__.format(self._name, self._date)
        Logger.file.append(open(path, "a+", encoding="utf-8"))
        print("Logger initialize success...")

    def switchlv(self, level: str=__log_level__[LogLevel.Info]):
        self._level = level

    def console(self, *msgs, **kwargs):
        LogThread.Thread.start(target=self.__write, args=(self._level, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msgs))

    def info(self, *msgs, **kwargs):
        LogThread.Thread.start(target=self.__write, args=(__log_level__[LogLevel.Info], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msgs))

    def debug(self, *msgs, **kwargs):
        LogThread.Thread.start(target=self.__write, args=(__log_level__[LogLevel.Debug], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msgs))

    def warning(self, *msgs, **kwargs):
        LogThread.Thread.start(target=self.__write, args=(__log_level__[LogLevel.Warning], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msgs))

    def error(self, *msgs, **kwargs):
        LogThread.Thread.start(target=self.__write, args=(__log_level__[LogLevel.Error], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msgs))

    def __write(self, *args, **kwargs):
        Logger.lock.acquire();
        if args is not None:
            text = '[{} {}]: '.format(args[0], args[1])
            for arg in args[2:]:
                for msg in arg:
                    text += msg
            text = list(text)
            msg_len = len(text)
            insert = 0
            while insert < msg_len:
                if insert > 0:
                     text.insert(insert, "\n\t\t")
                insert += __single_msg_len__
            text = ''.join(text)
            Logger.file[self._inst_idx].write(text)
            print(text)
        Logger.file[self._inst_idx].write("\n")
        Logger.lock.release()

    def __delete_inst(self):
        Logger.file[self._inst_idx].close()
        if self._inst_idx < Logger.inst_cnt - 1:
            for inst in Logger.instance[self._inst_idx + 1:]:
                inst._inst_idx -= 1
        del Logger.file[self._inst_idx]
        del Logger.instance[self._inst_idx]
        Logger.inst_cnt -= 1

    def close(self):
        self.__delete_inst()
        self = None
        print("Logger has been close")

    @staticmethod
    def closeAll():
        if Logger.inst_cnt > 0:
            for singleFile in Logger.file:
                singleFile.close()
        print("All Logger has been closed")
