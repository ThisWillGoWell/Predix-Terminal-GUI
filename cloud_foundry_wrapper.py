import subprocess
import threading
import json

class CF:
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

    def __init__(self):
        """Initialize the CF interface
        define the state variables of the cf app, currently not used as an object
        """
        self.current_app_info = {}
        self.org = ""
        self.space = ""
        self.user = ""
        self.update_call = self.defaultUpdateCall

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
        self.update_call(self.current_app_info)



    def setUpdateCall(self, func):
        self.update_call=func


    def defaultUpdateCall(self, value):
        pass


    def putAppList(self):
        """
        Populate the current_app_info from running the cf app command
        :return: None
        """
        cf_call_result = self.makeCall(self.cf_app_list_command).split('\n')
        startedAppList = False
        if cf_call_result[1] == "OK":
            for app_str in cf_call_result[5:-2]:
                app_list = app_str.split()
                self.current_app_info[app_list[0]] = {
                    self.cf_app_url_key: "",
                    self.cf_app_requested_state_key: app_list[1],
                    self.cf_app_memory_key: app_list[3],
                    self.cf_app_disk_key: app_list[4],
                    self.cf_app_instance_key: app_list[2]
                }
                if len(app_list) > 5:
                    self.current_app_info[app_list[0]][self.cf_app_url_key] = app_list[5]

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
        envResult = self.makeCall(self.cf_app_info_command + ' ' + appName).split('\n')

        env_dic = {self.cf_app_env_system_provided_key: {}, self.cf_app_env_user_provided_key: {}}
        current_env = self.cf_app_env_system_provided_key

        working_string = ""
        working_string_name = ''

        if envResult[1] == 'OK':
            for i in range(3, len(envResult)):
                line = envResult[i]
                if line == 'User-Provided:':
                    current_env = self.cf_app_env_user_provided_key

                elif line == 'No user-defiend env variables have been set':
                    break

                elif current_env == self.cf_app_env_system_provided_key:
                    if line == ' "VCAP_SERVICES": {':
                        working_string = '{'
                        working_string_name = self.cf_app_env_system_vcap_services_key

                    elif line == ' "VCAP_APPLICATION": {':
                        working_string = "{"
                        working_string_name = self.cf_app_env_system_vcap_app_key

                    elif line == '}':
                        env_dic[self.cf_app_env_system_provided_key][working_string_name] = json.loads(
                            working_string)
                        working_string = ''

                    elif line != '':
                        working_string += line


                elif current_env == self.cf_app_env_user_provided_key:
                    if line == '':
                        break
                    # todo deal with if they have a ': ' in the environment variable
                    env = line.split(': ')
                    env_dic[self.cf_app_env_user_provided_key][env[0]] = env[1]

        #print(json.dumps(env_dic))

        targetDic[self.cf_app_env_key] = env_dic
