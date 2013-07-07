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
Delete the appropreate file in 'ramdisk_dir/events' and execute the
appropreate script in 'event' if it exists.
"""

import os, sys, ConfigParser
import logger, mutex

log_level = 'WARNING'
logger = logger.Logger('event_end', log_level)

def main():
    """
    Delete the appropreate file in 'ramdisk_dir/events' and execute the
    appropreate script in 'event' if it exists.
    """

    event = int(sys.argv[1])
    kmotion_dir = os.getcwd()[:-5]
    
    try:
        mutex.acquire(kmotion_dir, 'core_rc')   
        parser = ConfigParser.SafeConfigParser()
        parser.read('./core_rc') 
    finally:
        mutex.release(kmotion_dir, 'core_rc')
        
    ramdisk_dir = parser.get('dirs', 'ramdisk_dir')
    event_file = '%s/events/%s' % (ramdisk_dir, event)
    if os.path.isfile(event_file):
        os.remove(event_file)
    
    exe_file = '%s/event/event_end%02i.sh' % (kmotion_dir, event)
    if os.path.isfile(exe_file):
        logger.log('executing: %s' % exe_file, 'CRIT')
        os.popen3('nohup %s &' % exe_file)
    
        
main()
        
        
        
        
        