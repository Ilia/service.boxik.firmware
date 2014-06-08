# -*- coding: utf-8 -*-
#
#     Copyright (C) 2013 BOXiK
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import xbmc
import xbmcaddon
import xbmcgui
import urllib2
import urllib
import os
import hashlib
import download
import re
from backup import Backup, Restore

__addon_id__     = 'service.boxik.firmware'
__addon__        = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonname__    = __addon__.getAddonInfo('name')
__addonpath__    = __addon__.getAddonInfo('path').decode('utf-8')
__localize__     = __addon__.getLocalizedString
__icon__         = __addon__.getAddonInfo('icon')
__UPDATEHOST__   = "https://dl.dropboxusercontent.com/u/2180474/boxik"

def fetch_url(url):
    ''' Fetch url '''

    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    except urllib2.HTTPError, e:
        xbmc.log("BOXiK Auto Service: HTTPError %s" % str(e))
    except urllib2.URLError, e:
        xbmc.log("BOXiK Auto Service: URLError %s" % str(e))
    
    return False

def message(txt):
    ''' Send message to GUI '''

    xbmc.executebuiltin("XBMC.Notification(%s, %s, %d, %s)" % (__addonname__, txt, 5000, __icon__))

def set_setting(setting, value):
    ''' Generic way of setting settings '''

    return xbmcaddon.Addon(id = __addon_id__).setSetting(setting, value)

def get_setting(setting):
    ''' Generic way of getting settings '''

    return xbmcaddon.Addon(id = __addon_id__).getSetting(setting)

def set_lock():
    ''' Set lock - used to stop script running again '''

    xbmcgui.Window(10000).setProperty('update.lock', 'true')
     
def remove_lock():
    ''' Remove running lock '''

    xbmcgui.Window(10000).clearProperty('update.lock')

def is_running():
    ''' Check if script is already running '''

    if xbmcgui.Window(10000).getProperty('update.lock') == 'true':
        return True
    return False

def get_local_version():
    ''' Get the local version of the device '''

    try:
        f = open('/usr/share/xbmc/system/version', 'r')
        version = f.readline()
    except IOError:
        version = get_setting('current_version')
    
    xbmc.log('BOXiK Update Service: Local version = %s' % version)

    xbmcgui.Window(10000).setProperty("firmware.version", version)
    return str(version).strip(' \t\n\r')

def remote_path():
    ''' Get model, state and create url '''

    state = 'unstable' if get_setting('nightly_update') == 'true' else 'stable'

    try:
        f = open('/usr/share/xbmc/system/model', 'r')
        model = f.readline()
        model = str(model).strip(' \t\n\r')
    except IOError:
        xbmc.log('BOXiK Update Service: can\'t read model, setting old url')
        return "%s/%s/update.ini" % (__UPDATEHOST__, state)

    return "%s/%s/%s/update.ini" % (__UPDATEHOST__, model, state)
    

def new_update(silent=False):
    ''' Check if there is new updare '''

    if not silent:
        dp = xbmcgui.DialogProgress()
        dp.create("BOXiK Updater", "Checking for new updates",' ', 'Please Wait...')
    
    link = fetch_url(remote_path())
    if link:
        link = link.replace('\n','').replace('\r','')
        if not silent:
            dp.update(70)
        remote_version, update_url, update_md5  = re.compile('version="(.+?)".+?ile="(.+?)".+?d5="(.+?)"').findall(link)[0]   
        if not silent:
            dp.update(100)
            dp.close()

        xbmc.log('BOXiK Update Service: Remote versions = %s' % remote_version)
        if str(remote_version) != get_local_version():
            return remote_version, update_url, update_md5
    
    return False, False, False
   

def manual():
    ''' Run a manual update '''
    
    if is_running():
        message('Updater is running, please wait.')
        return

    if xbmcgui.Dialog().yesno(__addonname__, "Would you like to do an online update?"):
        new_version, update_url, update_md5 = new_update()
        xbmc.log('BOXiK Manual Service: New update check - %s' % new_version)
        if not new_version:
            dp = xbmcgui.Dialog()
            dp.ok(__addonname__, "Your BOXiK version %s is up to date." % get_local_version())
        else:
            start(new_version, update_url, update_md5)
    else:
        if xbmcgui.Dialog().yesno(__addonname__, \
                        "Do you have the update.zip on USB thumb?", \
                        "Selecting 'Yes' will backup, reboot and start the update."):
            try:
                backup = Backup( which_usb() , get_local_version() )
                backup.run()
                reboot()
            except:    
                dp.ok(__addonname__, \
                    "Backup could not be completed. Please use a 16GB USB or larger.", 
                    " ", \
                    "Update manually from Settings > Update")

def auto():
    ''' Run an auto update '''
    if is_running():
        message('Updater is running, please wait.')
        return

    if get_setting('auto_update') == 'true':
        new_version, update_url, update_md5 = new_update(True)
        xbmc.log('BOXiK Auto Service: New update check - %s' % new_version)
        start(new_version, update_url, update_md5)

def reboot():
    ''' Remove once of lock and reboot to update '''
    remove_lock()
    os.system('reboot recovery')


def usb_ok():
    ''' check if USB is ok - ie enough space WIP '''

    import subprocess
    df = subprocess.Popen(["df"], stdout=subprocess.PIPE)
    output = df.communicate()[0]
    device, size, used, available, percent, mountpoint = output.split("\n")[1].split()


def which_usb():
    ''' Find suitable USB device to store update '''

    try:
        root = "/media"
        mount = [name for name in os.listdir(root) if \
            os.path.isdir(os.path.join(root, name)) and \
            os.access(os.path.join(root, name), os.W_OK | os.X_OK) and \
            name != "EFI" and \
            not os.path.exists( os.path.join(root, name) + "/.empty" )][0]
        path = "%s/%s/" % (root, mount)
        xbmc.log("BOXiK Auto Service: setting path %s" % path)
        return path
    except IndexError:
        xbmc.log("BOXiK Auto Service: no path")
    except:
        xbmc.log("BOXiK Auto Service: bad path")

    return False

def start(version, update_url, update_md5):
    ''' init update process '''

    set_lock()
    if version and xbmcgui.Dialog().yesno(__addonname__, \
                        "New update ("+ version +") is available.", \
                        "Selecting 'Yes' will backup your data, download the update,", \
                        "reboot your device and start the update process."):
        download_location = which_usb()

        try:
            backup = Backup(download_location, get_local_version())
            backup.run()
        except:  
            dp = xbmcgui.Dialog()  
            dp.ok(__addonname__, \
                    "Backup could not be completed.", 
                    "Please use a 16GB USB or larger.", \
                    "Update manually from Settings > Update")
                
            remove_lock()
            return

        if download_location:
            xbmc.log("BOXiK Auto Service: %s %s %s %s " % \
                     (remote_path(), download_location, update_url, update_md5))
            if download.firmware(download_location, update_url, update_md5):
                reboot()
            else: 
                dp = xbmcgui.Dialog()
                dp.ok(__addonname__, "Download failed", "", "Try again later.")
        else:
            dp = xbmcgui.Dialog()
            dp.ok(__addonname__, \
                  "Please insert a compatible USB into the BOXiK", 
                  " ", \
                  "Update manually from Settings > Update")
    remove_lock()