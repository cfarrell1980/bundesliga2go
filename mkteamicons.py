#!/usr/bin/python
import os,Image # requires python-imaging (openSUSE name for PIL)
from urllib2 import Request, urlopen, URLError, HTTPError
from bundesligaAPI import BundesligaAPI
from bundesligaHelpers import shortcuts
api = BundesligaAPI()
tmp_team_dir = os.path.join(os.getcwd(),'tmp_team_images')
final_sprite_dir = os.path.join(os.getcwd(),'static/img/')
icon_map = []
target_css = os.path.abspath(os.path.join(os.getcwd(),'static/css/teamicons.css'))

def saveIcon(icon_url,team_id,file_mode="b"):
  remote_file_name = os.path.basename(icon_url)
  target_local_file = os.path.join(tmp_team_dir,remote_file_name)
  shortcut = shortcuts[team_id]
  req = Request(icon_url)
  try:
    print "Getting %s"%icon_url
    f = urlopen(req)
    local_file = open(target_local_file, "w" + file_mode)
    local_file.write(f.read())
    local_file.close()
  except HTTPError, e:
    print "HTTP Error:",e.code , icon_url
  except URLError, e:
    print "URL Error:",e.reason , icon_url
  else:
    icon_map.append([shortcut,target_local_file])

teams = api.getTeams('bl1',2011)
for team in teams:
  saveIcon(team.iconURL,team.id)

# read all of the individual team icons into memory and get properties
images = [Image.open(filename) for cssClass, filename in icon_map]
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
    color=(0,0,0,0))  # fully transparent

print "created."

# add the images to the master image and write master.png and master.gif
for count, image in enumerate(images):
    location = image_height*count*2
    print "adding %s at %d..." % (icon_map[count][1], location),
    master.paste(image,(0,location))
    print "added."
print "done adding icons."
master_png_target = os.path.join(final_sprite_dir,'teams.png')
print "saving teams.png to %s"%master_png_target,
master.save(master_png_target)
print "saved!"

# create the css code needed to define the icon sprite
cssHead = '''span.icon { margin:0 10px; vertical-align:middle; line-height: 20px; border: 2px solid #cccccc; -moz-border-radius:50%; -webkit-border-radius:20px;  background: url(../img/teams.png) no-repeat top left; }
'''
# create the css code needed to interpret the sprite
cssTemplate = "span.icon-%s { background-position: 0 %d; width: 20px; height: 20px; display:inline-block; }\n"
# write the css code to string
css_code = cssHead
css_str = ""
iterator = 0
for teamlist in icon_map:
  scut,filename = teamlist[0],teamlist[1]
  location = (image_height*iterator*2)
  css_str = cssTemplate%(scut,location)
  css_code = css_code + css_str
  iterator+=1

# open the target css file
fd = open(target_css,'w')
fd.write(css_code)
fd.close()
