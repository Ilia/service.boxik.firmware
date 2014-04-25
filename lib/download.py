import urllib2
import urllib
import xbmcgui
import os
import time
import xbmc 

def firmware(localpath, remote_url, remote_md5):
	localfile = localpath + 'update.zip'
	if get_file(remote_url, localfile) and check_md5(localfile, remote_md5):
		os.system('echo "--update_package=/udisk/update.zip" > %s/factory_update_param.aml' % localpath)
		return True
	else:
		return False

def get_file(url, localfile):
	try:
		dp = xbmcgui.DialogProgress()
		dp.create("BOXiK Updater","Downloading new update",' ', 'Please wait...')
		start_time = time.time() 
		urllib.urlretrieve(url,localfile,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs, dp, start_time))
		dp.close()
		return True
	except: 
		xbmc.log("BOXiK Auto Service: Can't start download")
		return False

def _pbhook(numblocks, blocksize, filesize, dp, start_time):
	if dp.iscanceled(): 
		xbmcgui.Window(10000).clearProperty('update.lock')
		dp.close()
		raise StopDownloading('Stopped Downloading')

	try: 
		percent = min(numblocks * blocksize * 100 / filesize, 100) 
		currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
		kbps_speed = numblocks * blocksize / (time.time() - start_time) 
		if kbps_speed > 0: 
			eta = (filesize - numblocks * blocksize) / kbps_speed 
		else: 
			eta = 0 
		kbps_speed = kbps_speed / 1024 
		total = float(filesize) / (1024 * 1024) 
		eta = eta / 60
		mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total) 
		if abs(eta) >= 1:
			mbs = '%s - about %d min(s)' % (mbs, eta)
		else:
			mbs = '%s - less than a minute' % (mbs)
		dp.update(percent, 'Downloading new update', '', mbs)
	except: 
		percent = 100 
		xbmcgui.Window(10000).clearProperty('update.lock')
		dp.update(percent)

def check_md5(downloaded, remote_md5): 
	if MD5(downloaded) != remote_md5:
		xbmc.log("BOXiK Auto Service: Bad md5")
		return False
	
	return True

def MD5(path):
	if not os.path.exists(path):
		return False
	try:
		import hashlib        
		return hashlib.md5(open(path, 'r').read()).hexdigest()
	except:
		pass
	try:
		import md5
		return md5.new(open(path, 'r').read() ).hexdigest()
	except:
		pass

	return False

class StopDownloading(Exception): 
	def __init__(self, value): 
		self.value = value 
	def __str__(self): 
		return repr(self.value)