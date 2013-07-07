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
Returns the archive data index's
"""

import ConfigParser, os, time, random, os.path, datetime


def index(req):
    """
    Returns a coded string containing 'images_dbase' indexes for the archive 
    function. The returned data is dependent on the xmlhttp request.
    
    'date' = date YYYYMMDD
    'cam'  = camera 1 .. 16
    'func' = 'avail', 'index'
    
    if 'func' == 'avail' ie avaliable dates, coded string consists of:
    $<YYYYMMDD date >#<?? feed num>#A#B#C#<title># ...
    
    if 'func' = 'index' ie the indexes, coded string consists of consists of:
    
    $<HHMMSS movie start time>#<?? fps>#<HHMMSS movie end time> ... @
    $<HHMMSS smovie start>#<?? start items>#<?? fps>#<HHMMSS smovie end>#<?? end items>... @
    $<HHMMSS snap init time>#<?? interval secs> ... 
    
    args    : req ... from python-mod
    excepts : 
    returns : coded string
    """

    # python executed within python-mod has an undefined cwd
    file_path = str(req.__getattribute__('filename'))
    kmotion_dir = os.path.abspath('%s/../../../..' % file_path)
    parser = ConfigParser.SafeConfigParser()
    
    try:
        mutex_acquire(kmotion_dir)
        parser.read('%s/www/www_rc' % kmotion_dir)
    finally:
        mutex_release(kmotion_dir)
    
    images_dbase_dir = parser.get('system', 'images_dbase_dir')
    
    date_ = req.form['date']
    feed =  int(req.form['cam'])
    func =  req.form['func']
    
    coded_str = '' # in case of corrupted value, return zip
    
    if func == 'avail':   # date_s avaliable
        coded_str = date_feed_avail_data(images_dbase_dir)
        
    elif func == 'index': # movies and snapshots
        fps_time, fps = fps_journal_data(images_dbase_dir, date_, feed)
        coded_str = movie_journal_data(images_dbase_dir, date_, feed, fps_time, fps) + '@'
        coded_str += smovie_journal_data(images_dbase_dir, date_, feed, fps_time, fps) + '@' 
        coded_str += snap_journal_data(images_dbase_dir, date_, feed)
        
    coded_str += '$chk:%08i' % len(coded_str)
    return coded_str
    

def date_feed_avail_data(images_dbase_dir):
    """
    Returns a coded string containing the avaliable archive dates and feeds
    
    coded string consists of:
    
    $<YYYYMMDD date >#<?? feed num>#A#B#C#<title>#<?? feed num>#A#B#C#<title> ...
    
    A = movie dir exists,  1 yes; 0 no
    B = smovie dir exists, 1 yes; 0 no
    C = snap dir exists,   1 yes; 0 no
    
    args    : images_dbase_dir ... the images dbase dir ;)
    excepts : 
    returns : coded string
    """
    
    coded_str = ''
    dates = [i for i in os.listdir(images_dbase_dir) if len(i) == 8] # filter .svn 
    dates.sort()
    
    for date in dates:
        
        tmp_str = ''
        feeds = [i for i in os.listdir('%s/%s' % (images_dbase_dir, date)) if len(i) == 2] # filter .svn 
        feeds.sort()
        
        try:
            
            for feed in feeds:
                
                movie_flag =  os.path.isdir('%s/%s/%s/movie' %  (images_dbase_dir, date, feed)) 
                smovie_flag = os.path.isdir('%s/%s/%s/smovie' % (images_dbase_dir, date, feed)) 
                snap_flag =   os.path.isdir('%s/%s/%s/snap' %   (images_dbase_dir, date, feed)) 
                
                if movie_flag or smovie_flag or snap_flag: 
                    tmp_str += '%s#' % feed
                    
                    if movie_flag:
                        tmp_str += '1#'
                    else:
                        tmp_str += '0#'
                    
                    if smovie_flag:
                        tmp_str += '1#'
                    else:
                        tmp_str += '0#'
                    
                    if snap_flag:
                        tmp_str += '1#'
                    else:
                        tmp_str += '0#'
                    
                    f_obj = open('%s/%s/%s/title' % (images_dbase_dir, date, feed)) 
                    tmp_str += '%s#' % f_obj.read()
                    f_obj.close()
                
        # if 'title' corrupted, skip the date
        except IOError:
                continue 
            
        if tmp_str != '': 
            coded_str += '$%s#%s' % (date, tmp_str)
        
    return coded_str
                
    
def movie_journal_data(images_dbase_dir, date_, feed, fps_time, fps):
    """
    Returns a coded string containing the start and end times for all movies
    for the defined 'date_' and 'feed'. The movies are named by start time ie
    185937 for 185937.swf, with an associated end time
    
    coded string consists of:
    
    $<HHMMSS start time>#<?? fps>#<HHMMSS end time> ... 
    
    args    : images_dbase_dir ... the images dbase dir 
              date_ ...            the required date_
              feed ...             the required feed
              fps_time ...         list of fps start times
              fps ...              list of fps
    excepts : 
    returns : coded string 
    """
    
    coded_str = ''
    journal_file = '%s/%s/%02i/movie_journal' % (images_dbase_dir, date_, feed) 
        
    if os.path.isfile(journal_file):
        f_obj = open(journal_file)
        journal = f_obj.readlines()
        f_obj.close()
    
        journal = [i.strip('\n$') for i in journal] # clean the journal
        movies = [i[:-4] for i in os.listdir('%s/%s/%02i/movie' % (images_dbase_dir, date_, feed))]
        movies.sort() # journal already sorted
        
        for movie in movies:
            
            try:
                while movie > journal[0]:
                    journal.pop(0)
            except IndexError: # movie in progress, ie no end time in journal
                break;
                
            # -2 seconds off movie end time to account for motion delay in executing 'on_movie_end'
            dt = datetime.datetime(1900, 1, 1, int(journal[0][:2]), int(journal[0][2:4]), int(journal[0][4:]))
            dt += datetime.timedelta(seconds = -2)
            movie_end = dt.strftime('%H%M%S')
            
            # check for - or 0 movie length
            if movie_end <= movie: continue
            
            fps_latest = 0 # scan for correct fps time slot
            for i in range(len(fps_time)):
                if  movie < fps_time[i]: break
                fps_latest = fps[i]
                    
            coded_str += '$%s#%s#%s' % (movie, fps_latest, movie_end)
        
    return coded_str
        

def smovie_journal_data(images_dbase_dir, date, feed, fps_time, fps):
    """   
    Returns a coded string containing data on the 'smovie' directory. This is an
    expensive operation so checks for a cached 'smovie_cache' first.
    
    coded string consists of:
    
    $<HHMMSS start>#<?? start items>#<?? fps>#<HHMMSS end>#<?? end items>...
    
    args    : images_dbase_dir ... the images dbase dir ;)
              date ...             the required date
              feed ...             the required feed
              fps_time ...         list of fps start times
              fps ...              list of fps
    excepts : 
    returns : string data blob 
    """
    
    # check for cached data
    smovie_cache = '%s/%s/%02i/smovie_cache' % (images_dbase_dir, date, feed)
    
    if os.path.isfile(smovie_cache):
        f_obj = open(smovie_cache)
        cache = f_obj.readlines()
        f_obj.close()
        coded_str = ''.join(cache).replace('\n', '')
        
    else:
        # generate the data the expensive way
        start, end = scan_image_dbase(images_dbase_dir, date, feed)
        
        # merge the 'movie' and 'fps' data
        coded_str = ''
        for i in range(len(start)):
            coded_str += '$%s' % start[i]
            coded_str += '#%s' % len(os.listdir('%s/%s/%02i/smovie/%s' % (images_dbase_dir, date, feed, start[i])))
        
            fps_latest = 0 # scan for correct fps time slot
            for j in range(len(fps_time)):
                if  start[i] < fps_time[j]: break
                fps_latest = fps[j]
            
            coded_str += '#%s' % fps_latest
            
            coded_str += '#%s' % end[i]
            coded_str += '#%s' % len(os.listdir('%s/%s/%02i/smovie/%s' % (images_dbase_dir, date, feed, end[i])))

    return coded_str
         

def scan_image_dbase(images_dbase_dir, date_, feed):  
    """
    Scan the 'images_dbase' directory looking for breaks that signify 
    different 'smovie's, store in 'start' and 'end' and return as a pair
    of identically sized lists
    
    args    : images_dbase_dir ... the images dbase dir 
              date ...             the required date
              feed ...             the required feed
    excepts : 
    returns : start ...            lists the movie start times
              end ...              lists the movie end times
    """
    
    start, end = [], []
    smovie_dir = '%s/%s/%02i/smovie' % (images_dbase_dir, date_, feed)
    
    if os.path.isdir(smovie_dir):
        movie_secs = os.listdir(smovie_dir)
        movie_secs.sort()
        
        if len(movie_secs) > 0:
            old_sec = 0
            old_movie_sec = 0
            
            for movie_sec in movie_secs:
                sec = int(movie_sec[0:2]) * 3600 + int(movie_sec[2:4]) * 60 + int(movie_sec[4:6])
                if sec != old_sec + 1:
                    start.append('%06s' % movie_sec)
                    if old_sec != 0: end.append('%06s' % old_movie_sec)
                old_sec = sec
                old_movie_sec = movie_sec
            end.append(movie_sec)  
    
    return start, end
    

def snap_journal_data(images_dbase_dir, date, feed):
    """
    Returns a coded string containing the start time and interval secs for all 
    snapshot setting changes for the defined 'date' and 'feed'. 
    
    coded string consists of:
    
    $<HHMMSS init time>#<?? interval secs> ...
    
    args    : images_dbase_dir ... the images dbase dir 
              date ...             the required date
              feed ...             the required feed
    excepts : 
    returns : coded string
    """
    
    coded_str = ''
    journal_file = '%s/%s/%02i/snap_journal' % (images_dbase_dir, date, feed)
        
    if os.path.isfile(journal_file):
        f_obj = open(journal_file)
        journal = f_obj.readlines()
        f_obj.close()
        
        journal = [i.strip('\n$') for i in journal] # clean the journal
        for line in journal:
            data = line.split('#')
            coded_str += '$%s#%s' % (data[0], data[1])
            
        # if today append 'end' time of now 
        if date == time.strftime('%Y%m%d'):
            # -60 secs due to 60 sec delay buffer in 'kmotion_hkd2'
            time_obj = time.localtime(time.time() - 60)
            coded_str += '$%s#0' % time.strftime('%H%M%S', time_obj)
    
    return coded_str
    

def fps_journal_data(images_dbase_dir, date, feed):  
    """   
    Parses 'fps_journal' and returns two lists of equal length, one of start 
    times, the other of fps values.
    
    args    : images_dbase_dir ... the images dbase dir ;)
              date ...             the required date
              feed ...             the required feed
    excepts : 
    returns : time ...             list of fps start times
              fps ...              list of fps
    """
         
    time_, fps = [], []
    journal_file = '%s/%s/%02i/fps_journal' % (images_dbase_dir, date, feed)
        
    f_obj = open(journal_file)
    journal = f_obj.readlines()
    f_obj.close()
    
    journal = [i.strip('\n$') for i in journal] # clean the journal
    
    for line in journal:
        data = line.split('#')
        time_.append(data[0])
        fps.append(int(data[1]))
        
    return time_, fps
        

def mutex_acquire(kmotion_dir):
    """ 
    Aquire the 'www_rc' mutex lock, very carefully
    
    args    : kmotion_dir ... the 'root' dir of kmotion
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
        f_obj = open('%s/www/mutex/www_rc/%s' % (kmotion_dir, os.getpid()), 'w')
        print >> f_obj, ''
        f_obj.close()
            
        # wait ... see if another lock has appeared, if so remove our lock
        # and loop
        time.sleep(0.1)
        if check_lock(kmotion_dir) == 1:
            break
        os.remove('%s/www/mutex/www_rc/%s' % (kmotion_dir, os.getpid()))
        # random to avoid mexican stand-offs
        time.sleep(float(random.randint(01, 40)) / 1000)
            
        
