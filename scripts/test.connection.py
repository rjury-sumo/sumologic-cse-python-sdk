import argparse
import logging
import os
from sumologiccse.sumologiccse import SumoLogicCSE

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel('DEBUG')

from sumologiccse.sumologiccse import SumoLogicCSE

# defaults for accessId and accessKey
cse=SumoLogicCSE()

logger.info(f"Test endpoint was: connection to Sumo Logic CSE API at {cse.endpoint}")

