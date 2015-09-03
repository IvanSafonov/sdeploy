# -*- coding: utf-8 -*-

import os
import json
from logger import Logger

class ConfigLoader(object):
    def __init__(self, filePath):
        self.log = Logger()
        self.jsonData = None
        self._load(filePath)

    def _load(self, filePath):
        try:
            if not os.path.isfile(filePath):
                raise Exception("Config file not found - '%s'" % filePath)
            with open(filePath) as file:
                self.jsonData = json.load(file)
        except Exception, e:
            self.log.error("Load config file error: %s" % e)
            exit(1)
    
    def config(self, kits):
        confKits = self.jsonData.keys()
        if len(confKits) == 0:
            self.log.error("No kits in the config file")
            exit(1)
        if kits and len(kits) > 0:
            if not set(kits).issubset(set(confKits)):
                self.log.error("No such kits '%s' in the config file" % kits)
                exit(1)
            confKits = kits

        result = {'preInstall': [], 'files': [], 'postInstall': []}
        addedKits = set()
        for kit in confKits:
            self._addKit(result, addedKits, kit)
        return result

    def _addKit(self, result, addedKits, name):
        if name in addedKits:
            return
        if name not in self.jsonData:
            self.log.error("Unknown kit '%s'" %name)
            return
        addedKits.add(name)
        kit = self.jsonData[name]
        if 'preInstall' in kit:
            result['preInstall'].extend(kit['preInstall'])
        if 'files' in kit:
            result['files'].extend(kit['files'])
        if 'postInstall' in kit:
            result['postInstall'].extend(kit['postInstall'])
        if 'kits' in kit:
            for subKit in kit['kits']:
                self._addKit(result, addedKits, subKit)
