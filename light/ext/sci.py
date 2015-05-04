import numpy as np

def np_init_and_store_seed(e, seed):
    np.random.seed(seed)
    e["seed"] = seed
    return e
