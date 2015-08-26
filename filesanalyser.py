#!/usr/bin/env python

import os
import json
from datetime import datetime
import re
from sshclient import SshClient
from logger import Logger

class FilesAnalyser(object):
    def __init__(self, workDir, config, fullUpdate, buildDir):
        self.log = Logger()
        self.newChanges = {}
        self.filesToSend = []
        self.fullUpdate = fullUpdate
        self.config = config
        self.buildDir = buildDir
        self.changesFileName = os.path.join(workDir, 'changes')
        self.prevChanges = self._loadPreviousChanges()

    def _addFile(self, file):
        if os.path.isdir(file['src']):
            for item in os.listdir(file['src']):
                self._addFile({'src': os.path.join(file['src'], item), 
                               'dest': os.path.join(file['dest'], item), 
                               'permit': file['permit'],
                               'mask': file['mask'],
                               'exclude': file['exclude']
                               })
            return

        if file['mask']:
            try:
                mask = re.compile(file['mask'])
            except Exception, e:
                self.log.error("File mask error in '%s': %s" % (file, e))
                return
            if not mask.match(os.path.basename(file['src'])):
                return

        if file['exclude']:
            try:
                exclude = re.compile(file['exclude'])
            except Exception, e:
                self.log.error("Exclude mask error in '%s': %s" % (file, e))
                return
            if exclude.match(os.path.basename(file['src'])):
                return

        srcTime = os.path.getmtime(file['src'])
        self.newChanges[file['src']] = {"time": srcTime, "dest": file['dest']}
        if not self.fullUpdate and file['src'] in self.prevChanges and abs(srcTime - self.prevChanges[file['src']]["time"]) <= 0.01:
            return
        self.filesToSend.append(file)

    def getFilesToSend(self):
        for file in self.config['files']:
            if not 'src' in file:
                self.log.warn("Empty 'src' field in '%s'" % file)
                continue
            else:
                file['src'] = file['src'].replace("%{buildDir}", self.buildDir)
            if not 'dest' in file:
                self.log.warn("Empty 'dest' field in '%s'" % file)
                continue
            if not os.path.exists(file['src']):
                self.log.warn("Path '%s' isn't exists" % file['src'])
                continue
            for field in ['permit', 'mask', 'exclude']:
                if not field in file:
                    file[field] = None
                
            if os.path.isfile(file['src']) and SshClient().isDir(file['dest']):
                file['dest'] = os.path.join(file['dest'], os.path.basename(file['src']))
                
            self._addFile(file)
        self._saveLastChanges()
        return self.filesToSend

    def getFilesToRemove(self):
        result = []
        for fileName in self.prevChanges:
            if not os.path.isfile(fileName):
                result.append(self.prevChanges[fileName]['dest'])
        return result

    def _loadPreviousChanges(self):
        data = {}
        if not os.path.isfile(self.changesFileName):
            return data
        try:
            with open(self.changesFileName) as file:
                data = json.load(file)
        except Exception, e:
            self.log.error("Load last changes file error: %s" % e)

        return data

    def _saveLastChanges(self):
        with open(self.changesFileName, 'w') as outfile:
            json.dump(self.newChanges, outfile)
