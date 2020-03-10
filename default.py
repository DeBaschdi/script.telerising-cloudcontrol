import os
import platform
import subprocess
from subprocess import Popen
import re
import xbmc
import xbmcaddon
import xbmcgui
import json
import urllib
import requests
import xbmcvfs
from zipfile import ZipFile

ADDON = xbmcaddon.Addon(id="script.telerising-cloudcontrol")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
addonpath = xbmc.translatePath(ADDON.getAddonInfo('path'))
mute_notify = ADDON.getSetting('hide-osd-messages')

## Read Telerising Server Settings
connection_type = ADDON.getSetting('connection_type')
address = ADDON.getSetting('address')
port = ADDON.getSetting('port')
storage_path = ADDON.getSetting('storage_path').decode('utf-8')
quality = ADDON.getSetting('quality')
audio_profile = ADDON.getSetting('audio_profile')

## Translate Connection Type
if connection_type == 'true':
    connection_mode = "https://"
    port = ''
    use_port = ''
elif connection_type == 'false':
    connection_mode = "http://"
    use_port = ':'

## Translate Video Settings
if quality == '432p25':
    bandwith = "1500"
elif quality == '576p50':
    bandwith = "2999"
elif quality == '720p25':
    bandwith = "3000"
elif quality == '720p50':
    bandwith = "5000"
elif quality == '1080p25':
    bandwith = "4999"
elif quality == '1080p50':
    bandwith = "8000"

machine = platform.machine()

## Make OSD Notify Messages
OSD = xbmcgui.Dialog()
def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)

## Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[%s %s] %s' % (addon_name, addon_version, str(message)), loglevel)

## Check Machine Type
def machine_type():
    ##Check under Whitch Machine Type this Addon is running
    if machine == 'x86_64':
        log("Machine is Linux, " + machine, xbmc.LOGNOTICE)
        return True
    elif machine == 'AMD64':
        log("Machine is Windows, " + machine, xbmc.LOGNOTICE)
        return True
    elif machine == 'OSX64':
        log("Machine is OSX, " + machine, xbmc.LOGNOTICE)
        return True
    elif machine == 'armv7l':
        log("Machine is Linux,  " + machine, xbmc.LOGNOTICE)
        return True
    elif machine == 'armv8l':
        log("Machine is Linux, " + machine, xbmc.LOGNOTICE)
        return True
    elif machine == 'aarch64':
        log("Machine is Android, " + machine, xbmc.LOGNOTICE)
        return True
    else:
        return False
machine_type()

##Check Setup
if machine_type() == False:
    log(machine + " is currently not supported", xbmc.LOGERROR)
    notify(addon_name, 'No vaild Machine found "' + machine + '" is currently not supportet', icon=xbmcgui.NOTIFICATION_ERROR)
    xbmc.sleep(5000)
    quit()

if address  == '0.0.0.0':
    log('You need to setup Telerising Server First, Check IP / Port', xbmc.LOGERROR)
    notify(addon_name, 'You need to setup Telerising Server First, Check IP / Port', icon=xbmcgui.NOTIFICATION_ERROR)
    xbmc.sleep(5000)
    quit()

## Create needed Folders
if machine == 'AMD64':
    binpath = os.path.join(addonpath, "bin\\")
    runpath = os.path.join(datapath, "bin\\")
    temppath = os.path.join(datapath, "temp\\")
else:
    binpath = os.path.join(addonpath, "bin/")
    runpath = os.path.join(datapath, "bin/")
    temppath = os.path.join(datapath, "temp/")

def create_folders():
    # deal with bug that happens if the datapath not exist
    if not os.path.exists(runpath):
        os.makedirs(runpath)
    if not os.path.exists(temppath):
        os.makedirs(temppath)
create_folders()

