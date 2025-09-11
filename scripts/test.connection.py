import logging

from sumologiccse.sumologiccse import SumoLogicCSE

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel("DEBUG")


# defaults for accessId and accessKey
cse = SumoLogicCSE()

logger.info(f"Test endpoint was: connection to Sumo Logic CSE API at {cse.endpoint}")
