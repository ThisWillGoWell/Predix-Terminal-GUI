import npyscreen
import curses
import subprocess
import threading
import json

cf_app_requested_state_key = 'state'
cf_app_memory_key = 'memory'
cf_app_disk_key = 'disk'
cf_app_url_key = 'url'
cf_app_instance_key = 'instance'
cf_app_env_key = 'env'
cf_app_env_system_provided_key = 'System-Provided'
cf_app_env_system_vcap_services_key = 'VCAP_SERVICES'
cf_app_env_system_vcap_app_key = 'VCAP_APPLICATION'
cf_app_env_user_provided_key = 'User-Provided'

cf_app_list_command = 'cf a'
cf_app_info_command = 'cf env'


class CF:
    def __init__(self):
        """Initialize the CF interface
        define the state variables of the cf app, currently not used as an object
        """
        self.current_app_info = {}
        self.org = ""
        self.space = ""
        self.user = ""
        self.update()

    def update(self):
        """Update the working CF Cache
        Run the cf commands to so the dic can be created
        Then call the update function of the Test app to update the front ent
        don't really like that the test app is coupled in the cf interface but easy to do it
        :return:  None
        """

        self.current_app_info = {}
        self.putAppList()
        self.putAppsEnv()
        TestApp.update(self.current_app_info)

    def putAppList(self):
        """
        Populate the current_app_info from running the cf app command
        :return: None
        """
        cf_call_result = self.makeCall(cf_app_list_command).split('\n')
        startedAppList = False
        if cf_call_result[1] == "OK":
            for app_str in cf_call_result[5:-2]:
                app_list = app_str.split()
                self.current_app_info[app_list[0]] = {
                    cf_app_url_key: "",
                    cf_app_requested_state_key: app_list[1],
                    cf_app_memory_key: app_list[3],
                    cf_app_disk_key: app_list[4],
                    cf_app_instance_key: app_list[2]
                }
                if len(app_list) > 5:
                    self.current_app_info[app_list[0]][cf_app_url_key] = app_list[5]

    def putAppsEnv(self):
        """Get all the apps environment data
        Once the cf apps have all been placed into the interal cache, we can start getting more information on them
        Since there is no downstream requirements we can run each cf env in their own thread, then wait for
        all those threads to finish
        :return:
        """
        threads = []
        for key, value in self.current_app_info.iteritems():
            threads.append(threading.Thread(target=self.makeEnvCallAndWrite, args=(key, value)))
            threads[-1].start()

        for t in threads:
            t.join()

    @staticmethod
    def makeCall(call):
        """"""

        p = subprocess.Popen(call, stdout=subprocess.PIPE, shell=True)
        result = p.communicate()[0]
        return str(result.decode("utf-8"))

    def makeEnvCallAndWrite(self, appName, targetDic):
        envResult = self.makeCall(cf_app_info_command + ' ' + appName).split('\n')

        env_dic = {cf_app_env_system_provided_key: {}, cf_app_env_user_provided_key: {}}
        current_env = cf_app_env_system_provided_key

        working_string = ""
        working_string_name = ''

        if envResult[1] == 'OK':
            for i in range(3, len(envResult)):
                line = envResult[i]
                if line == 'User-Provided:':
                    current_env = cf_app_env_user_provided_key

                elif line == 'No user-defiend env variables have been set':
                    break

                elif current_env == cf_app_env_system_provided_key:
                    if line == ' "VCAP_SERVICES": {':
                        working_string = '{'
                        working_string_name = cf_app_env_system_vcap_services_key

                    elif line == ' "VCAP_APPLICATION": {':
                        working_string = "{"
                        working_string_name = cf_app_env_system_vcap_app_key

                    elif line == '}':
                        env_dic[cf_app_env_system_provided_key][working_string_name] = json.loads(
                            working_string)
                        working_string = ''

                    elif line != '':
                        working_string += line


                elif current_env == cf_app_env_user_provided_key:
                    if line == '':
                        break
                    # todo deal with if they have a ': ' in the environment variable
                    env = line.split(': ')
                    env_dic[cf_app_env_user_provided_key][env[0]] = env[1]

        print(json.dumps(env_dic))

        targetDic[cf_app_env_key] = env_dic


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
            self.predix_app_env.values = self.current_app_info[key][cf_app_env_key].split("\n")
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
# TestApp = MyApplication()
threading.Thread(target=CF).start()
# TestApp.run()
