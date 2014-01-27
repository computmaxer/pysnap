#!/usr/bin/env python

"""Basic Snapchat client

Usage:
  get_snaps.py -u <username> [-p <password> -q]

Options:
  -h --help                 Show usage
  -q --quiet                Suppress output
  -u --username=<username>  Username
  -p --password=<password>  Password (optional, will prompt if omitted)

"""
from __future__ import print_function

import os.path
import sys
from getpass import getpass

from docopt import docopt

from pysnap import get_file_extension, Snapchat

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

email_fromaddr = 'maxpete@iastate.edu'
email_toaddrs  = 'computmaxer@gmail.com'


def main():
    arguments = docopt(__doc__)
    quiet = arguments['--quiet']
    username = arguments['--username']
    if arguments['--password'] is None:
        password = getpass('Password:')
    else:
        password = arguments['--password']
    #path = arguments['<path>']
    path = "snaps"

    if not os.path.isdir(path):
        print('No such directory: {0}'.format(arguments['<path>']))
        sys.exit(1)

    s = Snapchat()
    if not s.login(username, password).get('logged'):
        print('Invalid username or password')
        sys.exit(1)


    for snap in s.get_snaps():
        filename = '{0}_{1}.{2}'.format(snap['sender'], snap['id'],
                                        get_file_extension(snap['media_type']))
        abspath = os.path.abspath(os.path.join(path, filename))
        if os.path.isfile(abspath):
            continue
        data = s.get_blob(snap['id'])
        if data is None:
            continue
        with open(abspath, 'wb') as f:
            f.write(data)

            # If we successfully mark this as viewed, go ahead and email it.
            if s.mark_viewed(snap['id']):
                # Setup email message
                msg = MIMEMultipart()
                msg['From'] = "Snapchat"
                msg['To'] = email_toaddrs
                msg['Subject'] = "Snapchat from %s" % snap['sender']
                body = "You have received a new snapchat from %s" % snap['sender']
                msg.attach(MIMEText(body, "plain"))
                msg.attach(MIMEImage(data))

                # The actual mail send
                if not quiet:
                    print("Sending mail!")
                server = smtplib.SMTP()
                server.connect('mailhub.iastate.edu', 25)
                server.ehlo()
                server.starttls()
                #server.login('username', 'password')
                server.sendmail(email_fromaddr, email_toaddrs, msg.as_string())
                server.quit()

            if not quiet:
                print('Saved: {0}'.format(abspath))


if __name__ == '__main__':
    main()
