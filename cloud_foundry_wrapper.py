import subprocess
import threading
import json
import os.path
import app_utils
import cache

class CF:
    cf_app_requested_state_key = 'state'
    cf_app_memory_key = 'memory'
    cf_app_disk_key = 'disk'
    cf_app_url_key = 'url'
    cf_app_instance_key = 'instance'
    cf_app_env_key = 'env'
    cf_app_details_key = 'details'
    cf_app_env_system_provided_key = 'System-Provided'
    cf_app_env_system_vcap_services_key = 'VCAP_SERVICES'
    cf_app_env_system_vcap_app_key = 'VCAP_APPLICATION'
    cf_app_env_user_provided_key = 'User-Provided'

    cf_app_list_command = 'cf a'
    cf_app_details_command = 'cf app'
    cf_app_info_command = 'cf env'


    def __init__(self):
        """Initialize the CF interface
        define the state variables of the cf app, currently not used as an object
        """
        self.logger = app_utils.logger
        self.current_app_info = {}
        self.org = ""
        self.space = ""
        self.user = ""
        self.cache = cache.Cache()
        self.update_call = self.defaultUpdateCall

    def update(self):
        """Update the working CF Cache
        Run the cf commands to so the dic can be created
        Then call the update function of the Test app to update the front ent
        don't really like that the test app is coupled in the cf interface but easy to do it
        :return:  None
        """
        if self.cache.file_found:
            self.logger.log('using cache')
            self.current_app_info = self.cache.read_cache(self.cache.cache_cf_app_info)
        else:
            self.current_app_info = {}
            self.putAppList()
            self.putAppsEnv()
            self.putAppDetails()
            self.cache.write_cache(self.cache.cache_cf_app_info, self.current_app_info)

        self.update_call(self.current_app_info)



    def setUpdateCall(self, func):
        self.update_call=func


    def defaultUpdateCall(self, value):
        pass

    def putAppDetails(self):
        threads = []
        for key,value in self.current_app_info.iteritems():
            threads.append(threading.Thread(target=self.makeDetailCallAndWrite, args=(key, value)))
            threads[-1].start()

        print 'joining'
        for t in threads:
            t.join()
        print 'exit'

    def makeDetailCallAndWrite(self, appId, targetDict, returnDic=False):
        builder = {}
        cf_call_result = self.makeCall(self.cf_app_details_command + " " + appId).split('\n')
        for line in cf_call_result:
            if ':' in line and len(line.split(':')) == 2:
                current_detail = line.split(':')
                builder[current_detail[0]]= ' '.join(current_detail[1].split())
        if targetDict is not None:
            targetDict[self.cf_app_details_key] = builder
        if returnDic:
            return builder




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
        Once the cf apps have all been placed into the internal cache, we can start getting more information on them
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
        """
        Make a call using the subprocess module. Will return a string with the result
         of the call was
        :param call: the command to be opnened
        :return: command result in a string
        """
        p = subprocess.Popen(call, stdout=subprocess.PIPE, shell=True)
        result = p.communicate()[0]
        return str(result.decode("utf-8"))


    def makeEnvCallAndWrite(self, app_name, target_dict=None, return_dict=False):
        """
        Get the env variables from a cloud foundry app and places them into a dic
        Makes the cf env call and the builds a dic of the environment variables
        uses a state machine to parse the env string
        The dic was used so when making a lot of these calls at a time 
        they can just be inserted into the dic
        :param app_name: the app to be called into cf
        :param target_dict: the dic to place the result if defined
        :param return_dict: if true will return the built dict 
        :return: dic if returnDict is true
        """

        envResult = self.makeCall(self.cf_app_info_command + ' ' + app_name).split('\n')

        env_dic = {self.cf_app_env_system_provided_key: {}, self.cf_app_env_user_provided_key: {}}
        current_env = self.cf_app_env_system_provided_key

        working_string = ""
        working_string_name = ''
        if envResult[1] == 'OK':
            for i in range(3, len(envResult)):
                line = envResult[i]
                if line == 'User-Provided:':
                    current_env = self.cf_app_env_user_provided_key

                elif line == 'No user-defined env variables have been set':
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
        if target_dict is not None:
            target_dict[self.cf_app_env_key] = env_dic
        if return_dict:
            return env_dic







if __name__ == "__main__":
    cf = CF()

    cf.update()













