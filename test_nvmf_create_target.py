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
"""
NVMF Create/Delete Target :-

    1. From the config file create Target.
    2. Delete Target.
"""


from nose.tools import assert_equal
from nvmf.misc.null_blk import NullBlk
from nvmf_test import NVMFTest
from nvmf.target import NVMFTarget
from nvmf.target import NVMFTargetNamespace


class TestNVMFCreateTarget(NVMFTest):

    """ Represents Create Target testcase """

    def __init__(self):
        NVMFTest.__init__(self)
        self.target_subsys = None
        self.setup_log_dir(self.__class__.__name__)

    def setUp(self):
        """ Pre section of testcase """
        self.null_blk = NullBlk(self.data_size, self.block_size, self.nr_dev)
        self.null_blk.init()
        self.build_target_config(self.null_blk.dev_list)
        target_type = "loop"
        self.target_subsys = NVMFTarget(target_type)

    def tearDown(self):
        """ Post section of testcase """
        self.target_subsys.delete()
        self.null_blk.delete()

    def test_create_target(self):
        """ Testcase main """
        ret = self.target_subsys.config(self.target_config_file)
        assert_equal(ret, True, "ERROR : config target failed.")
