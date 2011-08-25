# -*- coding: utf-8 -*-

'''
Copyright (c) 2011, Ciaran Farrell, Vladislav Lewin
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

Neither the name of the authors nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import os,Queue,threading,urllib2
try:
  import Image
except ImportError:
  raise ImportError,\
    'PIL is needed to create the sprites. Install python-imaging'
from api import localService
localService = localService()
queue = Queue.Queue()

class ThreadUrl(threading.Thread):
  def __init__(self, queue):
    ''' This class is based on an example from
    http://samratjp.posterous.com/a-multi-threaded-python-script-for-downloadin
    '''
    threading.Thread.__init__(self)
    self.queue = queue
     
  def run(self):
    try:
      while True:
        team = self.queue.get()
        url = urllib2.urlopen(team['iconURL'])
        icon = url.read()
        output=open(team['target'],'wb')
        output.write(icon)
        url.close()
        output.close()
        self.queue.task_done()
    except:
      self.queue.task_done()

class Sprite:
  def __init__(self,league,season):
    self.league = league
    self.season = season
    self.iconmap = []
    
        
  def syncIcons(self,tmpdir=os.path.join(os.getcwd(),'iconstore')):
    ''' @ŧmpdir:  the local directory where icon images are stored. This must
                  exist!
        This method obtains information about each team in the League and 
        Season requested. It then uses threads to download all of the icons in
        parallel and stores them to @tmpdir
    '''
    try:
      teams = localService.getTeams(self.league,self.season)
    except:
      raise
    else:
      for i in range(len(teams)):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()

      for team in teams:
        if team['iconURL']:
          base = os.path.basename(team['iconURL'])
          team['target'] = os.path.join(tmpdir,base)
          queue.put(team)
          self.iconmap.append([team['shortName'],team['target']])
        else:
          print "No iconURL for %s"%team['shortName']
      queue.join()
      
    
  def makeSprite(self,srcdir=os.path.join(os.getcwd(),'iconstore'),
                targetdir=os.path.join(os.getcwd(),'static/images/')):
    # read all of the individual team icons into memory and get properties
    images = [Image.open(filename) for cssClass, filename in self.iconmap]
    print "%d images will be combined." % len(images)
    image_width, image_height = images[0].size
    print "all images assumed to be %d by %d." % (image_width, image_height)
    master_width = image_width
    #seperate each image with lots of whitespace
    master_height = (image_height * len(images) * 2) - image_height
    print "the master image will by %d by %d" % (master_width, master_height)
    print "creating image...",
    master = Image.new(
      mode='RGBA',
      size=(master_width, master_height),
      color=(0,0,0,0)) # fully transparent
    print "created."
    # add the images to the master image and write master.png and master.gif
    for count, image in enumerate(images):
      location = image_height*count*2
      print "adding %s at %d..." % (self.iconmap[count][1], location),
      master.paste(image,(0,location))
      print "added."
    print "done adding icons."
    master_png_target = os.path.join(targetdir,'%s_%s.png'%(self.league,
          str(self.season)))
    print "saving teams.png to %s"%master_png_target,
    master.save(master_png_target)
    print "saved!"
    
  def makeCSS(self,targetdir=os.path.join(os.getcwd(),'static/css/')):
    pass
