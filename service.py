#!/usr/bin/python

import sys
import os
import xbmc
import xbmcgui
import lib.common as service

class Main:
    def __init__(self):
        if not sys.argv[0]:
            service.message("Service started")
            service.remove_lock()
            xbmc.executebuiltin('XBMC.AlarmClock(BOXiKCheckAtBoot,XBMC.RunScript(service.boxik.firmware, auto),00:00:10,silent)')
            xbmc.executebuiltin('XBMC.AlarmClock(BOXiKCheckWhileRunning,XBMC.RunScript(service.boxik.firmware, auto),12:00:00,silent,loop)')
        else:
            if not xbmc.Player().isPlayingVideo():
                try:
                    service.get_local_version()
                    if sys.argv[1] == 'auto':
                        service.auto()
                    elif sys.argv[1] == 'manual': 
                        service.manual()
                    else:
                        pass
                except IndexError:
                    pass

if (__name__ == "__main__"):
    Main()
