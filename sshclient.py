# -*- coding: utf-8 -*-

import paramiko
import stat
from logger import Logger

class SshClient(object):
    _instance = None
    def __new__(self, *args, **kwargs):
        if not self._instance:
            self._instance = super(SshClient, self).__new__(self, *args, **kwargs)
            self.sshClient = None
            self.sftpClient = None
            self.transport = None
            self.log = Logger()
        return self._instance

    def connect(self, host, port, user, password):
        try:
            self.sshClient = paramiko.SSHClient()
            self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.sshClient.connect(hostname=host, username=user, password=password, port=port)
            self.transport = paramiko.Transport((host, port))
            self.transport.connect(username=user, password=password)
            self.sftpClient = paramiko.SFTPClient.from_transport(self.transport)
            return True
        except Exception, e:
            self.log.error("No connection to remote host: %s" % e)
        return False

    def execCommand(self, command, printLog=False):
        if printLog:
            self.log.notice("Execute command '%s' on remote host" % command)
        stdin, stdout, stderr = self.sshClient.exec_command(command)
        if printLog:
            stderrStr = stderr.read()
            if stderrStr:
                self.log.error("stderr: %s" % stderrStr.strip())
            stdoutStr = stdout.read()
            if stdoutStr:
                self.log.notice("stdout: %s" % stdoutStr.strip())

    def sendFile(self, src, dest):
        self.sftpClient.put(src, dest)
    
    def closeConnection(self):
        self.sftpClient.close()
        self.sshClient.close()
        self.transport.close()
    
    def isDir(self, path):
        return stat.S_ISDIR(self.sftpClient.lstat(path).st_mode)
