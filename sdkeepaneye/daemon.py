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


import logging
import signal
import sys


from gi.repository import GLib
from gi.repository import Gio
import pydbus
import systemd.daemon


from . import systemdif
from . import notify


class SystemdMonitor(systemdif.SystemdInterface):

    def __init__(self, conf):
        super(SystemdMonitor, self).__init__()

        self.systemd1.JobRemoved.connect(self.systemd_event_cb)
        GLib.timeout_add(100, self.subscribe)

        self.conf = conf
        self.failed_units = []

    def __init_failed_units(self):
        for u in self.list_units():
            unit, load, active, state = u
            if state == 'failed':
                self.failed_units.append(unit)
        if self.failed_units:
            logging.debug('found the following failed units at startup: \n\t%s' % '\n\t'.join(self.failed_units))
            for failed_unit in self.failed_units:
                notify.send_email(failed_unit)
        else:
            logging.debug('no failed units found at startup')

    def subscribe(self):
        self.manager.Subscribe()
        logging.info('subscribed to systemd events')

        self.__init_failed_units()

        systemd.daemon.notify('READY=1')
        return False # make Glib.timeout_add() not repeat the call

    def get_unit_policy(self, unit):
        policy = None
        unit_name = unit.split('.')[0]
        if unit_name in self.conf['notify']:
            policy = self.conf['notify'][unit_name]
        else:
            policy = self.conf['keepaneye']['notify_policy']
        logging.debug("Policy for unit %s is '%s'", unit, policy)
        return policy

    def register_failed_state(self, unit_name, invocation_id, failed_state):
        if failed_state:
            if unit_name in self.failed_units:
                logging.debug('Unit %s: already failed, not notifying.'
                              % unit_name)
            else:
                failure = {
                    'unit'          : unit_name,
                    'invocation_id' : invocation_id,
                }
                self.failed_units.append(failure)
                notify.send_email(failure)

        elif unit_name in self.failed_units:
            self.failed_units.remove(unit_name)
            logging.debug('Unit %s: not failed anymore' % unit_name)

    def is_unit_failed(self, unit_name):
        try:
            unit = self.manager.GetUnit(unit_name)
        except GLib.Error as err:
            if Gio.DBusError.get_remote_error(err) \
            == 'org.freedesktop.systemd1.NoSuchUnit':
                logging.debug('Could not find any info on Unit %s, ignoring.'
                              % unit_name)
                return False
            else:
                raise

        if not unit:
            logging.debug('unit %s not found in system bus, user unit?' % unit_name)
            return None
        else:
            unit_if = self.sysbus.get('.systemd1', unit)
            unit_props = unit_if['org.freedesktop.DBus.Properties']

            failed_state = False

            active_state = unit_props.Get('org.freedesktop.systemd1.Unit',
                                          'ActiveState')
            sub_state = 'unprobbed'
            if active_state == 'failed':
                failed_state = True
            else:
                sub_state = unit_props.Get('org.freedesktop.systemd1.Unit',
                                           'SubState')
                if sub_state == 'failed':
                    failed_state = True

            invocation_id = unit_props.Get('org.freedesktop.systemd1.Unit',
                                           'InvocationID')
            invocation_id = ''.join(map(lambda x: '%0.2x' %x, invocation_id))

            logging.debug('Unit %s: ActiveState=%s, SubState=%s, InvocationID=%s'
                          % (unit_name, active_state, sub_state,
                             invocation_id))

            self.register_failed_state(unit_name, invocation_id, failed_state)

            return failed_state

    def is_unit_failed_retry(self, unit_name):
        self.is_unit_failed(unit_name)
        return False # make Glib.timeout_add() not repeat the call

    def systemd_event_cb(self, jobid, job_buspath, unit, result):
        logging.debug('received event for unit %s with result %s, jobid=%s'
                      % (unit, result, jobid))

        if unit.split('.')[-1] == 'scope':
            logging.debug('%s is a scope unit, ignoring.' % unit)
            return

        policy = self.get_unit_policy(unit)
        if policy == 'always':
            notify.send_email(unit)
        elif policy == 'onfailure':
            if not self.is_unit_failed(unit):
                GLib.timeout_add(1000, self.is_unit_failed_retry, unit)


def start(conf):
    SystemdMonitor(conf)
    loop = GLib.MainLoop()

    def sigint_handler(sig, frame):
        if sig == signal.SIGINT:
            loop.quit()
    signal.signal(signal.SIGINT, sigint_handler)

    loop.run()
