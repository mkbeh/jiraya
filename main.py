# -*- coding: utf-8 -*-
import time
import re
import functools

import requests

from datetime import timedelta, datetime

from bs4 import BeautifulSoup
from torrequest import TorRequest

from libs.pymongodb import pymongodb
from libs import decorators
from libs import utils


class Parser(object):
    def __init__(self):
        self.url = 'https://bitjournal.media/wp-admin/admin-ajax.php'
        self.mongo = pymongodb.MongoDB('bitjournal')
        self.last_new = None
        self.next = False

        self.today = datetime.today().strftime('%d-%m-%Y').zfill(2)
        self.yesterday = (datetime.today() - timedelta(1)).strftime('%d-%m-%Y').zfill(2)
        self.before_yesterday = (datetime.today() - timedelta(2)).strftime('%d-%m-%Y').zfill(2)

    @staticmethod
    def get_html(url, page_num):
        """
        Method which send GET request to specific url and return html.
        :param url:
        :param page_num:
        :return:
        """
        time.sleep(3)

        data = {
            "action": "loadNewsPosts",
            "page": "{}".format(page_num),
        }

        try:
            html = requests.post(url, data=data).content.decode('utf-8')
        except Exception as e:
            print(e)

            with TorRequest(proxy_port=9050, ctrl_port=9051, password=None) as tr:
                tr.reset_identity()
                html = tr.post(url, data=data).content

        return html

    def write_data(self, **kwargs):
        """
        Record processed data.
        :param kwargs:
        :return:
        """
        self.mongo.insert_one(kwargs, 'news')

    def get_last_new(self):
        """
        Get last new from db by current date. If there are no news on current date - trying to get yesterday news.
        Else - write clear list into last_new.
        :return:
        """
        self.last_new = self.mongo.find({'date': self.today}, 'news')

        if not self.last_new:
            self.last_new = self.mongo.find({'date': self.yesterday}, 'news')

            if not self.last_new:
                self.last_new = self.mongo.find({'date': self.before_yesterday}, 'news')

    def parse(self, page_num):
        """
        Parse data by page number. Processing and recording data into db.
        :param page_num:
        :return:
        """
        bs_obj = BeautifulSoup(self.get_html(self.url, page_num), 'lxml')
        items = bs_obj.findAll('div', {'class': 'item'})

        imgs_src = []
        titles = []
        full_desc_links = []
        dates = []

        for item in items:
            ad = item.find(text='Реклама')

            if ad:
                continue

            # When the link for the full description is missing.
            try:
                full_desc_link = item.find('a', {'href': re.
                                           compile('\shttps://bitjournal\.media/\d\d-\d\d-\d{4}/.*/')})['href'].strip()
            except AttributeError:
                continue

            img_src = item.find('img', {'src': re.compile('^https://bitjournal\.media/wp-content/uploads/')})['src']
            title = item.find('img', {'src': re.compile('^https://bitjournal\.media/wp-content/uploads/')})['alt']
            date = utils.get_date(full_desc_link)

            # Append data.
            full_desc_links.append(full_desc_link)
            imgs_src.append(img_src)
            titles.append(title)
            dates.append(date)

        # Processing and recording data.
        data_lst = [titles, full_desc_links, imgs_src, dates]

        if self.last_new:  # When database is not clear.
            try:
                index = titles.index(self.last_new[0]['title'])
                self.next = False

                # Remove unnecessary items.
                data_lst = list(map(functools.partial(utils.del_items_by_index, index=index), data_lst))

            except ValueError:  # Last new from db not in current parsed list.
                self.next = True

            if data_lst[0]:  # Not clear lst.
                # Write data into db.
                for i in range(len(data_lst[0])):
                    self.write_data(title=data_lst[0][i], full_desc_link=data_lst[1][i],
                                    img_src=data_lst[2][i], date=data_lst[3][i])

        else:  # When database is clear or no records for current and yesterday date.
            for i in range(len(data_lst[0])):
                self.write_data(title=data_lst[0][i], full_desc_link=data_lst[1][i],
                                img_src=data_lst[2][i], date=data_lst[3][i])

    @decorators.log
    def run(self):
        """
        Try to get last new from db and parse data.
        :return:
        """
        self.get_last_new()     # Get last new from db.

        # Parse data.
        page_count = 0

        while True:
            self.parse(page_count)

            if self.next is False:
                break

            page_count += 1


if __name__ == '__main__':
    try:
        Parser().run()
    except:
        utils.logger('Success status: %s' % 'ERROR', 'jiraya.log')
