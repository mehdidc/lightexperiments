from lightexperiments.light import Light
import logging

__all__ = ["process_waiting_list"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def process_waiting_list():
    light = Light()
    light.launch()
    if light.db_loaded is False:
        logger.error("Cant load the db...")
        return
    light.process_waiting_list()

if __name__ == "__main__":
    process_waiting_list()
