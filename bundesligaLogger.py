import logging
logger = logging.getLogger('bundesliga2go')
hdlr = logging.FileHandler('bundesliga2go.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

