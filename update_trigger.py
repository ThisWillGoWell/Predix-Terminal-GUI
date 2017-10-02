import threading
import app_utils
import time


class UpdateTrigger:
    event_time_key = 'time_of_event'
    event_call_key = 'function'
    event_parameters = 'parameters'


    current_updaters = {}
    update_time_trigger = 1
    currentCountdownLatch = threading.Lock()

    def __init__(self):
        self.countdown = self.updateEventPoller(self)
        self.countdown.start()


    def acquire_lock(self):
        self.currentCountdownLatch.acquire()

    def release_lock(self):
        self.currentCountdownLatch.release()

    def triggerEventCountdown(self, event, function, parameters):
        """
        events are defied as
        {
            event_title: {
                time_of_event: <long>
                call: <function>
                parameters: <?>
            }
        }
        they will get spawned as needed from the front end
        then after they are idle for the timeout time, the
        :param event:
        :return:
        """
        self.acquire_lock()
        if event not in self.current_updaters:
            self.current_updaters[event] = {}
        self.current_updaters[event][self.event_call_key] = function
        self.current_updaters[event][self.event_parameters] = parameters
        self.current_updaters[event][self.event_time_key] = time.time()
        self.release_lock()




    class updateEventPoller(threading.Thread):

        def __init__(self, update_trigger):
            threading.Thread.__init__(self)
            self.daemon = True
            self.update_trigger = update_trigger


        running = True
        def run(self):
            while True:
                self.update_trigger.acquire_lock()
                keys = self.update_trigger.current_updaters.keys()

                for key in keys:
                    value = self.update_trigger.current_updaters[key]
                    if time.time() - value[self.update_trigger.event_time_key] > self.update_trigger.update_time_trigger:
                        call = value[self.update_trigger.event_call_key]
                        param = value[self.update_trigger.event_parameters]
                        self.update_trigger.current_updaters.pop(key, None)
                        threading.Thread(target=call, args=(param,)).start()
                self.update_trigger.release_lock()
                time.sleep(.3)






if __name__ == "__main__":
    updater = UpdateTrigger()

    def test(string):
        print(string)

    updater.triggerEventCountdown('print', test, 'a string')
