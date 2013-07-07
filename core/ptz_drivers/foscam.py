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
PT(Z) driver for Foscam network camera

This is a difficult PT(Z) to work with, it just has 'home' and relative
movements, no absolutes, no step values. Its been interesting :)
"""

import os, urllib, cPickle, time
import logger

log_level = 'WARNING'
logger = logger.Logger('foscam', log_level)

URL_CGI_PLUS_X =  '/decoder_control.cgi?command=6'
URL_CGI_STOP_PLUS_X =  '/decoder_control.cgi?command=7'

URL_CGI_MINUS_X = '/decoder_control.cgi?command=4'
URL_CGI_STOP_MINUS_X = '/decoder_control.cgi?command=5'

URL_CGI_PLUS_Y =  '/decoder_control.cgi?command=0'
URL_CGI_STOP_PLUS_Y =  '/decoder_control.cgi?command=1'

URL_CGI_MINUS_Y = '/decoder_control.cgi?command=2'
URL_CGI_STOP_MINUS_Y = '/decoder_control.cgi?command=3'

URL_CGI_CALIB =   '/decoder_control.cgi?command=25'


def rel_xy(feed, feed_url, feed_proxy, feed_lgn_name, feed_lgn_pw, feed_x, feed_y, step_x, step_y):
    """
    Set the PT(Z) relative to the last position
    
    args    : feed, 
              feed_url,   
              feed_proxy, 
              feed_lgn_name, 
              feed_lgn_pw, 
              feed_x, 
              feed_y
    excepts : 
    return  : 
    """

    current_x, current_y, step_x, step_y = load_xy_step_xy(feed)
    
    # grab 'feed_x', 'feed_y' values as step values, a workaround
    if feed_x != 0:
        step_x = abs(feed_x)
        
    elif feed_y != 0:
        step_y = abs(feed_y)
        
    new_x = current_x + feed_x
    new_y = current_y + feed_y
    move_rel_xy(feed, current_x, current_y, new_x, new_y, step_x, step_y, feed_url, feed_proxy, feed_lgn_name, feed_lgn_pw)
    logger.log('rel_xy() - feed:%s, x:%s, y:%s' % (feed, new_x, new_y), 'DEBUG')
    save_xy_step_xy(feed, new_x, new_y, step_x, step_y)
    
         
def abs_xy(feed, feed_url, feed_proxy, feed_lgn_name, feed_lgn_pw, feed_x, feed_y, step_x, step_y):
    """
    Set the PT(Z) absolutely to  position
    
    args    : feed, 
              feed_url, 
              feed_proxy,   
              feed_lgn_name, 
              feed_lgn_pw, 
              feed_x, 
              feed_y
    excepts : 
    return  : 
    """
    
    logger.log('abs_xy() - feed:%s, x:%s, y:%s' % (feed, feed_x, feed_y), 'DEBUG')
    
    current_x, current_y, step_x, step_y = load_xy_step_xy(feed)
    move_rel_xy(feed, current_x, current_y, feed_x, feed_y, step_x, step_y, feed_url, feed_proxy, feed_lgn_name, feed_lgn_pw)
    save_xy_step_xy(feed, feed_x, feed_y, step_x, step_y)
    
    
def cal_xy(feed, feed_url, feed_proxy, feed_lgn_name, feed_lgn_pw, feed_x, feed_y, step_x, step_y):
    """
    Set the PT(Z) to the calibration position
    
    args    : feed, 
              feed_url, 
              feed_proxy, 
              feed_lgn_name, 
              feed_lgn_pw, 
              feed_x, 
              feed_y
    excepts : 
    return  : 
    """
    
    logger.log('cal_xy() - feed:%s, x:%s, y:%s' % (feed, feed_x, feed_y), 'DEBUG')
    
    touch_url(feed_url, URL_CGI_CALIB, '', 0, feed_proxy, feed_lgn_name, feed_lgn_pw)
    current_x, current_y, step_x, step_y = load_xy_step_xy(feed)
    save_xy_step_xy(feed, 0, 0, step_x, step_y)
    
    time.sleep(70)
    
    
def move_rel_xy(feed, current_x, current_y, new_x, new_y, step_x, step_y, feed_url, feed_proxy, feed_lgn_name, feed_lgn_pw):
    """
    Move the camera - hopefully :) 
    
    args    : feed,
              current_x, 
              current_y,
              new_x,
              new_y,
              step_x,
              step_y,
              feed_url,
              feed_proxy,
              feed_lgn_name,
              feed_lgn_pw  
    excepts : 
    return  :
    """
      
    if new_x > current_x:
        touch_url(feed_url, URL_CGI_PLUS_X, URL_CGI_STOP_PLUS_X, new_x - current_x, feed_proxy, feed_lgn_name, feed_lgn_pw)
    elif new_x < current_x:
        touch_url(feed_url, URL_CGI_MINUS_X, URL_CGI_STOP_MINUS_X, current_x - new_x, feed_proxy, feed_lgn_name, feed_lgn_pw)
        
    time.sleep(abs(new_x - current_x) * 0.1)
    
    if new_y > current_y:
        touch_url(feed_url, URL_CGI_PLUS_Y, URL_CGI_STOP_PLUS_Y, new_y - current_y, feed_proxy, feed_lgn_name, feed_lgn_pw)
    elif new_y < current_y:
        touch_url(feed_url, URL_CGI_MINUS_Y, URL_CGI_STOP_MINUS_Y, current_y - new_y, feed_proxy, feed_lgn_name, feed_lgn_pw)
    
    time.sleep(abs(new_y - current_y) * 0.1)
    
    
def touch_url(feed_url, cgi_start_url, cgi_stop_url, diff, feed_proxy, feed_lgn_name, feed_lgn_pw):
    """
    Touch the URL created by merging 'feed_url, and 'cgi_url' 

    args    : feed_url,
              cgi_start_url, 
              cgi_stop_url,
              diff,
              feed_proxy,
              feed_lgn_name,
              feed_lgn_pw  
    excepts : 
    return  :
    """
     
    base_url = feed_url.split('/video.cgi')[0]
    
    # add user name and password if supplied
    url_prot, url_body = base_url[:7], base_url[7:]
    
    if  feed_lgn_name != '':
        url_prot += '%s:%s@' % (feed_lgn_name, feed_lgn_pw)
        
    base_url = '%s%s' % (url_prot, url_body)
        
    # nasty bodge to get foscam to step, start moving, pause, stop moving
    logger.log('touch_url() - %s%s' % (base_url, cgi_start_url), 'DEBUG')
    f_obj = urllib.urlopen('%s%s' % (base_url, cgi_start_url))
    time.sleep(0.2)
    f_obj.close()
    
    if cgi_stop_url != '':
        
        time.sleep(diff * 0.05)
        
        logger.log('touch_url() - %s%s' % (base_url, cgi_stop_url), 'DEBUG')
        f_obj = urllib.urlopen('%s%s' % (base_url, cgi_stop_url))
        time.sleep(0.2)
        f_obj.close()
        
    
    
def save_xy_step_xy(feed, x, y, step_x, step_y):
    """
    Save absolute 'x', 'y' and 'step_x', 'step_y' as '<feed>xy'
    
    args    : feed,
              x, y, 
              step_x, 
              step_y
    excepts : 
    return  : 
    """
    
    f_obj = open('ptz_drivers/abs_xy/%02ixy' % feed, 'w')
    cPickle.dump([x, y, step_x, step_y], f_obj)
    f_obj.close()
    
    
def load_xy_step_xy(feed):
    """
    Load saved absolute 'x', 'y' and 'step_x', 'step_y' from '<feed>xy', 
    default to zeros if none saved
    
    args    : feed
    excepts : 
    return  : x, y, step_x, step_y
    """
    
    data = [0, 0, 0, 0]
    if os.path.isfile('ptz_drivers/abs_xy/%02ixy' % feed):
        f_obj = open('ptz_drivers/abs_xy/%02ixy' % feed)
        data = cPickle.load(f_obj)
        f_obj.close()
        
    if len(data) != 4:
        data = [0, 0, 0, 0]
        
    return (data[0], data[1], data[2], data[3])
    
  





