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
Returns the latest jpeg filenames and event status
"""

import time, os, os.path, cPickle


def index(req):
    """
    Returns the latest jpeg filenames for all active video feeds plus a token 
    for any feeds identified in 'images_dbase_dir/.../events' (ie feeds with 
    motion detected). In addition returns the latest 'servo_state'

    The returned data is in a form that facilitates rapid Javascript string 
    splitting:

    #<latest filename camera 1># ... #<latest filename camera 16>...
    #<latest server state>$<event number>$<event number>$ ...

    args    : req ... from python-mod
    excepts : 
    returns : string data blob
    """

    # python executed within python-mod has an undefined cwd
    file_path = str(req.__getattribute__('filename'))
    www_dir = os.path.abspath('%s/../../..' % file_path)
    kmotion_dir = os.path.abspath('%s/..' % www_dir)

    # unpickle 'feed_cache' list which has the format
    # ['ramdisk_dir', 'feed 1 enabled', 'feed 2 enabled', .....]
    # called multiple times per sec, no time for mutex :)
    f_obj = open('%s/www/feeds_cache' % kmotion_dir)
    cache = cPickle.load(f_obj)
    f_obj.close()
    
    ramdisk_dir = cache[0]
    dblob = '#'
    for feed in range(1, 17):
        if cache[feed]:
        #if parser.get('motion_feed%02i' % feed, 'feed_enabled') == 'true':
            # 'last_jpeg' is sometimes blank due to 'motion' calling BASH to
            # update it. This loop retrys to avoid white frames live view
            tmp = ''
            last_jpeg = '%s/%02i/last_jpeg' % (ramdisk_dir, feed)
            for attempt in range(5):
                # if 'motion' fails to start avoids this script crashing
                try:
                    f_obj = open(last_jpeg)
                    tmp = f_obj.readline().rstrip()
                    f_obj.close()
                    break
                except IOError:
                    pass
                time.sleep(0.01)
                
            # strip off everything before '/images_dbase/...' or 
            # '/kmotion_ramdisk/...' so apache2 can alias the path
            tmp = os.path.normpath(tmp)
            
            index_ = tmp.find('/images_dbase/')
            if index_ == -1: 
                index_ = tmp.find('/kmotion_ramdisk/')
            if index_ == -1: 
                index_ = tmp.find('/virtual_ramdisk/')
            
            index_ = max(index_, 0) # limit in case tmp = ''
            tmp_stripped = tmp[index_:]
            
            # screen for no image if feed enabled but no camera
            if tmp_stripped == '.':
                tmp_stripped = ''
            dblob += tmp_stripped
            
        dblob += '#'
    
    # called multiple times per sec, no time for mutex :)
    f_obj = open('%s/servo_state' % www_dir)
    dblob += f_obj.read().rstrip()
    f_obj.close()
        
    dblob += '#'
            
    for event in os.listdir('%s/events' % ramdisk_dir):
        dblob += '$%s' % event

    return dblob



# Module test code
class Test_Class(object):

    def __init__(self):
        self.filename = '../null/null'

if __name__ == '__main__':
    print '\nModule self test ...\n'
    print index(Test_Class())






















