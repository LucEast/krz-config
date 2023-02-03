#!/usr/bin/env python3

import os
import csv
import sys
import speedtest
import time
from threading import Thread

try:
    import psycopg2
except:
    print('Install requirements with "pip3 install -r requirements.txt')
    quit()

try:
    import inquirer
    from inquirer.themes import GreenPassion
    import inquirer.errors
except:
    print('Install requirements with "pip3 install -r requirements.txt')
    quit()


# Create checkbox prompt with desired options
def checkbox():
    try:
        questions = [inquirer.Checkbox('options',
                        message="What do you want to run?",
                        choices=["Install packages", "Update privileges", "Create Import-Profiles", "Create Groups", "Update Sysconf", "Deny Websites"],
                        # default choices 
                        default=["Install packages", "Update privileges", "Create Import-Profiles", "Create Groups", "Update Sysconf", "Deny Websites"]),
                    ]
        answers = inquirer.prompt(questions, theme=GreenPassion())['options']
    except KeyboardInterrupt:
        sys.exit(0)
    return answers


# Function to install apt packages
def install_packages(packages):
    os.system('apt install ' + packages)

# Function to create the groups
def creategroups(groups):
    try:
        for group in groups: # for every group in var "groups" add group
            os.system('iservgroupadd ' + group)
            print(f"Added group {group}")
    except Exception as e:
        print(e)

# Database class containing the table name
class Database:
    def __init__(self, table):
        self.table = table

    # function to update 'privileges_assign' table in psql
    def update_privileges(self):
        print('Updating Database...')
        conn = psycopg2.connect("dbname=iserv user=postgres") # connecting to psql
        cur = conn.cursor()
        with open('privileges.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';') # read in 'privileges.csv' 
            next(reader)  # skips the header row.
            try:
                for row in reader: # for each row
                    cur.execute(
                        "INSERT INTO %s VALUES (%s, %s)", [self.table, row]) 
            except Exception as e:
                print(e)
        conn.commit() # commit changes
        cur.close()
        conn.close() # close connection

    # function to create the import-profiles in IServ
    def import_profile(self, file):
        print("Creating Import-Profiles...")
        if os.path.exists(file): # check if 'import_profile.sql' exists
            try:
                conn = psycopg2.connect("dbname=iserv user=postgres")
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, name from import_profile WHERE id <= 2 OR name = 'Schüler' OR name = 'Lehrer'")
                rows = cur.fetchall()

                if not rows:  
                    os.system('psql -f ' + file) # if table 'import_profile' doesn't contain 'Schüler' or 'Lehrer' or any id <= 2 import 'import_profile.sql'
                else:
                    with open(file, 'r') as f:
                        for line in f:
                            try:
                                cur.execute(line) # if table 'import_profile' contain something, try to execute one profile after each other.
                            except Exception as e: 
                                print(e)
                                conn.rollback() # if error occurs because profile already exists -> rollback database. 
                                pass
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print(e)
        else:
            print(file + ' does not exist.')

# Simple question function
def question(question):
    prompt = f'{question}: '
    ans = input(prompt)
    return ans

# make bytes human readable
def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

# function to evaluate download speed
def test_download():
    global ds
    st = speedtest.Speedtest()
    ds = st.download() # stores downloadspeed in var ds

# just a loading screen to make sure script still running
def spinning_cursor():
    while True:
        for cursor in '|/–\\':
            yield cursor

# function to show the spinning cursor while testing download speed
def load_speedtest():
    thread = Thread(target=test_download) # start function 'test_download' as thread
    thread.start()
    spinner = spinning_cursor()
    sys.stdout.write('Testing download speed. ')
    while(thread.is_alive()):
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    sys.stdout.write('\b' * 24)
    print('\nDownload speed: ' + humansize(ds) + '\n') # print readable downloadspeed

# function to change the sysconf
def sysconf():
    with open('/etc/iserv/config', 'r') as config: # read in the file
        data = config.read()

    # replace
    data = data.replace('ShowLegalNotice = "none"', 'ShowLegalNotice = link')
    data = data.replace('PrintDirectEnable = false', 'PrintDirectEnable = true')
    data = data.replace('PrintDefault = true', 'PrintDefault = flase')
    data = data.replace('Region = ""', 'Region = "de_NW"')
    data = data.replace('DHCP = ("*")', 'DHCP = ("' +
                        question('Please enter internal NIC') + '")')
    # if downloadspeed >= 100mb/s 
    if ds >= 100000000:
        data = data.replace('WindowsupdateProxyMaxDownloaders = 3',
                            'WindowsupdateProxyMaxDownloaders = 30')
    else:
        data = data.replace('WindowsupdateProxyMaxDownloaders = 3',
                            'WindowsupdateProxyMaxDownloaders = 10')
    data = data.replace('DeployApplyAutoUpdates = false',
                        'DeployApplyAutoUpdates = true')
    data = data.replace('GrpVeyon = "lehrer"', 'GrpVeyon = "kollegium"')

    # Write changes to file
    with open('/etc/iserv/config', 'w') as config:
        config.write(data)

    print('Succesfully applied changes to system configuration.\n\n')

# function to deny given websites
def deny_websites(sites):
    with open("/usr/share/iserv/iconf/etc/squidguard/deny.local", "a+") as deny: # open file in append+ mode
        data = deny.read() # read content of file
        if sites in data: # if file already contains websites to block
            return 'Webseiten bereits verboten!'
        deny.write(sites)


if __name__ == "__main__":  # Only executes this script when it is executed directly
    answers = checkbox()
    if not answers:
        print("Nothing selected.\nAborting...")
    for answer in answers: # for checked box execute related function
        match answer:
            case 'Install packages': # add or remove packages here
                install_packages('freeradius freeradius-common freeradius-config freeradius-postgresql freeradius-utils freetds-common incron iserv-booking iserv-docker-libreoffice-online iserv-docker-libreoffice-online-data iserv-office iserv-poll iserv-schedule iserv-server-freeradius iserv-server-incron iserv-videoconference iserv-wlan iserv3-timetable libct4 libfreeradius3 iserv3-report krz-lemgo-remote-support')

            case 'Update privileges':
                priv_assign = Database("privileges_assign")
                priv_assign.update_privileges()
    
            case 'Create Import-Profiles':
                profiles = Database("import_profile")
                profiles.import_profile("import_profile.sql")

            case 'Create Groups': # add or remove groups here
                creategroups(["Krz", "Sekretariat", "Schulleitung", "Kollegium"])

            case 'Update Sysconf':
                load_speedtest()
                sysconf()

            case 'Deny Websites': # websites that should be blocked -> mostly on elementary schools 
                deny_websites('instagram.com\ntiktok.com\ntwitter.com\nfacebook.com\nsnapchat.com')