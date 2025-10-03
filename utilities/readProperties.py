import configparser
import os

config = configparser.RawConfigParser()
config.read(os.path.abspath(os.curdir)+'\\configurations\\config.ini')

class ReadConfig:
    @staticmethod
    def getApplicationURL():
        url=config.get('commonInfo', 'baseurl')
        return url

    @staticmethod
    def getUsername():
        username=config.get('commonInfo', 'username')
        return username

    @staticmethod
    def getPassword():
        password=config.get('commonInfo', 'password')
        return password