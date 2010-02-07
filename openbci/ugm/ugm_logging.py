import logging
def get_logger(p_name):
    logger = logging.getLogger(p_name)
    ch = logging.StreamHandler()

    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
