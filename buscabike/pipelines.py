# -*- coding: utf-8 -*-

import re
import logging
import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem


PHONE = r'([\(]?\d{2,3}[\)]?\s)?(\d\s)?\d{4,5}([\s|\-])?(\s\-\s)?\d{3,5}.'


class ContactsPipeline(object):
    def process_item(self, item, spider):
        pattern = re.compile(PHONE)
        match = pattern.search(item['description'])
        if match:
            item['phone'] = match.group().strip()

        return item


class MongoPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(settings['MONGODB_URI'])
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]
        logging.debug("Database connected.")

    def process_item(self, item, spider):
        for data in item:
            if not data:
                raise DropItem("Missing {0}".format(data))
        self.collection.update_one(
            {'url': item['url']},
            {
                "$set": {
                    'title': item.get('title'),
                    'posted_at': item.get('posted_at'),
                    'created_at': item.get('created_at'),
                    'url': item.get('url'),
                    'price': item.get('price'),
                    'owner': item.get('owner'),
                    'phone': item.get('phone'),
                    'description': item.get('description'),
                    'image': item.get('image'),
                    'type': item.get('property_type'),
                    'city': item.get('city'),
                    'cep': item.get('cep'),
                    'district': item.get('district')
                }
            },
            upsert=True
        )
        logging.debug("Property added to MongoDB database!")

        return item
