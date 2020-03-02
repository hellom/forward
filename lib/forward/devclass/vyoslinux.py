# coding:utf-8
#
# This file is part of Forward.
#
# Forward is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Forward is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
-----Introduction-----
[Core][forward] Device class for bclinux7.
"""
import re
from forward.devclass.bclinux7 import BCLINUX7


class VYOSLINUX(BCLINUX7):
    """This is a manufacturer of linux, so it is integrated with BCLINUX7 library.
    """
    def execute(self, cmd):
        """Because of the specificity of the device, it is not consistent with
        the execute method of the Linux device, so it is rewritten here."""
        result = {
            'status': False,
            'content': '',
            'errLog': ''
        }
        # Clean buffer.
        self.cleanBuffer()
        # Login status check.
        if self.isLogin:
            # check login status
            """The result returned is similar to 'show version\r\n\x1b[?1h\x1b=\r
               Version:      VyOS 1.1.7\x1b[m\r\nDescription:  VyOS 1.1.7 (helium
               )\x1b[m\r\nCopyright: 0.29\x1b[m\r\n\x1b[m\r\n\r\x1b[K\x1b[?1l
               \x1b>vyos@nxx-sdn-fwvm-253-153:~$
               Because of this type of device, special character information
               will be generated after executing the command, so delete it here.
            """
            self.shell.send(cmd + "\r")
            # resultPattern = '[\r\n]+([\s\S]*)[\r\n]+' + self.prompt
            resultPatternOld = '[\r\n]+([\s\S]*)[\r\n]+' + self.prompt
            resultPattern = "[\r\n]+([\s\S]*)({character1_1}|{character1_2}|{character1_\
            3}|{character1_4}){character2}".format(
                            character1_1=re.escape("\x1b[m\r\n\x1b[m\r\n\r\x1b[K\x1b[?1l\x1b>"),
                            character1_2=re.escape('\x1b[m\r\n\r\x1b[K\x1b[?1l\x1b>'),
                            character1_3=re.escape('\x1b[?1h\x1b=\r\r\x1b[K\x1b[?1l\x1b>'),
                            character1_4=re.escape('\x1b[m\r\n\x1b[m\r\n \x1b[m\r\n\r\x1b[K\x1b[?1l\x1b>'),
                            character2=self.prompt)
            try:
                while not re.search(self.prompt, result['content'].split('\n')[-1]):
                    # Get more.
                    self.getMore(result['content'])
                    # Get result.
                    result['content'] += self.shell.recv(1024).decode
                # try to extract the return data
                try:
                    # Intercepting the results of the command execution.
                    tmp = re.search(resultPattern, result['content']).group(1)
                except Exception:
                    # In cases where special characters are not included,
                    # the original character characteristics should be used
                    # Intercepting the results of the command execution.
                    tmp = re.search(resultPatternOld, result['content']).group(1)
                result['content'] = tmp
                result['status'] = True
            except Exception as e:
                # pattern not match
                result['status'] = False
                result['content'] = result['content']
                result['errLog'] = str(e)
        else:
            # not login
            result['status'] = False
            result['errLog'] = '[Execute Error]: device not login'
        return result
