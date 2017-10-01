import npyscreen
import curses
import threading

import time
from npyscreen import TreeData
import cloud_foundry_wrapper
import json
from app_utils import *

class PredixAppForm(npyscreen.Form):
    current_app_info = {}


    def afterEditing(self):
        self.parentApp.setNextForm(None)

    def create(self):
        self.predix_app_list = self.add(npyscreen.MultiLineAction, rely=2, name='Predix Apps', relx=2, max_width=50)
        self.predix_app_env_tree = self.add(npyscreen.MLTreeAction, rely=2, name='Predix Env', relx=self.predix_app_list.width + 4,max_height=int(self.max_y/2), max_width=100)
        self.buildPredixAppsList()
        self.predix_app_env_tree.actionHighlighted = self.onTreeAction

        self.current_app_details = self.add(npyscreen.MultiLineAction,
                                            relx=self.predix_app_env_tree.relx,
                                            rely=self.predix_app_env_tree.rely + self.predix_app_env_tree.height ,
                                            max_height=int(self.max_y/3),
                                            max_width=100)


    def beep(self):
        print(self.predix_app_list.value)
        curses.beep()

    def updateDetails(self, appId):
        lst = []

        if str(appId) in self.current_app_info:
            for key, value in self.current_app_info[str(appId)][cf.cf_app_details_key].iteritems():
                lst.append("%s: %s" % (key, value))
            self.current_app_details.values = lst
            logger.log(lst)
            logger.log('update')
        self.current_app_details.display()


    def buildPredixAppsList(self):
        self.predix_app_list.actionHighlighted = self.predixAppListHighlighted
        self.predix_app_list.values = ['loading...']
        self.predix_app_list.display()

    def predixAppListHighlighted(self, act_on_this, key_press):
        self.updateEnvTree(act_on_this)
        self.updateDetails(act_on_this)


    def updateEnvTree(self, appId):
        if self.current_app_info.__contains__(str(appId)):
            dictionary = self.current_app_info[str(appId)][cf.cf_app_env_key]
            self.predix_app_env_tree.values = dictToTreeData(dictionary)
            self.predix_app_env_tree.display()


    def onTreeAction(self, act_on_this, key_press):
        if act_on_this.name is not None:
            copyToClipboard(act_on_this.name)


    def updatePredixAppList(self, newAppsList):
        self.predix_app_list.values = newAppsList
        self.predix_app_list.display()





class MyApplication(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', PredixAppForm, name='Predix App Viewer')

    def update(self, app_info):
        self.getForm('MAIN').current_app_info = app_info
        keys = app_info.keys()
        keys.sort()
        self.getForm('MAIN').updatePredixAppList(keys)
        self.getForm('MAIN').updateEnvTree(keys[0])
        self.getForm('MAIN').updateDetails(keys[0])



def startCfUpdate(cf):
    time.sleep(.1)
    cf.update()

logger = LogToFile()
cf = cloud_foundry_wrapper.CF()
TestApp = MyApplication()
cf.setUpdateCall(TestApp.update)
threading.Thread(target=startCfUpdate, args=(cf, )).start()
TestApp.run()
