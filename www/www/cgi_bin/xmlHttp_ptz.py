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
Feed the POST'd value to the named pipe 'fifo_ptz'
"""

import os, os.path

def index(req):
    """
    Feed the POST'd 'val' to the named pipe 'fifo_ptz'
    
    args    : req
    excepts : 
    return  : none 
    """
    
    func = req.form['val']
    file_path = str(req.__getattribute__('filename'))
    www_dir = os.path.abspath('%s/../../..' % file_path)
    
    pipeout = os.open('%s/fifo_ptz' % www_dir, os.O_WRONLY)
    os.write(pipeout, func)
    os.close(pipeout)

    
# Module self test
class Test_Class(object):
        
    def __init__(self): 
        self.filename = '../null/null'
        self.form = {'val': 'crf01b01$'}
    
if __name__ == '__main__':
    print '\nModule self test ... adding \'crf01b01$\' to fifo_ptz\n'
    index(Test_Class())






















