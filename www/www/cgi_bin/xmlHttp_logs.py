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
Returns a string data blob containing 'logs'
"""

import os, time, random

def index(req):
    """
    Returns a string data blob containing the 'logs'
    
    args    : 
    excepts : 
    return  : a coded string containing ...
    
    $date#time#text$date ... $ck<length - $ck0000 element>
    """
    
    file_path = str(req.__getattribute__('filename'))
    www_dir = os.path.abspath('%s/../../..' % file_path)
    kmotion_dir = os.path.abspath('%s/..' % www_dir)
    coded_str = ''
    
    try:
        mutex_acquire(kmotion_dir)
        f_obj = open('%s/www/logs' % kmotion_dir)
        coded_str = f_obj.read()
        f_obj.close()     
    finally:
        mutex_release(kmotion_dir)
    
    coded_str += '$ck:%04i' % len(coded_str)
    return coded_str


def mutex_acquire(kmotion_dir):
    """ 
    Aquire the 'logs' mutex lock, very carefully
    
    args    : 
    excepts : 
    return  : none
    """
    
    while True:
        # wait for any other locks to go
        while True:
            if check_lock(kmotion_dir) == 0:
                break
            time.sleep(0.01)
        
        # add our lock
        f_obj = open('%s/www/mutex/logs/%s' % (kmotion_dir, os.getpid()), 'w')
        print >> f_obj, ''
        f_obj.close()
            
        # wait ... see if another lock has appeared, if so remove our lock
        # and loop
        time.sleep(0.1)
        if check_lock(kmotion_dir) == 1:
            break
        os.remove('%s/www/mutex/logs/%s' % (kmotion_dir, os.getpid()))
        # random to avoid mexican stand-offs
        time.sleep(float(random.randint(01, 40)) / 1000)
            
        
def mutex_release(kmotion_dir):
    """ 
    Release the 'logs' mutex lock
    
    args    : kmotion_dir ... kmotions root dir
    excepts : 
    return  : none
    """
    
    if os.path.isfile('%s/www/mutex/logs/%s' % (kmotion_dir, os.getpid())):
        os.remove('%s/www/mutex/logs/%s' % (kmotion_dir, os.getpid()))
       
        
def check_lock(kmotion_dir):
    """
    Return the number of active locks on the log mutex, filters out .svn
    
    args    : kmotion_dir ... kmotions root dir
    excepts : 
    return  : num locks ... the number of active locks
    """
    
    files = os.listdir('%s/www/mutex/logs' % kmotion_dir)
    files.sort()
    if len(files) > 0 and files[0] == '.svn': # strip the .svn dir
        files.pop(0)
    return len(files)
        
        
   
# Module self test
class Test_Class(object):
        
    def __init__(self):
        self.filename = '../null/null'
    
if __name__ == '__main__':
    print '\nModule self test ...\n'
    print index(Test_Class())








