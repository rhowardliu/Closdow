import logging
# import wired_connection


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)



class WindowManger:
    time_operation_counter = 0

    # query strings
    ISOPEN = 'isopen'
    CHILDLOCK = 'childlock'
    AUTO_RAINFALL = 'auto_rainfall'
    AUTO_DUST = 'auto_dust'
    AUTO_TIMESET = 'auto_timeset'
    ENABLE_SENSOR = 'enable_sensor'

    def __init__(self):
        self.mywindows={}
        self.add_new_window("bedroom_one", Window(123))
        self.add_new_window("living room", Window(1212))

    def add_new_window(self, name, new_window):
        self.mywindows[name] = vars(new_window)


    def get_windows(self, querying_for):
        w_dic = {}
        for name, status in self.mywindows.items():
            w_dic[name] = status[querying_for]
        return w_dic


    def change_all_window_state (self, isopen):
        for x in self.mywindows.keys():
            self.change_window_state (x, isopen=isopen)
        logger.info("All windows set")

    def change_window_state(self, window_name, isopen):
        self.mywindows[window_name]['isopen'] = isopen
        logger.info("Window {0} open is set to {1}".format(window_name, isopen))
        # if isopen:
        #     wired_connection.open()
        # else:
        #     wired_connection.close()


    def set_childlock(self, window_name, childlock):
        self.mywindows[window_name][self.CHILDLOCK] = childlock
        logger.info("Window {0} childlock is set to {1}".format(window_name, childlock))
        # if childlock:
        #     wired_connection.set_child_lock()
        # else:
        #     wired_connection.disable_child_lock()


    def add_window_time(self, window_name, state, time):
        self.mywindows[window_name][self.AUTO_TIMESET][state].add(time)
        logger.info("Added mywindows['{0}']['auto_timeset']['{1}'] = ['{2}'] Currently time".format(window_name, state, time))
        logger.info(self.mywindows[window_name][self.AUTO_TIMESET])
        self.time_operation_counter += 1

    def remove_all_window_time(self, window_name):
        self.mywindows[window_name][self.AUTO_TIMESET]['open'].clear()
        self.mywindows[window_name][self.AUTO_TIMESET]['close'].clear()
        logger.info("Removed all timeslot.")
        logger.info(self.mywindows[window_name][self.AUTO_TIMESET])
        self.time_operation_counter = 0

    def remove_window_time(self, window_name, state, time):
        self.mywindows[window_name][self.AUTO_TIMESET][state].remove(time)
        logger.info("{} removed. Remaining timeslots:".format(time))
        logger.info( self.mywindows[window_name][self.AUTO_TIMESET][state])
        self.time_operation_counter -=1

    def toggle_all_sensors(self, enable_sensor):
        for x in self.mywindows.keys():
            self.toggle_sensor(x, enable_sensor)
        logger.info("All windows sensors set")

    def toggle_sensor(self, window_name, enable_sensor):
        self.mywindows[window_name][self.ENABLE_SENSOR] = enable_sensor
        logger.info("Window {0} sensor is set to {1}".format(window_name, enable_sensor))
        # if enable_sensor:
        #     wired_connection.enable_sensor()
        # else:
        #     wired_connection.disable_sensor()

    def any_window_open(self, isOpen):
        for x in self.mywindows.values():
            if x['isopen'] == isOpen:
                return True
        else: return False

    def state_changed_sensor(self, window_name, state):
        self.mywindows[window_name][self.ISOPEN] = state


class Window:

    def __init__(self, window_id, isopen = False, childlock = False,
                 enable_sensor = False, auto_timeset = None):
        self.id = window_id
        self.isopen = isopen
        self.childlock = childlock
        self.auto_timeset = {}
        self.enable_sensor = enable_sensor
        if auto_timeset:
            self.auto_timeset = auto_timeset
        else:
            self.auto_timeset['open'] = set()
            self.auto_timeset['close'] = set()

    def open(self):
        if self.isopen:
            print("Window is already opened")

    def close(self):
        if not self.isopen:
            print("Window is already closed")