# Install needed Files
def install_files():
    ##Check under Whitch Machine Type this Addon is running and copy needed files
    if machine_type() == True:
        #notify(addon_name, 'Installing ffmpeg...',icon=xbmcgui.NOTIFICATION_INFO)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(addon_name, 'Installing ffmpeg...')
        if machine == 'x86_64':
            url_ffprobe = 'https://github.com/DeBaschdi/packages/raw/master/ffprobe_x86_64.zip'
            url_ffmpeg = 'https://github.com/DeBaschdi/packages/raw/master/ffmpeg_x86_64.zip'

            ## Download ffprobe
            log("Downloading FFProbe.... " + url_ffprobe + ' to ' + runpath + 'ffprobe.zip', xbmc.LOGNOTICE)
            ffprobe_zip = requests.get(url_ffprobe)
            open(runpath + 'ffprobe.zip', 'wb').write(ffprobe_zip.content)

            ## Download ffmpeg
            log("Downloading FFMpeg.... " + url_ffmpeg + ' to ' + runpath + 'ffmpeg.zip', xbmc.LOGNOTICE)
            ffmpeg_zip = requests.get(url_ffmpeg)
            open(runpath + 'ffmpeg.zip', 'wb').write(ffmpeg_zip.content)

            ## Extract
            log("Extracting...", xbmc.LOGNOTICE)
            with ZipFile(runpath + 'ffprobe.zip', 'r') as zipObj1:
                # Extract all the contents of zip file in different directory
                zipObj1.extractall(runpath)
            with ZipFile(runpath + 'ffmpeg.zip', 'r') as zipObj2:
                # Extract all the contents of zip file in different directory
                zipObj2.extractall(runpath)

            ## Set Premissions
            rights = "chmod 777 -R " + runpath
            subprocess.Popen(rights, shell=True)

        elif machine == 'AMD64':
            url_ffprobe = 'https://github.com/DeBaschdi/packages/raw/master/ffprobe_amd64.zip'
            url_ffmpeg = 'https://github.com/DeBaschdi/packages/raw/master/ffmpeg_amd64.zip'

            ## Download ffprobe
            log("Downloading FFProbe.... " + url_ffprobe + ' to ' + runpath + 'ffprobe.zip', xbmc.LOGNOTICE)
            ffprobe_zip = requests.get(url_ffprobe)
            open(runpath + 'ffprobe.zip', 'wb').write(ffprobe_zip.content)

            ## Download ffmpeg
            log("Downloading FFMpeg.... " + url_ffmpeg + ' to ' + runpath + 'ffmpeg.zip', xbmc.LOGNOTICE)
            ffmpeg_zip = requests.get(url_ffmpeg)
            open(runpath + 'ffmpeg.zip', 'wb').write(ffmpeg_zip.content)

            ## Extract
            log("Extracting...", xbmc.LOGNOTICE)
            with ZipFile(runpath +'ffprobe.zip', 'r') as zipObj1:
                # Extract all the contents of zip file in different directory
                zipObj1.extractall(runpath)
            with ZipFile(runpath +'ffmpeg.zip', 'r') as zipObj2:
                # Extract all the contents of zip file in different directory
                zipObj2.extractall(runpath)

        elif machine == 'armv7l':
            url_ffprobe = 'https://github.com/DeBaschdi/packages/raw/master/ffprobe_arm32.zip'
            url_ffmpeg = 'https://github.com/DeBaschdi/packages/raw/master/ffmpeg_arm32.zip'

            ## Download ffprobe
            log("Downloading FFProbe.... " + url_ffprobe + ' to ' + runpath + 'ffprobe.zip', xbmc.LOGNOTICE)
            ffprobe_zip = requests.get(url_ffprobe)
            open(runpath + 'ffprobe.zip', 'wb').write(ffprobe_zip.content)

            ## Download ffmpeg
            log("Downloading FFMpeg.... " + url_ffmpeg + ' to ' + runpath + 'ffmpeg.zip', xbmc.LOGNOTICE)
            ffmpeg_zip = requests.get(url_ffmpeg)
            open(runpath + 'ffmpeg.zip', 'wb').write(ffmpeg_zip.content)

            ## Extract
            log("Extracting...", xbmc.LOGNOTICE)
            with ZipFile(runpath + 'ffprobe.zip', 'r') as zipObj1:
                # Extract all the contents of zip file in different directory
                zipObj1.extractall(runpath)
            with ZipFile(runpath + 'ffmpeg.zip', 'r') as zipObj2:
                # Extract all the contents of zip file in different directory
                zipObj2.extractall(runpath)

            ## Set Premissions
            rights = "chmod 777 -R " + runpath
            subprocess.Popen(rights, shell=True)

        elif machine == 'armv8l':
            url_ffprobe = 'https://github.com/DeBaschdi/packages/raw/master/ffprobe_arm64.zip'
            url_ffmpeg = 'https://github.com/DeBaschdi/packages/raw/master/ffmpeg_arm64.zip'

            ## Download ffprobe
            log("Downloading FFProbe.... " + url_ffprobe + ' to ' + runpath + 'ffprobe.zip', xbmc.LOGNOTICE)
            ffprobe_zip = requests.get(url_ffprobe)
            open(runpath + 'ffprobe.zip', 'wb').write(ffprobe_zip.content)

            ## Download ffmpeg
            log("Downloading FFMpeg.... " + url_ffmpeg + ' to ' + runpath + 'ffmpeg.zip', xbmc.LOGNOTICE)
            ffmpeg_zip = requests.get(url_ffmpeg)
            open(runpath + 'ffmpeg.zip', 'wb').write(ffmpeg_zip.content)

            ## Extract
            log("Extracting...", xbmc.LOGNOTICE)
            with ZipFile(runpath + 'ffprobe.zip', 'r') as zipObj1:
                # Extract all the contents of zip file in different directory
                zipObj1.extractall(runpath)
            with ZipFile(runpath + 'ffmpeg.zip', 'r') as zipObj2:
                # Extract all the contents of zip file in different directory
                zipObj2.extractall(runpath)

            ## Set Premissions
            rights = "chmod 777 -R " + runpath
            subprocess.Popen(rights, shell=True)

        #elif machine == 'aarch64':
            #src = os.path.join(binpath, "ffmpeg_android")
            #dest = '/data/data/%s/ffmpeg' % android_get_current_appid()
            #xbmcvfs.copy(src, dest)

        elif machine == 'OSX64':
            url_ffprobe = 'https://github.com/DeBaschdi/packages/raw/master/ffprobe_osx64.zip'
            url_ffmpeg = 'https://github.com/DeBaschdi/packages/raw/master/ffmpeg_osx64.zip'

            ## Download ffprobe
            log("Downloading FFProbe.... " + url_ffprobe + ' to ' + runpath + 'ffprobe.zip', xbmc.LOGNOTICE)
            ffprobe_zip = requests.get(url_ffprobe)
            open(runpath + 'ffprobe.zip', 'wb').write(ffprobe_zip.content)

            ## Download ffmpeg
            log("Downloading FFMpeg.... " + url_ffmpeg + ' to ' + runpath + 'ffmpeg.zip', xbmc.LOGNOTICE)
            ffmpeg_zip = requests.get(url_ffmpeg)
            open(runpath + 'ffmpeg.zip', 'wb').write(ffmpeg_zip.content)

            ## Extract
            log("Extracting...", xbmc.LOGNOTICE)
            with ZipFile(runpath +'ffprobe.zip', 'r') as zipObj1:
                # Extract all the contents of zip file in different directory
                zipObj1.extractall(runpath)
            with ZipFile(runpath +'ffmpeg.zip', 'r') as zipObj2:
                # Extract all the contents of zip file in different directory
                zipObj2.extractall(runpath)
            pDialog.close()

