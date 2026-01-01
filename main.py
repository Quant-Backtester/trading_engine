#STL
import logging


#Custom
from common.logging_config import setup_engine_logging
from core.engine import Engine



def run_engine():
    setup_engine_logging()
    engine = Engine()



    


if __name__ == "__main__":
    run_engine()