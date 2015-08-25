# -*- coding: utf-8 -*-

class Logger(object):
    _instance = None
    def __new__(self, *args, **kwargs):
        if not self._instance:
            self._instance = super(Logger, self).__new__(self, *args, **kwargs)
        return self._instance

    def info(self, msg):
        print msg

    def notice(self, msg):
        print '\033[92m%s\033[0m' % msg
        
    def error(self, msg):
        print '\033[91m%s\033[0m' % msg
        
    def warn(self, msg):
        print '\033[93m%s\033[0m' % msg
