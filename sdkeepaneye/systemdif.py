# sd-keepaneye, keeping an eye on systemd.
# Copyright (C) 2023 Alexandre Rossi <alexandre.rossi@gmail.com>
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


class SystemdInterface(object):

    def __init__(self):
        self.sysbus = pydbus.SystemBus()
        if not self.sysbus:
            logging.error('Cannot connect to system D-Bus')
            sys.exit(1)

        self.systemd1 = self.sysbus.get('.systemd1')
        self.manager = self.systemd1['.Manager']

    def list_units(self, typefilter=None):
        for u in self.manager.ListUnits():
            unit, desc, load, active, state = u[:5]

            if typefilter and self.unit_type(unit) not in typefilter:
                continue

            try:
                assert load in ('loaded', 'not-found', )
                assert active in ('active', 'inactive', 'activating', 'deactivating', 'failed', )
                assert state in ('plugged', 'exited', 'running', 'dead', 'active', 'waiting', 'elapsed', 'mounted', 'listening', 'failed', )
            except AssertionError:
                logging.debug('Unknwon state received for unit %s: %s'
                              % (unit, ', '.join((load, active, state, )), ))
            yield unit, load, active, state


    def unit_type(self, unit_name):
        return unit_name.split('.')[-1]


