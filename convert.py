#! /usr/bin/python3

import subprocess
import http.client, urllib
import json
import argparse
import os
import time

src_dir = '/mnt/storage/shared/Captures/Raw/'
dest_dir = '/mnt/external/media/Library/Home Videos/'

def pushover(message):
    with open('pushover.json') as f:
        params = json.load(f)

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": params['token'],
                "user": params['user'],
                "message": message,
                }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

#/mnt/storage/shared/Captures/Raw/002.dv 
#/mnt/external/media/Library/Home Videos/002.m4v
def convert(in_path, out_path):
    command = 'HandBrakeCLI --preset-import-file ./home.json -Z "HomeVideo" -i "%s" -o "%s"' % (in_path, out_path)
    #result = subprocess.call(command, shell=True)
    #result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    #proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    #result = proc.communicate()

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except Exception as e:
        output = str(e.output)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('id', type=int, help='video to convert')
    args = parser.parse_args()

    id = str(args.id).zfill(3)

    if os.path.exists(src_dir + id + '.avi'):
        in_path = src_dir + id + '.avi'
    elif os.path.exists(src_dir + id + '.dv'):
        in_path = src_dir + id + '.dv'
    else:
        print('File not found')
        exit(1)

    out_path = dest_dir + id + '.m4v'

    pushover('Starting conversion of %s' % (in_path))
    
    start_time = time.time()
    result = convert(in_path, out_path)
    end_time = time.time()
    total_time = end_time - start_time

    if 'Encode done!' in str(result):
        pushover('Finished conversion of video %s after %d seconds' % (id, total_time))
    else:
        pushover('Error: converstion of video %s failed\n\nFull output:\n%s' % (id, str(result)))
