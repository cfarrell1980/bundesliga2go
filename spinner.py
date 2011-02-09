import sys,time
def draw_ascii_spinner(delay=0.1):
  for char in '/-\|': # there should be a backslash in here.
    sys.stdout.write(" ")
    sys.stdout.write(char)
    sys.stdout.flush()
    time.sleep(delay)
    sys.stdout.write('\r') # this should be backslash r.
while True:
  draw_ascii_spinner()
