import npyscreen
import curses
import threading
import cloud_foundry_wrapper
import json
from app_utils import *

class PredixAppForm(npyscreen.Form):
    current_app_info = {}

    def afterEditing(self):
        self.parentApp.setNextForm(None)

    def create(self):
        self.predix_app_list = self.add(npyscreen.MultiLineAction, rely=2, name='Predix Apps', relx=2, max_width=50)
        self.predix_app_env = self.add(npyscreen.BoxTitle, rely=2, name='Predix Env', relx=54, max_width=100)
        self.buildPredixAppsList()


    def beep(self):
        print(self.predix_app_list.value)
        curses.beep()

    def buildPredixAppsList(self):
        self.predix_app_list.actionHighlighted = self.predixAppListHighlighted
        self.predix_app_list.values = ['loading...']
        self.predix_app_list.display()

    def predixAppListHighlighted(self, act_on_this, key_press):
        self.updateEnvList(act_on_this)

    def updateEnvList(self, key):
        if key in self.current_app_info:
            self.predix_app_env.values = get_pretty_print(self.current_app_info[key][cf.cf_app_env_key]).split("\n")
        else:
            self.beep()

        self.predix_app_env.display()

    def updatePredixAppList(self, newAppsList):
        self.predix_app_list.values = newAppsList





class MyApplication(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', PredixAppForm, name='Predix App Viewer')

    def update(self, app_info):
        self.getForm('MAIN').current_app_info = app_info
        keys = app_info.keys()
        keys.sort()
        self.getForm('MAIN').predix_app_list.values = keys
        self.getForm('MAIN').updateEnvList(keys[0])
        self.getForm('MAIN').predix_app_list.display()








class LogToFile:
    def __init__(self):
        self.f = open('log.txt', 'w')

    def log(self, value):
        self.f.write(str(value) + '\n')


logger = LogToFile()
cf = cloud_foundry_wrapper.CF()
TestApp = MyApplication()
cf.setUpdateCall(TestApp.update)
threading.Thread(target=cf.update).start()
TestApp.run()
