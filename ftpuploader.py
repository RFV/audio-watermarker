import ftplib
import os

class FTPUploader(object):
    def __init__(self, server, username, password):
        super(FTPUploader, self).__init__()
        # self.server = server
        # self.username = username
        # self.password = password
        self.myFTP = ftplib.FTP(server, username, password)

    def upload(self, path, top_folder=False):
        if top_folder:
            self.myFTP.mkd(top_folder)
            self.myFTP.cwd(top_folder)
        os.chdir(path)
        files = os.listdir(path)
        for f in files:
            if os.path.isfile(path + r'\{}'.format(f)):
                fh = open(f, 'rb')
                self.myFTP.storbinary('STOR %s' % f, fh)
                fh.close()
            elif os.path.isdir(path + r'\{}'.format(f)):
                self.myFTP.mkd(f)
                self.myFTP.cwd(f)
                self.upload(path + r'\{}'.format(f))
        self.myFTP.cwd('..')
        os.chdir('..')