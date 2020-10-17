#!/usr/bin/env python3

# 'NewsOnAir: Prasar Bharati Official App' uses the best audio source.
# Internally it fetches the audio source URLs from the following API:
#
# http://prasarbharati.org/pb/code/index.php/channels/getRadioChannels
# http://prasarbharati.org/pb/code/index.php/channels (jackpot!)
#
# Last modified: 26-May-2021 (dhiru).

import re
import sys
import string
import subprocess

import evdev
import requests
from pyquery import PyQuery as pq


def discover_youtube_url():
    s = requests.Session()
    url = "https://www.vividhbharti.org/"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'}

    r = s.get(url, headers=headers)

    d = pq(r.text)
    # print(d)

    youtube_url = None
    links = d("iframe")
    for link in links:
        src = link.get("src")
        if src.startswith("https://www.youtube.com"):
            youtube_url = src

    print(youtube_url)

    return youtube_url

def run(cmd):
    subprocess.run(cmd, shell=True)


def stop():
    command = "killall mpv; killall vlc; sleep 0.5"
    run(command)

def announce(text):
    command = """espeak '%s'""" % text
    run(command)


def volume_up():
    # text = "OK"
    # announce(text)

    # command = """amixer set 'Master' 5%+"""
    command = """amixer set 'Digital' unmute"""
    run(command)
    command = """amixer set 'Digital' 2%+"""
    run(command)


def volume_down():
    # text = "OK"
    # announce(text)

    # command = """amixer set 'Master' 5%-"""
    command = """amixer set 'Digital' 2%-"""
    run(command)


def pause():
    command = """amixer set 'Digital' toggle"""
    run(command)


def play_radio(text, url):
    stop()

    announce(text)

    # command = """screen -dmS mpv mpv %s""" % url
    command = """screen -dmS vlc cvlc '%s'""" % url
    run(command)


radio_streams = {
        "air": {
            # 'text': 'All India Radio', 'url': discover_youtube_url(),
            'text': 'All India Radio', 'url': "https://radioindia.net/radio/vividhbharti/icecast.audio",
            # 'text': 'All India Radio', 'url': 'http://vividhbharati-lh.akamaihd.net/i/vividhbharati_1@507811/master.m3u8'
        },
        "air_backup": {
            # Has occasional hiccups...
            # [ffmpeg] http: HTTP error 404 Not Found
            # [ffmpeg/demuxer] hls: Failed to open segment 2630 of playlist...
            'text': 'All India Radio Backup', 'url': 'http://air.pc.cdn.bitgravity.com/air/live/pbaudio001/playlist.m3u8',
            'comment': 'Sniffed from "NewsOnAir Prasar Bharati Official App"',
            "comment2": 'https://vividhbharati-lh.akamaihd.net/i/vividhbharati_1@507811/index_1_a-p.m3u8',
        },

        "bigfm": {
            'text': 'Big FM', 'url': 'https://radioindia.net/radio/sc-bb/icecast.audio',
        },

        "ceylon": {
            'text': 'Radio Ceylon', 'url': 'http://220.247.227.6:8000/Asiastream',
        },

        "bbc_ws": {
            'text': 'BBC World Service', 'url': 'http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_world_service_south_asia.m3u8',
        },

        "wqxr": {
            'text': 'WQXR New York', 'url': 'https://www.wqxr.org/stream/wqxr/aac.pls',
        },
}

def shutdown():
    stop()

    text = "Shutting down the system. Good bye!"
    announce(text)

    command = "sudo poweroff"
    run(command)


"""
Layout of the "Car MP3 remote":

References:

- http://www.geeetech.com/wiki/index.php/Arduino_IR_Remote_Control
- https://gist.github.com/steakknife/e419241095f1272ee60f5174f7759867

   ------------------
 /                    \
|  CH-    CH     CH+   |
| FFA25D FF629D FFE21D |
|                      |
|  |<<     >>|   |>||  |
| FF22DD FF02FD FFC23D |
|                      |
|   -       +     EQ   |
| FFE01F FFA857 FF906F |
|                      |
|   0      100+  200+  |
| FF6897 FF9867 FFB04F |
|                      |
|   1       2     3    |
| FF30CF FF18E7 FF7A85 |
|                      |
|   4       5     6    |
| FF10EF FF38C7 FF5AA5 |
|                      |
|   7       8     9    |
| FF42BD FF4AB5 FF52AD |
|                      |
|         Car          |
|         mp3          |
 \                    /
   ------------------
(FFFFFFFF for repeat when a button is held)
"""

# IR codes for the "Car MP3" remote control
shutdown_code = "FF9867"
codes_to_actions = {
        "FF6897": "radio_air",
        "FF30CF": "radio_bbc_ws",
        "FF18E7": "radio_air_backup",
        "FF7A85": "radio_bigfm",
        "FF10EF": "radio_ceylon",
        "FF52AD": "radio_wqxr",
        shutdown_code: shutdown,
        "FFC23D": pause,
        "FFE01F": volume_down,
        "FFA857": volume_up,
}

# Note
code_pattern = r'FF.{4}?'

codes = list(codes_to_actions.keys())
print(codes_to_actions, codes)

valid_chars = string.digits + string.ascii_uppercase
line = ""

# boot stuff
command = """amixer set 'Digital' unmute"""
run(command)
text = "Device is ready now!"
announce(text)

selected_radio_stream = radio_streams["air_backup"]
# selected_radio_stream = radio_streams["air"]
play_radio(selected_radio_stream["text"], selected_radio_stream["url"])

device = evdev.InputDevice('/dev/input/by-id/usb-Adafruit_Trinket_HID_Combo-event-kbd')

shutdown_count = 0

for event in device.read_loop():
    if event.type == evdev.ecodes.EV_KEY:
        # print((evdev.categorize(event).keycode))
        # print((evdev.categorize(event).scancode))
        if event.value == 1:
            data = evdev.categorize(event)
            key = None
            try:
                key = (data.keycode).split("_")[1]
            except:
                pass
            if key in valid_chars:
                line = line + key

            # matching code
            r = re.search(code_pattern, line)
            if r:
                print(r.group())
                line = ""
                action = codes_to_actions.get(r.group(), None)
                if isinstance(action, str) and action.startswith("radio_"):  # hack for radio stations!
                    key = action.replace("radio_", "")
                    selected_radio_stream = radio_streams[key]
                    print(selected_radio_stream)
                    play_radio(selected_radio_stream["text"], selected_radio_stream["url"])
                    continue
                print(r.group(), action)
                if r.group() == shutdown_code:
                    shutdown_count = shutdown_count + 1
                    if shutdown_count == 3:
                        action()
                else:
                    shutdown_count = 0
                if action:
                    action()