def mutex_release(kmotion_dir):
    """ 
    Release the 'www_rc' mutex lock
    
    args    : kmotion_dir ... the 'root' dir of kmotion
    excepts : 
    return  : none
    """
    
    if os.path.isfile('%s/www/mutex/www_rc/%s' % (kmotion_dir, os.getpid())):
        os.remove('%s/www/mutex/www_rc/%s' % (kmotion_dir, os.getpid()))
       
        
def check_lock(kmotion_dir):
    """
    Return the number of active locks on the www_rc mutex, filters out .svn
    
    args    : kmotion_dir ... kmotions root dir
    excepts : 
    return  : num locks ... the number of active locks
    """
    
    files = os.listdir('%s/www/mutex/www_rc' % kmotion_dir)
    files.sort()
    if len(files) > 0 and files[0] == '.svn': # strip the .svn dir
        files.pop(0)
    return len(files)
        
        

# Module test code

if __name__ == '__main__':
    
    class Test_Class1(object):
    
        def __init__(self):
            self.filename = '../null/null'
            self.form = {'date': time.strftime('%Y%m%d'), 'cam': 1, 'func': 'avail'}
            
    class Test_Class2(object):
        def __init__(self):
            self.filename = '../null/null'
            self.form = {'date': time.strftime('%Y%m%d'), 'cam': 1, 'func': 'index'}

    print '\nModule self test ... \'avail\' ...\n'
    print index(Test_Class1())

    print '\nModule self test ... \'index\' ...\n'
    print index(Test_Class2())
    














