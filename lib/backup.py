import os
import re
import glob
import time
import xbmc
import xbmcgui
import tarfile
import threading
import subprocess

from xml.dom import minidom

#XBMC_USER_HOME = os.environ.get("XBMC_USER_HOME", "/Users/ilia/Library/Application Support/XBMC/")

XBMC_USER_HOME = os.environ.get("XBMC_USER_HOME", "/root/.xbmc")
SSH_KEYS = "/etc/ssh"

BACKUP_DIRS = [XBMC_USER_HOME]

class Backup:
    
    backup_dir = False
    files_location = False

    def __init__(self, backup_dir, version):
        self.version = version
        self.backup_dir = backup_dir
        xbmc.log("BOXiK Auto Service: backing up to %s" % (self.backup_dir))


    def run(self):
        try:
            self.total_backup_size = 1
            self.done_backup_size = 1

            try:
                
              for directory in BACKUP_DIRS:
                  xbmc.log("BOXiK Auto Service: backing up dir %s" % (directory))
                  self.get_folder_size(directory)

            except Exception, e:
                xbmc.log("BOXiK Auto Service: error" + repr(e))
                
              
            xbmc.log("BOXiK Auto Service: backing up size %s" % (self.total_backup_size))

            xbmcDialog = xbmcgui.Dialog()

            self.backup_dlg = xbmcgui.DialogProgress()
            self.backup_dlg.create('BOXiK Backup', 'Backing up, please wait ...', ' ', ' ')
            
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            
            #self.version = "Build_X"

            self.backup_file = "backup." + self.version + '.tar'

            xbmc.log("BOXiK Auto Service: backing up file %s" % (self.backup_file))

            tar = tarfile.open(self.backup_dir + self.backup_file, 'w')
            for directory in BACKUP_DIRS:
                self.tar_add_folder(tar, directory)

            tar.close()
            self.backup_dlg.close()
            del self.backup_dlg
            
            # self.oe.dbg_log('system::do_backup', 'exit_function', 0)
        except Exception, e:
            xbmc.log("BOXiK Auto Service: backup error: " + repr(e))
            self.backup_dlg.close()
            
            # self.oe.dbg_log('system::do_backup', 'ERROR: (' + repr(e) + ')')

    def tar_add_folder(self, tar, folder):
        try:
            for item in os.listdir(folder):

                if item == self.backup_file:
                    continue

                if self.backup_dlg.iscanceled():
                    try:
                        os.remove(self.backup_dir + self.backup_file)
                    except:
                        pass
                    return 0

                itempath = os.path.join(folder, item)
                if os.path.islink(itempath):
                    tar.add(itempath)
                elif os.path.ismount(itempath):
                    tar.add(itempath,recursive=False)
                elif os.path.isdir(itempath):
                    if os.listdir(itempath) == []:
                        tar.add(itempath)
                    else:
                        self.tar_add_folder(tar, itempath)
                else:
                    self.done_backup_size += os.path.getsize(itempath)
                    tar.add(itempath)
                    if hasattr(self, 'backup_dlg'):
                        progress = round(1.0 * self.done_backup_size
                                / self.total_backup_size * 100)
                        self.backup_dlg.update(int(progress), 'Backing up, please wait ...', folder,
                                item)
        except Exception, e:
            xbmc.log("BOXiK Auto Service: error" + repr(e))
            self.backup_dlg.close()
            # self.oe.dbg_log('system::tar_add_folder', 'ERROR: ('
            #                + repr(e) + ')')


    def get_folder_size(self, folder):

        for item in os.listdir(folder):
            itempath = os.path.join(folder, item)
            if os.path.isfile(itempath):
                self.total_backup_size += os.path.getsize(itempath)
            elif os.path.ismount(itempath):
                continue
            elif os.path.isdir(itempath):
                self.get_folder_size(itempath)


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