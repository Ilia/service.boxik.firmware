import xbmc
import xbmcgui
import xbmcvfs
import os.path
import time

'''
Notes: 
    -- WIP --
    Restore - Once backup, update and reboot occurs, the newly updated service needs to 
    check for backup (ie backup folder on usb) and restore all files 
    if userdata is bad (ie md5 userdata/Database/MyVideos75.db), delete backup, 
    ask user to reboot
    Backup  - class needs to be independant so that can be called
    Restore - class needs to be independant so that can be called
'''
class Backup:
	backup_dir = False
	files_location = False

	def __init__(self, backup_dir):
		self.backup_dir = backup_dir + '_backup/'
		self.files_location = xbmc.translatePath('special://userdata') 
		xbmc.log("BOXiK Auto Service: backing up %s to %s" % (self.files_location, self.backup_dir))
		self.filesystem = XBMCFileSystem()

	def run(self):
		if not self.filesystem.exists(self.backup_dir):
			self.filesystem.mkdir(self.backup_dir)

		return False


class Restore:

	def __init__(self):
		pass

	def run(self):
		pass


class XBMCFileSystem:

    def listdir(self,directory):
        return xbmcvfs.listdir(directory)

    def mkdir(self,directory):
        return xbmcvfs.mkdir(directory)

    def put(self,source,dest):
        return xbmcvfs.copy(source,dest)
        
    def rmdir(self,directory):
        return xbmcvfs.rmdir(directory,True)

    def exists(self,aFile):
        return xbmcvfs.exists(aFile)