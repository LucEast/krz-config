import inquirer
from inquirer.themes import GreenPassion

questions = [inquirer.Checkbox('options',
                               message="What do you want to run?",
                               choices=["Install packages", "Update privileges",
                                        "Create Import-Profiles", "Create Groups", "Update Sysconf"],
                               default=["Install packages", "Update privileges", "Create Import-Profiles", "Create Groups", "Update Sysconf"]),
             ]
answers = inquirer.prompt(questions, theme=GreenPassion())['options']

for answer in answers:
    # print(answer)
    if 'Install packages' in answer:
        print('Install packages')
    if 'Update privileges' in answer:
        print('Update privileges')
    if 'Create Import-Profiles' in answer:
        print('Create Import-Profiles')
    if 'Create Groups' in answer:
        print('Create Groups')
    if 'Update Sysconf' in answer:
        print('Update Sysconf')


class install_pkg:
    def __init__(self):
        pass

    def install_packages(self, packages):
        print('apt install ' + packages)


if __name__ == "__main__":
    pkgs = install_pkg()
    pkgs.install_packages('freeradius freeradius-common freeradius-config freeradius-postgresql freeradius-utils freetds-common incron iserv-booking iserv-docker-libreoffice-online iserv-docker-libreoffice-online-data iserv-office iserv-poll iserv-schedule iserv-server-freeradius iserv-server-incron iserv-videoconference iserv-wlan iserv3-timetable libct4 libfreeradius3 iserv3-report krz-lemgo-remote-support')
