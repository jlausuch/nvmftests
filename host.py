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
#   Author: Chaitanya Kulkarni <chaitanya.kulkarni@hgst.com>
#
""" Represents NVMe Over Fabric Host Subsystem.
"""

import json
import random
import subprocess

from utils.shell import Cmd
from host_subsystem import NVMeOFHostController


class NVMeOFHost(object):

    """
    Represents a host.
        - Attributes :
              - target_type : rdma/loop/fc. (only loop supported now)
              - ctrl_list : list of the host controllers.
    """
    def __init__(self, target_type):
        """ Constructor for NVMeOFHost.
            - Args :
                  - target_type : represents target transport type.
                  - ctrl_list : list of host controllers.
            - Returns :
                  - None.
        """
        self.target_type = target_type
        self.ctrl_list = []
        self.err_str = "ERROR : " + self.__class__.__name__ + " : "
        self.load_modules()

    def load_modules(self):
        """ Wrapper for Loading NVMeOF Host modules.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        ret = Cmd.exec_cmd("modprobe nvme-fabrics")
        if ret is False:
            print(self.err_str + "unable to load nvme-fabrics.")
            return False
        return True

    def config_loop(self, config_file):
        """ Configure host for loop target :-
            1. Load Loop module(s).
            2. Load config from json file.
            3. Create Controller list.
            - Args :
                  - None
            -Returns :
                  - True on success, False on failure.
        """
        ret = Cmd.exec_cmd("modprobe nvme-loop")
        if ret is False:
            print(self.err_str + "failed to load nvme-loop.")
            return False
        try:
            config_file_handle = open(config_file, "r")
            config = json.loads(config_file_handle.read())
            config_file_handle.close()
        except Exception, err:
            print(self.err_str + str(err))
            return False

        for sscfg in config['subsystems']:
            ctrl = NVMeOFHostController(sscfg['nqn'], "loop")
            ret = ctrl.init_ctrl()
            if ret is False:
                print(self.err_str + "failed init_ctrl() " + \
                      str(ctrl.ctrl_dev) + ".")
                return False
            self.ctrl_list.append(ctrl)
        return True

    def run_ios_parallel(self, iocfg):
        """ Run parallel IOs on all host controller(s) and
            wait for completion.
            - Args :
                  - iocfg : io configuration.
            - Returns :
                  - None.
        """
        print("Starting IOs parallelly on all controllers ...")
        for ctrl in self.ctrl_list:
            if ctrl.run_io_all_ns(iocfg) is False:
                return False

        print("Waiting for all threads to finish the IOs...")
        for ctrl in self.ctrl_list:
            ctrl.wait_io_all_ns()

        return True

    def run_ios_seq(self, iocfg):
        """ Run IOs on all host controllers one by one.
            - Args :
                  - None.
            - Returns :
                  - None.
        """
        print("Starting IOs seq ...")
        ret = None
        for ctrl in self.ctrl_list:
            ret = ctrl.run_io_seq(iocfg)
            if ret is False:
                break

        return ret

    def run_ios_random(self, iocfg):
        """ Select a controller from the list of controllers
            randomly and run IOs. Exhaust entire list.
            - Args :
                  - None.
            - Returns :
                  - None.
        """
        ctrl_list = range(0, len(self.ctrl_list))

        ret = True
        for i in range(0, len(self.ctrl_list)):
            random.shuffle(ctrl_list)
            ctrl_id = ctrl_list.pop()
            ctrl = self.ctrl_list[ctrl_id]
            if ctrl.run_io_random(iocfg) is False:
                ret = False
                break

        return ret

    def smart_log(self):
        """ Execute smart log.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        ret = True
        for ctrl in self.ctrl_list:
            if ctrl.smart_log() is False:
                ret = False
                break

        return ret

    def id_ctrl(self):
        """ Execute id-ctrl on all the controllers(s).
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        ret = True
        for ctrl in self.ctrl_list:
            if ctrl.id_ctrl() is False:
                ret = False
                break

        return ret

    def id_ns(self):
        """ Execute id-ns on controllers(s) and all its namespace(s).
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        ret = True
        for ctrl in self.ctrl_list:
            if ctrl.id_ns() is False:
                ret = False
                break

        return ret

    def mkfs_seq(self):
        """ Run mkfs, mount fs, run IOs.
            - Args :
                  - None.
            - Returns :
                  - None.
        """
        ret = True
        for ctrl in self.ctrl_list:
            if ctrl.run_mkfs_seq() is False:
                ret = False
                break

        return ret

    def config(self, config_file="loop.json"):
        """ Configure Host based on the target transport.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        ret = False
        if self.target_type == "loop":
            print("Configuring loop host")
            ret = self.config_loop(config_file)
        else:
            print(self.err_str + "only loop target type is supported.")
        return ret

    def delete(self):
        """ Delete all the Host Controllers.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        ret = True
        for subsys in self.ctrl_list:
            if subsys.delete() is False:
                ret = False
        return ret
