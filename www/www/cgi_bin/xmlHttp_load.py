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
Returns a coded string data blob containing load statistics
"""

import os, re

def index():
    """
    Gets server statistics from 'uname' and 'top' 
    
    args    : 
    excepts : 
    return  : a coded string containing ...
    
    The box name
    $bx:<name>
    
    Server info
    $sr:<server info>
    
    Server uptime
    $up:<uptime>
    
    The load averages for 1min, 5min, 15min
    $l1:<number>
    $l2:<number>
    $l3:<number>
    
    The CPU user, system and IO wait percent
    $cu:<percent>
    $cs:<percent>
    $ci:<percent>
    
    The memory total, free, buffers, cached
    $mt:<total>
    $mf:<free>
    $mb:<buffers>
    $mc:<cached>
    
    The swap total, used
    $st:<total>
    $su:<used>
    
    A length checksum
    $ck<length - $ck0000 element>
    """

    f_obj = os.popen3('uname -srvo')[1]
    uname = f_obj.readline()
    f_obj.close()

    u_split = uname.split(' ')
    coded_str = '$bx:%s' % ' '.join(u_split[0:2])    # box name 
    coded_str += '$sr:%s' % ' '.join(u_split[2:-1])  # server info

    f_obj = os.popen3('top -b -n 1')[1]
    top = f_obj.readlines()
    f_obj.close()

    top_0 = re.split(r'[\s,]+', top[0])

    coded_str += '$up:'  # uptime
    for i in range(4, len(top_0) - 1):
        if top_0[i + 1][:4] != 'user':
            coded_str += '%s ' % top_0[i]
        else:
            break

    coded_str += '$l1:%s' % top_0[-4]   # load average 1
    coded_str += '$l2:%s' % top_0[-3]   # load average 1
    coded_str += '$l3:%s' % top_0[-2]   # load average 1

    top_2 = re.split(r'[\s,]+', top[2])

    coded_str += '$cu:%s' % top_2[1][:-3]  # CPU user
    coded_str += '$cs:%s' % top_2[2][:-3]  # CPU systemuser
    coded_str += '$ci:%s' % top_2[5][:-3]  # CPU IO wait

    top_3 = re.split(r'[\s,]+', top[3])

    coded_str += '$mt:%s' % top_3[1][:-1]  # memory total
    coded_str += '$mf:%s' % top_3[5][:-1]  # memory free
    coded_str += '$mb:%s' % top_3[7][:-1]  # memory buffers

    top_4 = re.split(r'[\s,]+', top[4])

    coded_str += '$mc:%s' % top_4[7][:-1]  # memory cached
    coded_str += '$st:%s' % top_4[1][:-1]  # swap total
    coded_str += '$su:%s' % top_4[3][:-1]  # swap used

    coded_str += '$ck:%04i' % len(coded_str)
    return coded_str


# Module self test
if __name__ == '__main__':
    print '\nModule self test ...\n'
    print index()





