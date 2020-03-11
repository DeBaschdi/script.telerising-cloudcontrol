import os
import platform
import subprocess
from subprocess import Popen
import re
import xbmc
import xbmcaddon
import xbmcgui
import json
import requests
import xbmcvfs
from zipfile import ZipFile
import glob

ADDON = xbmcaddon.Addon(id="script.telerising-cloudcontrol")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
addonpath = xbmc.translatePath(ADDON.getAddonInfo('path'))
runpath = os.path.join(datapath, "bin")
temppath = os.path.join(datapath, "temp")
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
def create_folders():
    # deal with bug that happens if the datapath not exist
    if not os.path.exists(runpath):
        os.makedirs(runpath, mode=0o777)
    if not os.path.exists(temppath):
        os.makedirs(temppath, mode=0o777)
create_folders()

def delete_tempfiles():
    trash = glob.glob(os.path.join(temppath, '*'))
    for f in trash:
        os.remove(f)

## Create definitions depending on the machine type
if machine == 'x86_64':
    url_ffprobe = 'https://github.com/DeBaschdi/packages/raw/master/ffprobe_x86_64.zip'
    url_ffmpeg = 'https://github.com/DeBaschdi/packages/raw/master/ffmpeg_x86_64.zip'
    ffmpeg = os.path.join(runpath, 'ffmpeg')
    ffprobe = os.path.join(runpath, 'ffprobe')
elif machine == 'AMD64':
    url_ffprobe = 'https://github.com/DeBaschdi/packages/raw/master/ffprobe_amd64.zip'
    url_ffmpeg = 'https://github.com/DeBaschdi/packages/raw/master/ffmpeg_amd64.zip'
    ffmpeg = os.path.join(runpath, 'ffmpeg.exe')
    ffprobe = os.path.join(runpath, 'ffprobe.exe')
elif machine == 'armv7l':
    url_ffprobe = 'https://github.com/DeBaschdi/packages/raw/master/ffprobe_arm32.zip'
    url_ffmpeg = 'https://github.com/DeBaschdi/packages/raw/master/ffmpeg_arm32.zip'
    ffmpeg = os.path.join(runpath, 'ffmpeg')
    ffprobe = os.path.join(runpath, 'ffprobe')
elif machine == 'armv8l':
    url_ffprobe = 'https://github.com/DeBaschdi/packages/raw/master/ffprobe_arm64.zip'
    url_ffmpeg = 'https://github.com/DeBaschdi/packages/raw/master/ffmpeg_arm64.zip'
    ffmpeg = os.path.join(runpath, 'ffmpeg')
    ffprobe = os.path.join(runpath, 'ffprobe')
elif machine == 'OSX64':
    url_ffprobe = 'https://github.com/DeBaschdi/packages/raw/master/ffprobe_osx64.zip'
    url_ffmpeg = 'https://github.com/DeBaschdi/packages/raw/master/ffmpeg_osx64.zip'
    ffmpeg = os.path.join(runpath, 'ffmpeg')
    ffprobe = os.path.join(runpath, 'ffprobe')
elif machine == 'aarch64':
    Dummy = 'dummy'

# Install needed Files
def install_files():
    if machine_type() == True:
        #notify(addon_name, 'Installing ffmpeg...',icon=xbmcgui.NOTIFICATION_INFO)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(addon_name, 'Download ffprobe...')
        ## Download ffprobe
        ffprobe_zip_location = os.path.join(runpath, 'ffprobe.zip')
        log("Downloading FFProbe.... " + url_ffprobe + ' to ' + ffprobe_zip_location, xbmc.LOGNOTICE)
        download_ffprobe = requests.get(url_ffprobe)
        open(ffprobe_zip_location, 'wb').write(download_ffprobe.content)

        ## Download ffmpeg
        pDialog.update(33, 'Download ffmpeg...')
        ffmpeg_zip_location = os.path.join(runpath, 'ffmpeg.zip')
        log("Downloading FFMpeg.... " + url_ffmpeg + ' to ' + ffmpeg_zip_location, xbmc.LOGNOTICE)
        download_ffmpeg = requests.get(url_ffmpeg)
        open(ffmpeg_zip_location, 'wb').write(download_ffmpeg.content)

        ## Extract
        pDialog.update(66, 'Extract ffprobe...')
        log("Extracting... " + ffprobe_zip_location, xbmc.LOGNOTICE)
        with ZipFile(ffprobe_zip_location, 'r') as zipObj1:
            # Extract all the contents of zip file in different directory
            zipObj1.extractall(runpath)

        xbmc.sleep(1000)
        pDialog.update(99, 'Extract ffmpeg...')
        log("Extracting... " + ffmpeg_zip_location, xbmc.LOGNOTICE)
        with ZipFile(ffmpeg_zip_location, 'r') as zipObj2:
            # Extract all the contents of zip file in different directory
            zipObj2.extractall(runpath)
        xbmc.sleep(1000)

        ## Set Premissions
        rights = "chmod 777 -R " + runpath
        subprocess.Popen(rights, shell=True)

        pDialog.close()

