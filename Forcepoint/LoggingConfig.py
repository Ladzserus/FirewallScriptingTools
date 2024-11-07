import logging, sys

# initialize the logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a message format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# create console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)

# create file handler
fh = logging.FileHandler("Forcepoint_SMC_Tool.log", encoding="utf-8")
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

# add the handlers to the logger object
logger.addHandler(ch)
logger.addHandler(fh)
