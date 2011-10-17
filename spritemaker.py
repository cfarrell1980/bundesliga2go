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
import os,Queue,threading,urllib2,tempfile,shutil
try:
  import Image
except ImportError:
  raise ImportError,\
    'PIL is needed to create the sprites. Install python-imaging'
from bundesligaAPI import bundesligaAPI
api = bundesligaAPI()
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
    self.image_height = 0
    self.image_width = 0
    self.iconmap = []
    self.tmpdir = tempfile.mkdtemp()
    self.default_icon = os.path.join(os.getcwd(),
                      '/static/images/default_icon.png')
        
  def syncIcons(self):
    ''' This method obtains information about each team in the League and 
        Season requested. It then uses threads to download all of the icons in
        parallel and stores them to @tmpdir
    '''
    try:
      teams = api.getTeams(self.league,self.season)
    except:
      raise
    else:
      if not len(teams):
        raise StandardError, "No teams found locally. Did you sync?"
      for i in range(len(teams)):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()

      for team in teams:
        if team['iconURL']:
          base = os.path.basename(team['iconURL'])
          team['target'] = os.path.join(self.tmpdir,base)
          queue.put(team)
          self.iconmap.append([team['shortName'],team['target']])
        else:
          print "No iconURL for %s"%team['shortName']
          self.iconmap.append([team['shortName'],self.default_icon])
      queue.join()
      
    
  def makeSprite(self,targetdir=os.path.join(os.getcwd(),'static/images/')):
    # read all of the individual team icons into memory and get properties
    images =  []
    for imglist in self.iconmap:
      try:
        images.append(Image.open(imglist[1]))
      except IOError:
        print "IOError opening %s. Using default icon instead..."%imglist[1]
        images.append(self.default_icon)
    self.image_width, self.image_height = images[0].size
    master_width = self.image_width
    #seperate each image with lots of whitespace
    master_height = (self.image_height * len(images) * 2) - self.image_height
    master = Image.new(
      mode='RGBA',
      size=(master_width, master_height),
      color=(0,0,0,0)) # fully transparent
    # add the images to the master image and write master.png and master.gif
    for count, image in enumerate(images):
      location = self.image_height*count*2
      master.paste(image,(0,location))
    master_png_target = os.path.join(targetdir,'%s_%s.png'%(self.league,
          str(self.season)))
    master.save(master_png_target)
    shutil.rmtree(self.tmpdir,ignore_errors=True)
    
    
  def makeCSS(self,targetdir=os.path.join(os.getcwd(),'static/css/')):
    # create the css code needed to define the icon sprite
    bg_url = '%s_%s.png'%(self.league,str(self.season))
    cssHead = " span.icon { margin:0 10px; vertical-align:middle;\
                line-height: 20px; border: 2px solid #cccccc;\n\
                -moz-border-radius:50%; -webkit-border-radius:20px;"
    cssHead=cssHead+"background: url(../images/%s)"%bg_url
    cssHead=cssHead+"no-repeat top left; }"
    # create the css code needed to interpret the sprite
    cssTemplate = " span.icon-%s { background-position: 0px -%dpx;\
                    width: 20px; height: 20px; display:inline-block; }\n"
    # write the css code to string
    css_str = []
    iterator = 0
    for teamlist in self.iconmap:
      scut,filename = teamlist[0],teamlist[1]
      location = (self.image_height*iterator*2)
      css_str.append(cssTemplate%(scut,location))
      iterator+=1

    # open the target css file
    fd = open(os.path.join(targetdir,
        "%s_%s.css"%(self.league,str(self.season))),'w')
    fd.write(cssHead+"\n")
    fd.write("\n".join(css_str))
    fd.close()
