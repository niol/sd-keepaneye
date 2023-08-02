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


from sdkeepaneye import systemdif


NAME = 'systemd-units'


if __name__ != '__main__':
    import collectd


def collectd_dispatch(collectd_type, type_instance, value):
    val = collectd.Values(plugin=NAME, type=collectd_type)
    val.type_instance = type_instance
    val.values = [ value ]
    val.dispatch()
dispatch = collectd_dispatch


def debug_dispatch(collectd_type, type_instance, value):
    print("DEBUG: %s/%s-%s = %s" %(NAME, collectd_type, type_instance, value))


class SystemdStatsCollector(systemdif.SystemdInterface):

    def read_callback(self):
        stats = {
            'total'    : 0,
            'notfound' : 0,
            'active'   : 0,
            'failed'   : 0,
        }

        for u in self.list_units(typefilter=('service','socket', )):
            unit, load, active, state = u
            stats['total'] = stats['total'] + 1
            if load == 'notfound':
                stats['notfound'] = stats['total'] + 1
            if active in ('active', 'activating', ):
                stats['active'] = stats['active'] + 1
            if active == 'failed':
                stats['failed'] = stats['failed'] + 1

        for stat_name, count in stats.items():
            dispatch('count', stat_name, count)


c = SystemdStatsCollector()


if __name__ == '__main__':
    dispatch = debug_dispatch
    c.read_callback()
else:
    collectd.register_read(c.read_callback, 30)
