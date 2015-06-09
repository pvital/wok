#
# Project Kimchi
#
# Copyright IBM, Corp. 2015
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import os
import tempfile
import unittest

from kimchi.model import model
from kimchi.yumparser import delete_repo_from_file, get_repo_files
from kimchi.yumparser import get_yum_repositories, write_repo_to_file
from kimchi.yumparser import YumRepoObject


TEMP_REPO_FILE = ''


def _is_yum_distro():
    inst = model.Model('test:///default')
    repo_type = inst.capabilities_lookup()['repo_mngt_tool']
    return repo_type == 'yum'


def _create_fake_repos(repo_file_name):
    repo1 = YumRepoObject('fake-repo-1', repo_file_name)
    repo2 = YumRepoObject('fake-repo-2', repo_file_name)
    repo3 = YumRepoObject('fake-repo-3', repo_file_name)
    repo4 = YumRepoObject('fake-repo-4', repo_file_name)
    repos = [repo1, repo2, repo3, repo4]
    return repos


def _create_fake_repos_file():
    _, tmp_file_name = tempfile.mkstemp(suffix='.repo',
                                        dir='/etc/yum.repos.d')

    fake_repos = _create_fake_repos(tmp_file_name)
    file_data = ''
    for repo in fake_repos:
        file_data += str(repo) + '\n'

    with open(tmp_file_name, 'w') as f:
        f.writelines(file_data)

    return tmp_file_name


@unittest.skipIf(not _is_yum_distro(), 'Skipping: YUM exclusive test')
def setUpModule():
    global TEMP_REPO_FILE
    TEMP_REPO_FILE = _create_fake_repos_file()


@unittest.skipIf(not _is_yum_distro(), 'Skipping: YUM exclusive test')
def tearDownModule():
    os.remove(TEMP_REPO_FILE)


@unittest.skipIf(not _is_yum_distro(), 'Skipping: YUM exclusive test')
class YumParserTests(unittest.TestCase):

    def test_get_yum_repositories(self):
        repo_files = get_repo_files()
        repo_objects = get_yum_repositories()
        self.assertGreaterEqual(len(repo_objects), len(repo_files))

    def test_update_repo_attributes(self):
        repos = get_yum_repositories()
        fake_repo_2 = repos['fake-repo-2']
        fake_repo_2.disable()
        fake_repo_2.name = 'This is a fake repo'
        fake_repo_2.baseurl = 'http://a.fake.repo.url'
        fake_repo_2.gpgkey = 'file://a/fake/gpg/key.fake'
        fake_repo_2.gpgcheck = False
        fake_repo_2.metalink = 'this is not a true metalink'
        fake_repo_2.mirrorlist = 'fake mirrorlist'
        write_repo_to_file(fake_repo_2)

        repos = get_yum_repositories()
        fake_repo_2 = repos['fake-repo-2']
        self.assertEqual(False, fake_repo_2.enabled)
        self.assertEqual(False, fake_repo_2.gpgcheck)
        self.assertEqual('This is a fake repo', fake_repo_2.name)
        self.assertEqual('http://a.fake.repo.url', fake_repo_2.baseurl)
        self.assertEqual('file://a/fake/gpg/key.fake', fake_repo_2.gpgkey)
        self.assertEqual('this is not a true metalink', fake_repo_2.metalink)
        self.assertEqual('fake mirrorlist', fake_repo_2.mirrorlist)

    def test_delete_repo_from_file(self):
        repos = get_yum_repositories()
        fake_repo_3 = repos['fake-repo-3']
        delete_repo_from_file(fake_repo_3)

        repos = get_yum_repositories()
        repos_id = repos.keys()
        self.assertNotIn('fake-repo-3', repos_id)
