#!/usr/bin/env python

# Copyright 2008 David Selby dave6502@googlemail.com

# This file is part of kmotion.

# kmotion is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# kmotion is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with kmotion.  If not, see <http://www.gnu.org/licenses/>.

"""
Returns a coded string data blob containing the error file
"""

import os, time

def index(req):
    """
    Gets the motions daemons error output
    
    args    : 
    excepts : 
    return  : a coded string containing ...
    
    
    The motion daemons error output
    <string>
    
    A length checksum
    $ck<length - $ck0000 element>
    """

    # python executed within python-mod has an undefined cwd
    file_path = str(req.__getattribute__('filename'))
    www_dir = os.path.abspath('%s/../../..' % file_path)
    
    coded_str = ''
    # sloppy checking but due to 'motion_out' being appended to directly from
    # 'motion' daemon its impossible to add an EOF checker
    while True:
        try:
            f_obj = open('%s/motion_out' % www_dir)
            coded_str += f_obj.read().rstrip()
            f_obj.close()
            break
        except IOError: # an file exceptions, pause and loop
            time.sleep(0.01)
        
    # possibly large string so 6 digit checksum
    coded_str += '$ck:%06i' % len(coded_str)
    return coded_str



# Module test code
class Test_Class(object):

    def __init__(self):
        self.filename = '../null/null'

if __name__ == '__main__':
    print '\nModule self test ...\n'
    print index(Test_Class())