def check_ffmpeg():
    if machine == 'AMD64':
        if os.path.isfile(runpath + 'ffmpeg.exe'):
            log("ffmpeg exist, skip installing", xbmc.LOGNOTICE)
        else:
            install_files()
        if os.path.isfile(runpath + 'ffprobe.exe'):
            log("ffprobe exist, skip installing", xbmc.LOGNOTICE)
        else:
            install_files()
    elif machine == 'aarch64':
        log("ffmpeg installing on Android is currently not supportet", xbmc.LOGNOTICE)
    else:
        if os.path.isfile(runpath + 'ffmpeg'):
            log("ffmpeg exist, skip installing", xbmc.LOGNOTICE)
        else:
            install_files()
        if os.path.isfile(runpath + 'ffprobe'):
            log("ffprobe exist, skip installing", xbmc.LOGNOTICE)
        else:
            install_files()
check_ffmpeg()

# Download Recording m3u from Telerising Server
def get_recordings():
    url = connection_mode + address + use_port + port + '/?file=recordings.m3u&bw='+ bandwith +'&platform=hls5&ffmpeg=true&profile='+ audio_profile
    log("Downloading recordings.m3u.... " + url + ' to ' + temppath + 'recordings.m3u', xbmc.LOGNOTICE)
    recordings = urllib.URLopener()
    recordings.retrieve( url, temppath + 'recordings.m3u')
get_recordings()

## Read m3u and Translate to Listitem ##
m3u8 = os.path.join(temppath, 'recordings.m3u')

# Create List
recordings = list()
with open(m3u8) as fo:
    lines = fo.readlines()

# Cleanup List, remove 1st Line (#EXTM3U)
lines.pop(0)

# Run through the remaining list in two lines (1st line #EXTINF, 2nd line link)
for i in range(0, len(lines), 2):
    parts = lines[i].split(',')  # Split before and after the comma, pull out infs
    (extinf, tvgid, grouptitle, tvglogo) = parts[0].split(' ')
    (showtime, title, channel) = parts[1].split(' | ')
    # pull m3u out of 2nd line
    ffmpeg_line = lines[i + 1].split('-i')[1]
    server = ffmpeg_line.split('index.m3u8')[0].replace(' ','').replace('"','')
    liz = xbmcgui.ListItem(label='%s %s' % (showtime, title), label2=channel)
    liz.setArt({'icon': tvglogo.split('=')[1].replace('"','')})
    liz.setProperties({'ffmpeg': ffmpeg_line, 'title': title, 'server': server})
    # Attach list item (ListItem) to list
    recordings.append(liz)

# Show List
dialog = xbmcgui.Dialog()
selected = dialog.select('Manage Cloud Recordings', recordings, useDetails=True)

# read Listitem
li = recordings[selected]
fo.close()