def check_ffmpeg():
    if machine == 'aarch64':
        log("ffmpeg installing on Android is currently not supportet", xbmc.LOGNOTICE)
    else :
        if xbmcvfs.exists(ffmpeg):
            log("ffmpeg exist, skip installing", xbmc.LOGNOTICE)
        else:
            install_files()
        if xbmcvfs.exists(ffprobe):
            log("ffprobe exist, skip installing", xbmc.LOGNOTICE)
        else:
            install_files()
check_ffmpeg()

# Download Recording m3u from Telerising Server
recordings_m3u = os.path.join(temppath, 'recordings.m3u')
def get_recordings():
    url = connection_mode + address + use_port + port + '/?file=recordings.m3u&bw='+ bandwith +'&platform=hls5&ffmpeg=true&profile='+ audio_profile
    log("Downloading recordings.m3u.... " + url + ' to ' + recordings_m3u, xbmc.LOGNOTICE)
    download_m3u = requests.get(url)
    open(recordings_m3u, 'wb').write(download_m3u.content)
get_recordings()


## Read m3u and Translate to Listitem ##

# Create List
recordings = list()
with open(recordings_m3u) as fo:
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

## Properity Definitions
recording_id = li.getProperty('ffmpeg').split('&bw')[0].split('recording=')[1]
recording_property = li.getProperty('title').decode("utf-8")
recording_title = recording_property.replace('_', '-')
src_json = xbmc.makeLegalFilename(os.path.join(temppath, recording_id + '_src.json'))
dest_json = xbmc.makeLegalFilename(os.path.join(temppath, recording_id + '_dest.json'))
src_movie = xbmc.makeLegalFilename(os.path.join(temppath, recording_id + '.ts'))
dest_movie = xbmc.makeLegalFilename(os.path.join(storage_path, recording_title + '.ts').encode('utf-8'))
ffmpeg_properity = li.getProperty('ffmpeg').replace('pipe:1', '"' + src_movie + '"')
ffmpeg_command = '"' + connection_mode + address + use_port + port + '/index.m3u8' + ffmpeg_properity.split('index.m3u8')[1]
planned_string = '\[PLANNED\]'

def move_to_destination():
    ## Copy Downloaded Files to Destination
    if xbmcvfs.exists(src_movie):

        cDialog = xbmcgui.DialogProgressBG()
        cDialog.create('Copy ' + recording_title + ' to Destination',"Status is currently not supportet, please wait until finish")
        xbmc.sleep(2000)
        log('copy ' + src_movie + ' to Destination', xbmc.LOGNOTICE)
        notify(addon_name, 'Copy ' + recording_title + ' to Destiantion', icon=xbmcgui.NOTIFICATION_INFO)
        done = xbmcvfs.copy(src_movie, dest_movie)
        cDialog.close()

        ## Delete all old Files if the copyrprocess was successful
        if done == True:
            log(recording_id + ' has been copied', xbmc.LOGNOTICE)
            notify(addon_name, recording_id + ' has been copied', icon=xbmcgui.NOTIFICATION_INFO)
            delete_tempfiles()
        else:
            log(recording_id + ' cannot be copied', xbmc.LOGERROR)
            notify(addon_name, recording_id + ' cannot be copied', icon=xbmcgui.NOTIFICATION_ERROR)
    else:
        notify(addon_name, "Could not open " + src_movie, icon=xbmcgui.NOTIFICATION_ERROR)
        log("Could not open " + src_movie, xbmc.LOGERROR)

#Select Download / Play / Delete from Listitem
def manage_recordings():
    dialog = xbmcgui.Dialog()
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
                log('Downloading is corrently not supportet under Android Sorry...', xbmc.LOGNOTICE)
                notify(addon_name, 'Sorry, Downloading is corrently not supportet under Android ',icon=xbmcgui.NOTIFICATION_ERROR)

            else:
                ffmpegbin = '"' + ffmpeg + '"'
                ffprobebin = '"' + ffprobe + '"'
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
                    notify(addon_name, "Could not open Json SRC File", icon=xbmcgui.NOTIFICATION_ERROR)
                    log("Could not open Json SRC File", xbmc.LOGERROR)
                command = ffmpegbin + ' -y -i ' + ffmpeg_command
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
                            xbmc.sleep(3000)
                            f_dest.close()
                            f_src.close()
                            pDialog.close()
                            move_to_destination()

                    else:  # # Still Running
                        probe_duration_dest = ffprobebin + ' -v quiet -print_format json -show_format ' + '"' + src_movie + '"' +  ' >' + ' "' + dest_json + '"'
                        subprocess.Popen(probe_duration_dest , shell=True)
                        xbmc.sleep(7000)
                        retries = 10
                        while retries > 0:
                            try:
                                xbmc.sleep(3000)
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

        urlrequest_location = os.path.join(temppath, 'urlrequest.txt')
        delete_recording = requests.get(url)
        open(urlrequest_location, 'wb').write(delete_recording.content)

        retries = 5
        while retries > 0:
            try:
                f = open(urlrequest_location, 'r')
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
        if re.search(error_string, file_contents):
            notify(addon_name, "ERROR: " + recording_title + 'can not be removed')
            log("SUCCESS: Recording " + recording_id + ' removed', xbmc.LOGERROR)
        f.close
    ## Cancel
    if ret_cancel == False:
        dummy2 = 'cancel'
if selected > -1:
    manage_recordings()