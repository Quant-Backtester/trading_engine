#STL
import logging


#Custom
from core import setup_engine_logging, Engine



def run_engine():
    setup_engine_logging()
    logger = logging.getLogger(__name__)
    engine = Engine()






if __name__ == "__main__":
    run_engine()