#Select Download / Play / Delete from Listitem
def manage_recordings():
    recording_title = li.getProperty('title').replace(' _ ',' ').decode('utf-8')
    src_movie = temppath + recording_title + '.ts'
    dest_movie = storage_path + recording_title + '.ts'
    ffmpeg_command = li.getProperty('ffmpeg').replace('pipe:1', '"' + src_movie + '"')
    recording_id = li.getProperty('ffmpeg').split('&bw')[0].split('recording=')[1]
    dialog = xbmcgui.Dialog()
    planned_string = '\[PLANNED\]'
    src_json = temppath + recording_title + '_src.json'
    dest_json = temppath + recording_title + '_dest.json'


    if re.search(planned_string,  li.getProperty('title').replace(' _ ',' ').decode('utf-8')):
        ret_cancel = dialog.yesno(li.getLabel() + ' ' + li.getLabel2(), 'Do you want to cancel this planned Recording?')
        ret = 'skipped'
    else:
        ret = dialog.select(li.getLabel() + ' ' + li.getLabel2(), ['Download', 'Play', 'Delete'])
        ret_cancel = False

    ## Download
    if ret == 0:
        if storage_path == 'choose':
            log('You need to setup an Storage Path First', xbmc.LOGERROR)
            notify(addon_name, 'You need to setup an Storage Path First',icon=xbmcgui.NOTIFICATION_ERROR)
            xbmc.sleep(5000)
            quit()
        else:
            log("Selectet Recording ID for Download = " + recording_id, xbmc.LOGNOTICE)
            if machine == 'aarch64':
                #ffmpegbin = '/data/data/%s/ffmpeg' % android_get_current_appid()
                #command = ffmpegbin + ' -i' + ffmpeg_command
                #log('command is ' + command , xbmc.LOGNOTICE)
                #process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
                #output = process.communicate()
                log('Downloading is corrently not supportet under Android Sorry...', xbmc.LOGNOTICE)
                notify(addon_name, 'Sorry, Downloading is corrently not supportet under Android ',icon=xbmcgui.NOTIFICATION_ERROR)

            elif machine == 'AMD64':
                ffmpegbin = '"' + runpath +  'ffmpeg.exe' + '"'
                ffprobebin = '"' + runpath + 'ffprobe.exe' + '"'
                percent = 100
                pDialog = xbmcgui.DialogProgressBG()
                pDialog.create('Downloading ' + recording_title + ' ' + quality, "%s Prozent verbleibend" % percent)
                probe_duration_src = ffprobebin + ' -v quiet -print_format json -show_format ' + '"' + connection_mode + address + use_port + port + '/index.m3u8?recording=' + recording_id + '&bw=' + bandwith + '&platform=hls5&profile=' + audio_profile + '"' + ' >' + ' "' + src_json + '"'
                subprocess.Popen(probe_duration_src , shell=True)
                xbmc.sleep(10000)
                retries = 10
                while retries > 0:
                    try:
                        with open(src_json, 'r') as f_src:
                            xbmc.sleep(3000)
                            src_status = json.load(f_src)
                            src_duration = src_status["format"].get("duration")
                        break
                    except (IOError, KeyError, AttributeError) as e:
                        xbmc.sleep(1000)
                        retries -= 1
                if retries == 0:
                    notify(addon_name, "Could not open Json SRC File")
                    log("Could not open Json SRC File", xbmc.LOGERROR)
                command = ffmpegbin + ' -y -i' + ffmpeg_command
                log('Started Downloading ' + recording_id, xbmc.LOGNOTICE)
                running_ffmpeg = [Popen(command, shell=True)]
                xbmc.sleep(10000)
                while running_ffmpeg:
                    for proc in running_ffmpeg:
                        retcode = proc.poll()
                        if retcode is not None:  # Process finished.
                            running_ffmpeg.remove(proc)
                            percent = 0
                            pDialog.update(100 - percent, 'Downloading ' + recording_title + ' ' + quality,"%s Prozent verbleibend" % percent)
                            xbmc.sleep(1000)
                            pDialog.close()
                            f_dest.close()
                            f_src.close()
                            log('finished Downloading ' + recording_id, xbmc.LOGNOTICE)
                            notify(addon_name, recording_title + " Download Finished", icon=xbmcgui.NOTIFICATION_INFO)

                            ## Copy Downloaded Files to Destination
                            #percent = 100
                            #src_size = xbmcvfs.Stat(src_movie).st_size()
                            cDialog = xbmcgui.DialogProgressBG()
                            #cDialog.create('Copy ' + recording_title + ' to Destination',"%s Prozent verbleibend" % percent)
                            cDialog.create('Copy ' + recording_title + ' to Destination',"Status is currently not supportet, please wait until finish")
                            xbmc.sleep(2000)
                            log('copy ' + recording_id + ' to Destination' , xbmc.LOGNOTICE)
                            notify(addon_name, 'Copy ' + recording_title + ' to Destiantion' , icon=xbmcgui.NOTIFICATION_INFO)
                            #copy_movie = xbmcvfs.copy(src_movie, dest_movie)
                            xbmcvfs.copy(src_movie, dest_movie)
                            #while copy_movie:
                            #    xbmc.sleep(2000)
                            #    dest_size = xbmcvfs.Stat(dest_movie).st_size()
                            #    log('size source is = ' + src_size, xbmc.LOGNOTICE)
                            #    log('size destination is = ' + dest_size, xbmc.LOGNOTICE)
                            #    log('copy ' + recording_id + ' to Destination', xbmc.LOGNOTICE)
                            #    percent = int(100) - int(dest_size) * int(100) / int(src_size)
                            #    cDialog.update(100 - percent, 'Copy ' + recording_title + ' to Destination', "%s Prozent verbleibend" % percent)
                            cDialog.close()

                            ## Delete all old Files
                            xbmcvfs.rmdir(temppath, force=True)
                            break
                    else:  # # Still Running
                        probe_duration_dest = ffprobebin + ' -v quiet -print_format json -show_format ' + '"' + src_movie + '"' +  ' >' + ' "' + dest_json + '"'
                        subprocess.Popen(probe_duration_dest , shell=True)
                        xbmc.sleep(7000)
                        retries = 10
                        while retries > 0:
                            try:
                                with open(dest_json, 'r') as f_dest:
                                    dest_status = json.load(f_dest)
                                    dest_duration = dest_status["format"].get("duration")
                                break
                            except (IOError, KeyError, AttributeError) as e:
                                xbmc.sleep(7000)
                                retries -= 1
                        if retries == 0:
                            notify(addon_name, "Could not open Json Dest File", icon=xbmcgui.NOTIFICATION_ERROR)
                            log("Could not open Json Dest File", xbmc.LOGERROR)
                        percent = int(100) - int(dest_duration.replace('.', '')) * int(100) / int(src_duration.replace('.', ''))
                        pDialog.update(100 - percent, 'Downloading ' + recording_title + ' ' + quality, "%s Prozent verbleibend" % percent)
                        continue
                f_dest.close()
                f_src.close()
                pDialog.close()

            elif machine == 'x86_64':
                ffmpegbin = runpath +  'ffmpeg'
                ffprobebin = runpath + 'ffprobe'
                percent = 100
                pDialog = xbmcgui.DialogProgressBG()
                pDialog.create('Downloading ' + recording_title + ' ' + quality, "%s Prozent verbleibend" % percent)
                probe_duration_src = ffprobebin + ' -v quiet -print_format json -show_format ' + '"' + connection_mode + address + use_port + port + '/index.m3u8?recording=' + recording_id + '&bw=' + bandwith + '&platform=hls5&profile=' + audio_profile + '"' + ' >' + ' "' + src_json + '"'
                subprocess.Popen(probe_duration_src , shell=True)
                xbmc.sleep(10000)
                retries = 10
                while retries > 0:
                    try:
                        with open(src_json, 'r') as f_src:
                            xbmc.sleep(3000)
                            src_status = json.load(f_src)
                            src_duration = src_status["format"].get("duration")
                        break
                    except (IOError, KeyError, AttributeError) as e:
                        xbmc.sleep(1000)
                        retries -= 1
                if retries == 0:
                    notify(addon_name, "Could not open Json SRC File")
                    log("Could not open Json SRC File", xbmc.LOGERROR)
                command = ffmpegbin + ' -y -i' + ffmpeg_command
                log('Started Downloading ' + recording_id, xbmc.LOGNOTICE)
                running_ffmpeg = [Popen(command, shell=True)]
                xbmc.sleep(10000)
                while running_ffmpeg:
                    for proc in running_ffmpeg:
                        retcode = proc.poll()
                        if retcode is not None:  # Process finished.
                            running_ffmpeg.remove(proc)
                            percent = 0
                            pDialog.update(100 - percent, 'Downloading ' + recording_title + ' ' + quality,"%s Prozent verbleibend" % percent)
                            xbmc.sleep(1000)
                            pDialog.close()
                            f_dest.close()
                            f_src.close()
                            log('finished Downloading ' + recording_id, xbmc.LOGNOTICE)
                            notify(addon_name, recording_title + " Download Finished", icon=xbmcgui.NOTIFICATION_INFO)

                            ## Copy Downloaded Files to Destination
                            #percent = 100
                            #src_size = xbmcvfs.Stat(src_movie).st_size()
                            cDialog = xbmcgui.DialogProgressBG()
                            #cDialog.create('Copy ' + recording_title + ' to Destination',"%s Prozent verbleibend" % percent)
                            cDialog.create('Copy ' + recording_title + ' to Destination',"Status is currently not supportet, please wait until finish")
                            xbmc.sleep(2000)
                            log('copy ' + recording_id + ' to Destination' , xbmc.LOGNOTICE)
                            notify(addon_name, 'Copy ' + recording_title + ' to Destiantion' , icon=xbmcgui.NOTIFICATION_INFO)
                            #copy_movie = xbmcvfs.copy(src_movie, dest_movie)
                            xbmcvfs.copy(src_movie, dest_movie)
                            #while copy_movie:
                            #    xbmc.sleep(2000)
                            #    dest_size = xbmcvfs.Stat(dest_movie).st_size()
                            #    log('size source is = ' + src_size, xbmc.LOGNOTICE)
                            #    log('size destination is = ' + dest_size, xbmc.LOGNOTICE)
                            #    log('copy ' + recording_id + ' to Destination', xbmc.LOGNOTICE)
                            #    percent = int(100) - int(dest_size) * int(100) / int(src_size)
                            #    cDialog.update(100 - percent, 'Copy ' + recording_title + ' to Destination', "%s Prozent verbleibend" % percent)
                            cDialog.close()

                            ## Delete all old Files
                            xbmcvfs.rmdir(temppath, force=True)
                            break
                    else:  # # Still Running
                        probe_duration_dest = ffprobebin + ' -v quiet -print_format json -show_format ' + '"' + src_movie + '"' +  ' >' + ' "' + dest_json + '"'
                        subprocess.Popen(probe_duration_dest , shell=True)
                        xbmc.sleep(7000)
                        retries = 10
                        while retries > 0:
                            try:
                                with open(dest_json, 'r') as f_dest:
                                    dest_status = json.load(f_dest)
                                    dest_duration = dest_status["format"].get("duration")
                                break
                            except (IOError, KeyError, AttributeError) as e:
                                xbmc.sleep(7000)
                                retries -= 1
                        if retries == 0:
                            notify(addon_name, "Could not open Json Dest File", icon=xbmcgui.NOTIFICATION_ERROR)
                            log("Could not open Json Dest File", xbmc.LOGERROR)
                        percent = int(100) - int(dest_duration.replace('.', '')) * int(100) / int(src_duration.replace('.', ''))
                        pDialog.update(100 - percent, 'Downloading ' + recording_title + ' ' + quality, "%s Prozent verbleibend" % percent)
                        continue
                f_dest.close()
                f_src.close()
                pDialog.close()

            elif machine == 'OSX64':
                ffmpegbin = runpath +  'ffmpeg'
                ffprobebin = runpath + 'ffprobe'
                percent = 100
                pDialog = xbmcgui.DialogProgressBG()
                pDialog.create('Downloading ' + recording_title + ' ' + quality, "%s Prozent verbleibend" % percent)
                probe_duration_src = ffprobebin + ' -v quiet -print_format json -show_format ' + '"' + connection_mode + address + use_port + port + '/index.m3u8?recording=' + recording_id + '&bw=' + bandwith + '&platform=hls5&profile=' + audio_profile + '"' + ' >' + ' "' + src_json + '"'
                subprocess.Popen(probe_duration_src , shell=True)
                xbmc.sleep(10000)
                retries = 10
                while retries > 0:
                    try:
                        with open(src_json, 'r') as f_src:
                            xbmc.sleep(3000)
                            src_status = json.load(f_src)
                            src_duration = src_status["format"].get("duration")
                        break
                    except (IOError, KeyError, AttributeError) as e:
                        xbmc.sleep(1000)
                        retries -= 1
                if retries == 0:
                    notify(addon_name, "Could not open Json SRC File")
                    log("Could not open Json SRC File", xbmc.LOGERROR)
                command = ffmpegbin + ' -y -i' + ffmpeg_command
                log('Started Downloading ' + recording_id, xbmc.LOGNOTICE)
                running_ffmpeg = [Popen(command, shell=True)]
                xbmc.sleep(10000)
                while running_ffmpeg:
                    for proc in running_ffmpeg:
                        retcode = proc.poll()
                        if retcode is not None:  # Process finished.
                            running_ffmpeg.remove(proc)
                            percent = 0
                            pDialog.update(100 - percent, 'Downloading ' + recording_title + ' ' + quality,"%s Prozent verbleibend" % percent)
                            xbmc.sleep(1000)
                            pDialog.close()
                            f_dest.close()
                            f_src.close()
                            log('finished Downloading ' + recording_id, xbmc.LOGNOTICE)
                            notify(addon_name, recording_title + " Download Finished", icon=xbmcgui.NOTIFICATION_INFO)

                            ## Copy Downloaded Files to Destination
                            #percent = 100
                            #src_size = xbmcvfs.Stat(src_movie).st_size()
                            cDialog = xbmcgui.DialogProgressBG()
                            #cDialog.create('Copy ' + recording_title + ' to Destination',"%s Prozent verbleibend" % percent)
                            cDialog.create('Copy ' + recording_title + ' to Destination',"Status is currently not supportet, please wait until finish")
                            xbmc.sleep(2000)
                            log('copy ' + recording_id + ' to Destination' , xbmc.LOGNOTICE)
                            notify(addon_name, 'Copy ' + recording_title + ' to Destiantion' , icon=xbmcgui.NOTIFICATION_INFO)
                            #copy_movie = xbmcvfs.copy(src_movie, dest_movie)
                            xbmcvfs.copy(src_movie, dest_movie)
                            #while copy_movie:
                            #    xbmc.sleep(2000)
                            #    dest_size = xbmcvfs.Stat(dest_movie).st_size()
                            #    log('size source is = ' + src_size, xbmc.LOGNOTICE)
                            #    log('size destination is = ' + dest_size, xbmc.LOGNOTICE)
                            #    log('copy ' + recording_id + ' to Destination', xbmc.LOGNOTICE)
                            #    percent = int(100) - int(dest_size) * int(100) / int(src_size)
                            #    cDialog.update(100 - percent, 'Copy ' + recording_title + ' to Destination', "%s Prozent verbleibend" % percent)
                            cDialog.close()

                            ## Delete all old Files
                            xbmcvfs.rmdir(temppath, force=True)
                            break
                    else:  # # Still Running
                        probe_duration_dest = ffprobebin + ' -v quiet -print_format json -show_format ' + '"' + src_movie + '"' +  ' >' + ' "' + dest_json + '"'
                        subprocess.Popen(probe_duration_dest , shell=True)
                        xbmc.sleep(7000)
                        retries = 10
                        while retries > 0:
                            try:
                                with open(dest_json, 'r') as f_dest:
                                    dest_status = json.load(f_dest)
                                    dest_duration = dest_status["format"].get("duration")
                                break
                            except (IOError, KeyError, AttributeError) as e:
                                xbmc.sleep(7000)
                                retries -= 1
                        if retries == 0:
                            notify(addon_name, "Could not open Json Dest File", icon=xbmcgui.NOTIFICATION_ERROR)
                            log("Could not open Json Dest File", xbmc.LOGERROR)
                        percent = int(100) - int(dest_duration.replace('.', '')) * int(100) / int(src_duration.replace('.', ''))
                        pDialog.update(100 - percent, 'Downloading ' + recording_title + ' ' + quality, "%s Prozent verbleibend" % percent)
                        continue
                f_dest.close()
                f_src.close()
                pDialog.close()

            elif machine == 'armv7l':
                ffmpegbin = runpath +  'ffmpeg'
                ffprobebin = runpath + 'ffprobe'
                percent = 100
                pDialog = xbmcgui.DialogProgressBG()
                pDialog.create('Downloading ' + recording_title + ' ' + quality, "%s Prozent verbleibend" % percent)
                probe_duration_src = ffprobebin + ' -v quiet -print_format json -show_format ' + '"' + connection_mode + address+ use_port + port + '/index.m3u8?recording=' + recording_id + '&bw=' + bandwith + '&platform=hls5&profile=' + audio_profile + '"' + ' >' + ' "' + src_json + '"'
                subprocess.Popen(probe_duration_src , shell=True)
                xbmc.sleep(10000)
                retries = 10
                while retries > 0:
                    try:
                        with open(src_json, 'r') as f_src:
                            xbmc.sleep(3000)
                            src_status = json.load(f_src)
                            src_duration = src_status["format"].get("duration")
                        break
                    except (IOError, KeyError, AttributeError) as e:
                        xbmc.sleep(1000)
                        retries -= 1
                if retries == 0:
                    notify(addon_name, "Could not open Json SRC File")
                    log("Could not open Json SRC File", xbmc.LOGERROR)
                command = ffmpegbin + ' -y -i' + ffmpeg_command
                log('Started Downloading ' + recording_id, xbmc.LOGNOTICE)
                running_ffmpeg = [Popen(command, shell=True)]
                xbmc.sleep(10000)
                while running_ffmpeg:
                    for proc in running_ffmpeg:
                        retcode = proc.poll()
                        if retcode is not None:  # Process finished.
                            running_ffmpeg.remove(proc)
                            percent = 0
                            pDialog.update(100 - percent, 'Downloading ' + recording_title + ' ' + quality,"%s Prozent verbleibend" % percent)
                            xbmc.sleep(1000)
                            pDialog.close()
                            f_dest.close()
                            f_src.close()
                            log('finished Downloading ' + recording_id, xbmc.LOGNOTICE)
                            notify(addon_name, recording_title + " Download Finished", icon=xbmcgui.NOTIFICATION_INFO)

                            ## Copy Downloaded Files to Destination
                            #percent = 100
                            #src_size = xbmcvfs.Stat(src_movie).st_size()
                            cDialog = xbmcgui.DialogProgressBG()
                            #cDialog.create('Copy ' + recording_title + ' to Destination',"%s Prozent verbleibend" % percent)
                            cDialog.create('Copy ' + recording_title + ' to Destination',"Status is currently not supportet, please wait until finish")
                            xbmc.sleep(2000)
                            log('copy ' + recording_id + ' to Destination' , xbmc.LOGNOTICE)
                            notify(addon_name, 'Copy ' + recording_title + ' to Destiantion' , icon=xbmcgui.NOTIFICATION_INFO)
                            #copy_movie = xbmcvfs.copy(src_movie, dest_movie)
                            xbmcvfs.copy(src_movie, dest_movie)
                            #while copy_movie:
                            #    xbmc.sleep(2000)
                            #    dest_size = xbmcvfs.Stat(dest_movie).st_size()
                            #    log('size source is = ' + src_size, xbmc.LOGNOTICE)
                            #    log('size destination is = ' + dest_size, xbmc.LOGNOTICE)
                            #    log('copy ' + recording_id + ' to Destination', xbmc.LOGNOTICE)
                            #    percent = int(100) - int(dest_size) * int(100) / int(src_size)
                            #    cDialog.update(100 - percent, 'Copy ' + recording_title + ' to Destination', "%s Prozent verbleibend" % percent)
                            cDialog.close()

                            ## Delete all old Files
                            xbmcvfs.rmdir(temppath, force=True)
                            break
                    else:  # # Still Running
                        probe_duration_dest = ffprobebin + ' -v quiet -print_format json -show_format ' + '"' + src_movie + '"' +  ' >' + ' "' + dest_json + '"'
                        subprocess.Popen(probe_duration_dest , shell=True)
                        xbmc.sleep(7000)
                        retries = 10
                        while retries > 0:
                            try:
                                with open(dest_json, 'r') as f_dest:
                                    dest_status = json.load(f_dest)
                                    dest_duration = dest_status["format"].get("duration")
                                break
                            except (IOError, KeyError, AttributeError) as e:
                                xbmc.sleep(7000)
                                retries -= 1
                        if retries == 0:
                            notify(addon_name, "Could not open Json Dest File", icon=xbmcgui.NOTIFICATION_ERROR)
                            log("Could not open Json Dest File", xbmc.LOGERROR)
                        percent = int(100) - int(dest_duration.replace('.', '')) * int(100) / int(src_duration.replace('.', ''))
                        pDialog.update(100 - percent, 'Downloading ' + recording_title + ' ' + quality, "%s Prozent verbleibend" % percent)
                        continue
                f_dest.close()
                f_src.close()
                pDialog.close()

            elif machine == 'armv8l':
                ffmpegbin = runpath +  'ffmpeg'
                ffprobebin = runpath + 'ffprobe'
                percent = 100
                pDialog = xbmcgui.DialogProgressBG()
                pDialog.create('Downloading ' + recording_title + ' ' + quality, "%s Prozent verbleibend" % percent)
                probe_duration_src = ffprobebin + ' -v quiet -print_format json -show_format ' + '"' + connection_mode + address + use_port + port + '/index.m3u8?recording=' + recording_id + '&bw=' + bandwith + '&platform=hls5&profile=' + audio_profile + '"' + ' >' + ' "' + src_json + '"'
                subprocess.Popen(probe_duration_src , shell=True)
                xbmc.sleep(10000)
                retries = 10
                while retries > 0:
                    try:
                        with open(src_json, 'r') as f_src:
                            xbmc.sleep(3000)
                            src_status = json.load(f_src)
                            src_duration = src_status["format"].get("duration")
                        break
                    except (IOError, KeyError, AttributeError) as e:
                        xbmc.sleep(1000)
                        retries -= 1
                if retries == 0:
                    notify(addon_name, "Could not open Json SRC File")
                    log("Could not open Json SRC File", xbmc.LOGERROR)
                command = ffmpegbin + ' -y -i' + ffmpeg_command
                log('Started Downloading ' + recording_id, xbmc.LOGNOTICE)
                running_ffmpeg = [Popen(command, shell=True)]
                xbmc.sleep(10000)
                while running_ffmpeg:
                    for proc in running_ffmpeg:
                        retcode = proc.poll()
                        if retcode is not None:  # Process finished.
                            running_ffmpeg.remove(proc)
                            percent = 0
                            pDialog.update(100 - percent, 'Downloading ' + recording_title + ' ' + quality,"%s Prozent verbleibend" % percent)
                            xbmc.sleep(1000)
                            pDialog.close()
                            f_dest.close()
                            f_src.close()
                            log('finished Downloading ' + recording_id, xbmc.LOGNOTICE)
                            notify(addon_name, recording_title + " Download Finished", icon=xbmcgui.NOTIFICATION_INFO)

                            ## Copy Downloaded Files to Destination
                            #percent = 100
                            #src_size = xbmcvfs.Stat(src_movie).st_size()
                            cDialog = xbmcgui.DialogProgressBG()
                            #cDialog.create('Copy ' + recording_title + ' to Destination',"%s Prozent verbleibend" % percent)
                            cDialog.create('Copy ' + recording_title + ' to Destination',"Status is currently not supportet, please wait until finish")
                            xbmc.sleep(2000)
                            log('copy ' + recording_id + ' to Destination' , xbmc.LOGNOTICE)
                            notify(addon_name, 'Copy ' + recording_title + ' to Destiantion' , icon=xbmcgui.NOTIFICATION_INFO)
                            #copy_movie = xbmcvfs.copy(src_movie, dest_movie)
                            xbmcvfs.copy(src_movie, dest_movie)
                            #while copy_movie:
                            #    xbmc.sleep(2000)
                            #    dest_size = xbmcvfs.Stat(dest_movie).st_size()
                            #    log('size source is = ' + src_size, xbmc.LOGNOTICE)
                            #    log('size destination is = ' + dest_size, xbmc.LOGNOTICE)
                            #    log('copy ' + recording_id + ' to Destination', xbmc.LOGNOTICE)
                            #    percent = int(100) - int(dest_size) * int(100) / int(src_size)
                            #    cDialog.update(100 - percent, 'Copy ' + recording_title + ' to Destination', "%s Prozent verbleibend" % percent)
                            cDialog.close()

                            ## Delete all old Files
                            xbmcvfs.rmdir(temppath, force=True)
                            break
                    else:  # # Still Running
                        probe_duration_dest = ffprobebin + ' -v quiet -print_format json -show_format ' + '"' + src_movie + '"' +  ' >' + ' "' + dest_json + '"'
                        subprocess.Popen(probe_duration_dest , shell=True)
                        xbmc.sleep(7000)
                        retries = 10
                        while retries > 0:
                            try:
                                with open(dest_json, 'r') as f_dest:
                                    dest_status = json.load(f_dest)
                                    dest_duration = dest_status["format"].get("duration")
                                break
                            except (IOError, KeyError, AttributeError) as e:
                                xbmc.sleep(7000)
                                retries -= 1
                        if retries == 0:
                            notify(addon_name, "Could not open Json Dest File", icon=xbmcgui.NOTIFICATION_ERROR)
                            log("Could not open Json Dest File", xbmc.LOGERROR)
                        percent = int(100) - int(dest_duration.replace('.', '')) * int(100) / int(src_duration.replace('.', ''))
                        pDialog.update(100 - percent, 'Downloading ' + recording_title + ' ' + quality, "%s Prozent verbleibend" % percent)
                        continue
                f_dest.close()
                f_src.close()
                pDialog.close()

    ## Play
    if ret == 1:
        url = connection_mode + address + use_port + port + '/index.m3u8?recording=' + recording_id + '&bw=' + bandwith + '&platform=hls5&ffmpeg=true&profile=' + audio_profile
        log("Opening Recording " + recording_id + " for direct Play", xbmc.LOGNOTICE)
        xbmc.Player().play(url, li)

    ## Delete
    if ret == 2 or ret_cancel == True:
        log("Selectet Recording ID for Delete = "  + recording_id, xbmc.LOGNOTICE)
        url = connection_mode + address + use_port + port + '/index.m3u8?recording=' + recording_id + '&remove=true'
        log("Selectet Recording ID for Delete = " + url, xbmc.LOGNOTICE)
        xbmc.sleep(1000)
        notify(addon_name, "Deleting " + recording_title + ' from Cloud ...')
        xbmc.sleep(5000)
        delete_recording = urllib.URLopener()
        delete_recording.retrieve(url, runpath +'urlrequest.txt')
        retries = 5
        while retries > 0:
            try:
                f = open(runpath +'urlrequest.txt', 'r')
                file_contents = f.read()
                break
            except IOError as e:
                xbmc.sleep(1000)
                retries -= 1
        if retries == 0:
            notify(addon_name, "ERROR, Could not open urlrequest.txt")
            log("ERROR, Could not open urlrequest.txt", xbmc.LOGERROR)

        ## Check if Recording is successfull removed
        removed_string = "Recording removed"
        error_string = "ERROR"
        if re.search(removed_string, file_contents):
            notify(addon_name, "SUCCESS: " + recording_title + ' removed')
            log("SUCCESS: Recording " + recording_id + ' removed', xbmc.LOGNOTICE)
            f.close
        if re.search(error_string, file_contents):
            notify(addon_name, "ERROR: " + recording_title + 'can not be removed')
            log("SUCCESS: Recording " + recording_id + ' removed', xbmc.LOGERROR)
            f.close
        f.close
    ## Cancel
    if ret_cancel == False:
        print 'cancel'
if selected > -1:
    manage_recordings()