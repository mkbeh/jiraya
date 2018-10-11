import logging


# Func which log func success result.
def log(func):
    def wrapper(self, *args, **kwargs):
        logger = logging.getLogger('Main')
        logger.setLevel(logging.INFO)

        fh = logging.FileHandler('jiraya.log')
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        if func(self, *args, **kwargs) is None:
            logger.info('Success status: %s' % 'DONE')

    return wrapper

