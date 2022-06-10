# sd-keepaneye, keeping an eye on systemd.
# Copyright (C) 2021 Alexandre Rossi <alexandre.rossi@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


from email.message import EmailMessage
import logging
import os
import subprocess
import sys


import sdkeepaneye.daemon


def readfile(path):
    with open(path, 'r') as f:
        return f.read().strip()


MACHINEID = readfile('/etc/machine-id')
HOSTNAME = os.uname()[1]
BOOTID = readfile('/proc/sys/kernel/random/boot_id')


logging.debug('machine-id is %s' % MACHINEID)
logging.debug('hostname   is %s' % HOSTNAME)
logging.debug('boot-id    is %s' % BOOTID)


def systemctl_status(unit):
    return """Hostname:\t%(hostname)s
Machine ID:\t%(machineid)s
Boot ID:\t%(bootid)s

%(status)s""" % {
    'unit'      : unit,
    'hostname'  : HOSTNAME,
    'machineid' : MACHINEID,
    'bootid'    : BOOTID,
    # FIXME: replace with systemd.journal.Reader() ?
    'status'    : subprocess.run(('systemctl', 'status', unit, '-l', '-n', '9999'),
                                  capture_output=True).stdout.decode(sys.getdefaultencoding()),
}


def send_email(unit):
    msg = EmailMessage()
    msg['Subject'] = 'Status report for unit: %s' % unit
    msg['From'] = 'systemd event monitor <root>'
    msg['To'] = 'root'

    msg.set_content(systemctl_status(unit))

    cmd = ('/usr/sbin/sendmail', '-t', '-oi')
    try:
        p = subprocess.run(cmd, input=msg.as_bytes(), capture_output=True)
    except subprocess.CalledProcessError:
        logging.error('could not send email for event of %s' % unit)
        logging.error('`%s` call failed with the following output:%s'
                      % (' '.join(cmd),
                         p))
    else:
        logging.info('sent email for event of %s' % unit)


def notify(notify_type, service):
    if notify_type == 'email':
        send_email(service)
    elif notify_type == 'stdout':
        print(systemctl_status(service))
    else:
        logging.error('unknown notification type %s.' % notify_type)
        sys.exit(os.EX_USAGE)


