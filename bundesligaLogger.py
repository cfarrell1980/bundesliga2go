import logging,os
here = "/space/repos/bundesliga2go/"
logfile = os.path.abspath(os.path.join(here,"bundesliga2go.log"))
logger = logging.getLogger('bundesliga2go')
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

