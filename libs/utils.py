# -*- coding: utf-8 -*-
import logging
import re


# Func which logging message into file.
def logger(msg, file):
    logger = logging.getLogger('Main')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(file)
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info(msg)


def del_items_by_index(seq, index):
    """
    Delete items from sequence starting with index.
    :param seq:
    :param index:
    :return:
    """
    del seq[index:]

    return seq


def get_date(url):
    pattern = re.compile(r'\d\d-\d\d-\d{4}')
    res = re.search(pattern, url).group()

    return res
