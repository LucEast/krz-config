#!/usr/bin/env python3

import os
import csv
import sys
import speedtest
import time
from threading import Thread


packages = 'freeradius freeradius-common freeradius-config freeradius-postgresql freeradius-utils freetds-common incron iserv-booking iserv-docker-libreoffice-online iserv-docker-libreoffice-online-data iserv-office iserv-poll iserv-schedule iserv-server-freeradius iserv-server-incron iserv-videoconference iserv-wlan iserv3-timetable libct4 libfreeradius3 iserv3-report krz-lemgo-remote-support'
groups = 'krz'


try:
    import psycopg2
except:
    print('Install requirements with "pip3 install -r requirements.txt')
    quit()


def question(question):
    """Simple question Function."""
    prompt = f'{question} ?: '
    ans = input(prompt)
    return ans


def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def test_download():
    global ds
    st = speedtest.Speedtest()
    ds = st.download()


def spinning_cursor():
    while True:
        for cursor in '|/–\\':
            yield cursor


def install_packages(packages):
    os.system('apt install ' + packages)


def creategroups(groups):
    try:
        os.system('iservgroupadd ' + groups)
    except Exception as e:
        print(e)


def load_speedtest():
    thread = Thread(target=test_download)
    thread.start()
    spinner = spinning_cursor()
    sys.stdout.write('Testing download speed. ')
    while(thread.is_alive()):
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    sys.stdout.write('\b' * 24)
    # Readable
    print('\nDownload speed: ' + humansize(ds) + '\n')


def sysconf():
    # Read in the File
    with open('/etc/iserv/config', 'r') as config:
        data = config.read()

    # Replace
    data = data.replace('Region = ""', 'Region = "de_NW"')
    data = data.replace('DHCP = ("*")', 'DHCP = ("' +
                        question('Please enter internal NIC') + '")')
    if ds > 100000000:
        data = data.replace('WindowsupdateProxyMaxDownloaders = 3',
                            'WindowsupdateProxyMaxDownloaders = 50')
    else:
        data = data.replace('WindowsupdateProxyMaxDownloaders = 3',
                            'WindowsupdateProxyMaxDownloaders = 15')
    data = data.replace('DeployApplyAutoUpdates = false',
                        'DeployApplyAutoUpdates = true')
    data = data.replace('PrintDefault = true', 'PrintDefault = false')
    data = data.replace('PrintDirectEnable = flase',
                        'PrintDirectEnable = true')
    data = data.replace('GrpVeyon = "lehrer"', 'GrpVeyon = "kollegium"')

    # Write changes to file
    with open('/etc/iserv/config', 'w') as config:
        config.write(data)

    print('Succesfully applied changes to system configuration.\n\n')


def update_db():
    print('Updating Database...')
    conn = psycopg2.connect("dbname=iserv user=postgres")
    cur = conn.cursor()
    with open('privileges.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # skips the header row.
        try:
            for row in reader:
                cur.execute(
                    "INSERT INTO privileges_assign VALUES (%s, %s)", row)
        except Exception as e:
            print(e)
    conn.commit()
    conn.close()


install_packages(packages)
creategroups(groups)
load_speedtest()
sysconf()
update_db()
