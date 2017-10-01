import os
import time
import json
import app_utils
logger = app_utils.logger

class Cache:
    file_folder = ''
    file_name = 'config.json'
    file_found = False

    config = {}

    cache_timestamp_key = 'timestamp'
    cache_content_key = 'value'

    cache_cf_app_info = 'cf_app_info'


    def __init__(self):
        self.file_path = os.path.join(self.file_folder+ self.file_name)
        self.file_found = os.path.isfile(self.file_path)


        if self.file_found:
            logger.log('reading')
            self.config = json.load(open(self.file_path))



    def read_cache(self, value):
        if value in self.config:
            return self.config[value][self.cache_content_key]


    def config_factory(self, content):
        new_config = {
            self.cache_timestamp_key: time.time(),
            self.cache_content_key : content
        }
        return new_config


    def write_cache(self, value, content):
        if self.file_folder != '' and not os.path.exists(self.file_folder):
            os.makedirs(self.file_path)

        f = open(self.file_path, 'w')
        if value in self.config:
            self.config[value][self.cache_content_key] = content
            self.config[value][self.cache_timestamp_key] = time.time()
        else:
            self.config[value] = self.config_factory(content)

        f.write(json.dumps(self.config))
        f.close()


