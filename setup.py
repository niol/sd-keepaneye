#!/usr/bin/python3
#
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


import distutils.command.build
from distutils.core import setup
from distutils.core import Command
from distutils.dep_util import newer
from distutils.spawn import find_executable
import glob
import os


class build_manpages(Command):

    description = 'Build manpages'
    user_options = []

    manpages = None
    mandir = os.path.join(os.path.dirname(__file__), 'man')
    executable = find_executable('pandoc')

    def initialize_options(self):
        pass

    def finalize_options(self):
        self.manpages = glob.glob(os.path.join(self.mandir, '*.md'))

    def __get_man_section(self, filename):
        # filename should be file.mansection.md
        return filename.split('.')[-2]

    def run(self):
        data_files = self.distribution.data_files

        for manpagesrc in self.manpages:
            manpage = os.path.splitext(manpagesrc)[0] # remove '.md' at the end
            section = manpage[-1:]
            if newer(manpagesrc, manpage):
                cmd = (self.executable, '-s', '-t', 'man',
                       '-o', manpage,
                       manpagesrc)
                self.spawn(cmd)

            targetpath = os.path.join('share', 'man', 'man%s' % section)
            data_files.append((targetpath, (manpage, ), ))


class build(distutils.command.build.build):

    def __has_manpages(self, command):
        return 'build_manpages' in self.distribution.cmdclass\
            and build_manpages.executable is not None

    def finalize_options(self):
        distutils.command.build.build.finalize_options(self)
        self.sub_commands.append(("build_manpages", self.__has_manpages))


setup(name='sd-keepaneye',
      version='0.2',
      description='Keeping an eye on systemd',
      author='Alexandre Rossi',
      author_email='alexandre.rossi@gmail.com',
      url='https://sml.zincube.net/~niol/repositories.git/sd-keepaneye/about/',
      scripts=['keepaneyed'],
      data_files=[],
      cmdclass = {
          'build'         : build,
          'build_manpages': build_manpages,
      },
     )
