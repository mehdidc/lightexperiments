from lightexperiments.light import Light

__all__ = ["process_waiting_list"]


def process_waiting_list():
    light = Light()
    light.launch()
    light.process_waiting_list()
