#!/usr/bin/python
################################################################################

from test import *

from diamond.collector import Collector
from DiskSpaceCollector import DiskSpaceCollector

import disk

################################################################################

class TestDiskSpaceCollector(CollectorTestCase):
    def setUp(self):
        config = get_collector_config('DiskSpaceCollector', {
            'interval'  : 10,
            'byte_unit' : 'gigabyte'
        })

        self.collector = DiskSpaceCollector(config, None)

    @patch('os.access', Mock(return_value=True))
    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data(self, publish_mock):
        statvfs_mock = Mock()
        statvfs_mock.f_bsize   = 4096
        statvfs_mock.f_frsize  = 4096
        statvfs_mock.f_blocks  = 360540255
        statvfs_mock.f_bfree   = 285953527
        statvfs_mock.f_bavail  = 267639130
        statvfs_mock.f_files   = 91578368
        statvfs_mock.f_ffree   = 91229495
        statvfs_mock.f_favail  = 91229495
        statvfs_mock.f_flag    = 4096
        statvfs_mock.f_namemax = 255

        with nested(
            patch('os.stat'),
            patch('os.major', Mock(return_value = 9)),
            patch('os.minor', Mock(return_value = 0)),
            patch('__builtin__.open', Mock(return_value = self.getFixture('proc_mounts')))
        ):
            file_systems_mock = disk.get_file_systems()

        with nested(
            patch('disk.get_file_systems', Mock(return_value = file_systems_mock)),
            patch('os.statvfs', Mock(return_value = statvfs_mock))
        ):
            self.collector.collect()

        self.assertPublishedMany(publish_mock, {
            'root.gigabyte_used'  : ( 284.525, 2),
            'root.gigabyte_free'  : (1090.826, 2),
            'root.gigabyte_avail' : (1020.962, 2),
            'root.inodes_used'    : 348873,
            'root.inodes_free'    : 91229495,
            'root.inodes_avail'   : 91229495
        })

################################################################################
if __name__ == "__main__":
    unittest.main()
