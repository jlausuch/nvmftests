# Copyright (c) 2016-2017 Western Digital Corporation or its affiliates.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.
#
#   Author: Chaitanya Kulkarni <chaitanya.kulkarni@wdc.com>
#
""" Represents Shell Command execution.
"""
import subprocess


class Cmd(object):

    """
    Represents a shell command execution.
        - Attributes :
    """

    @staticmethod
    def exec_cmd(cmd):
        """ Wrapper for executing a shell command.
            - Args :
                - cmd : command to execute.
            - Returns :
                - True if cmd returns 0, False otherwise.
        """
        proc = None
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        except Exception as err:
            print(str(err))
            return False

        return True if proc.wait() == 0 else False
