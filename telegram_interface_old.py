

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from time import sleep
import STATES
import WindowManagerMaster
import logging
import TimeManager
import JobManager

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "595584946:AAEldjnWw02P4cL_GoM8B4P6V596dH9vH6k"

# STATE_SEQUENCE = []
window_selections = {}


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def generate_keyboard_from_available_list(state):
    global window_selections
    keyboard = []
    if state == STATES.CLOSE:
        keyboard += [["Close all windows"]]
        for name in window_selections.keys():
            keyboard += [[name]]

    elif state == STATES.OPEN:
        keyboard+= [["Open all windows"]]
        for name in window_selections.keys():
            keyboard += [[name]]

    elif state == STATES.CHILDLOCK:
        for name, status in window_selections.items():
            if status:
                keyboard += [[name + "\n Child locked. Click to disable lock."]]
            else:
                keyboard += [[name + "\n Not child locked. Click to enable lock"]]

    elif state == STATES.SENSORS:
        keyboard += [["Enable all sensors", "Disable all sensors"]]
        for name, status in window_selections.items():
            if status:
                keyboard += [[name + "\nSensors enabled"]]
            else:
                keyboard += [[name + "\nSensors disabled"]]

    elif state == STATES.TIME:

        for name, status in window_selections.items():
            logger.info(name)
            opentimestrings = get_time_display(status['open'])
            closetimestrings = get_time_display(status['close'])
            keyboard += [[name +
                          "\nOpens at:" + opentimestrings +
                          "\nCloses at:" + closetimestrings]]


    return keyboard


def get_time_display(myset):
    list = sorted(myset)
    timestring = ''
    for string in list:
        timestring += " {},".format(string)

    if not timestring:
        timestring = '- '
    return timestring[:-1]

def parse_for_window_name(keyboard_key):
    window_name = keyboard_key.split("\n",1)[0]
    logger.info(" Parsing string from '{0}' to '{1}'".format(keyboard_key, window_name) )
    return window_name

def error_instruction(bot, update):
    update.message.reply_text("Sorry, I did not understand that.\n"
                              "/main to return to the main menu\n")

# def back(bot, update):
#
#     if not STATE_SEQUENCE:
#         logger.info("Going back 1 page but not available")
#         update.message.reply_text("No back option available.")
#         return command_wait(bot, update)
#
#     logger.info("Going Back 1 page")
#     prev_state = STATE_SEQUENCE.pop()
#     return prev_state

def remove_irrelevant_windows(removing):
    todelete = set()
    global window_selections
    for name, status in window_selections.items():
        if status == removing:
            todelete.add(name)
    for windows in todelete:
        del window_selections[windows]

def main_menu (bot, update, user_data = None):
    if user_data:
        logger.info("clearing:")
        logger.info(user_data)
        user_data.clear()
    # STATE_SEQUENCE.clear()
    window_selections.clear()
    changed_window_status = update.message.text
    if changed_window_status != "/main":
        update.message.reply_text("It's been great serving you!", reply_markup = ReplyKeyboardRemove())
    logger.info("Going back to main")
    return command_wait(bot, update)

def exit(bot, update):
    user=update.message.from_user
    logger.info("User exited conversation")
    update.message.reply_text("Hmm. Bye.",reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

def start(bot, update):
    user = update.message.from_user
    update.message.reply_text("Window Management can be a chore but I'm here for you sweetheart!", reply_markup = ReplyKeyboardRemove())
    sleep(0.3)
    return command_wait(bot, update)

def command_wait(bot,update):
    command_wait_keyboard = [["Open", "Close"],
                             ["Set Time", "Set Child Lock"],
                             ["Toggle Sensor"]]
    markup = ReplyKeyboardMarkup (command_wait_keyboard, one_time_keyboard= True)

    user = update.message.from_user
    logger.info("Command wait")
    update.message.reply_text("Nice to see you, {}.".format(user.first_name))
    update.message.reply_text("If you ever get stuck, remember the following commands!\n"
                              # "/back to return to the previous page\n"
                              "/main to return here\n"
                              "/exit will terminate the conversation.")
    update.message.reply_text("Now what would you like to do?", reply_markup = markup)
    return STATES.COMMAND_WAIT


def open_select_windows(bot,update):
    # STATE_SEQUENCE.append(STATES.OPEN)
    global window_selections
    window_selections = myWindowManager.get_windows(myWindowManager.ISOPEN)
    remove_irrelevant_windows(True)

    # create keyboard
    closed_windows_keyboard = generate_keyboard_from_available_list(STATES.OPEN)
    markup = ReplyKeyboardMarkup (closed_windows_keyboard, one_time_keyboard= True)

    logger.info("Open: Windows selection page")
    update.message.reply_text("Select windows to open.",reply_markup = markup)
    return STATES.OPEN

def open_execute(bot, update):

    logger.info("Windows available:")
    for x in window_selections.keys():
        logger.info(x)
    instruction = update.message.text
    logger.info("received instruction " + instruction)

    if instruction == "Open all windows" :
        logger.info("Opening all windows")
        #open all windows
        myWindowManager.change_all_window_state(True)
        return main_menu(bot, update)


    elif instruction in window_selections.keys():
        logger.info("Opening window: " + instruction)
        myWindowManager.change_window_state(instruction, True)
        #open window named instruction

        return main_menu(bot, update)

    else:
        logger.info("Window to open not found")
        return error_instruction(bot, update)


def close_select_windows(bot, update):
    # STATE_SEQUENCE.append(STATES.CLOSE)

    global window_selections
    window_selections = myWindowManager.get_windows(myWindowManager.ISOPEN)
    remove_irrelevant_windows(False)

    # create keyboard
    opened_windows_keyboard = generate_keyboard_from_available_list(STATES.CLOSE)
    markup = ReplyKeyboardMarkup(opened_windows_keyboard, one_time_keyboard= True)

    logger.info("Close: Windows selection page")
    update.message.reply_text("Select windows to close.", reply_markup=markup)
    return STATES.CLOSE

def close_execute(bot, update):

    logger.info("Windows available:")
    for x in window_selections.keys():
        logger.info(x)
    instruction = update.message.text
    logger.info("received instruction " + instruction)

    if instruction == "Close all windows" :
        logger.info("Closing all windows")
        #close all windows
        myWindowManager.change_all_window_state(False)
        return main_menu(bot, update)


    elif instruction in window_selections.keys():
        logger.info("Closing window" + instruction)
        #close window named instruction
        myWindowManager.change_window_state(instruction, False)
        return main_menu(bot, update)

    else:
        logger.info("Window to close not found")
        return error_instruction(bot, update)


def childlock_windows_selection (bot, update):
    logger.info("Childlock: Windows selection page")
    # STATE_SEQUENCE.append(STATES.CHILDLOCK)
    global window_selections
    window_selections = myWindowManager.get_windows(myWindowManager.CHILDLOCK)

    # create keyboard
    childlock_windows_keyboard = generate_keyboard_from_available_list(STATES.CHILDLOCK)
    markup = ReplyKeyboardMarkup(childlock_windows_keyboard, one_time_keyboard= True)

    update.message.reply_text("Select window to toggle childlock setting.", reply_markup = markup)
    return STATES.CHILDLOCK

def childlock_execute(bot, update):
    instruction = update.message.text
    window_chosen = parse_for_window_name(instruction)
    if window_chosen in window_selections.keys():
        if window_selections[window_chosen]:
            logger.info(" Disabling child lock for" + window_chosen)
            myWindowManager.set_childlock(window_chosen, False)
            update.message.reply_text("Disabled the childlock of " + window_chosen)
            return main_menu(bot, update)

        elif not window_selections[window_chosen]:
            logger.info("Enabling child lock for "+ window_chosen)
            myWindowManager.set_childlock(window_chosen, True)
            update.message.reply_text("Enabled the childlock of " + window_chosen)
            return main_menu(bot, update)
    else:
        logger.info("Window to child lock not found")
        return error_instruction(bot, update)

def timeset_windows_selection(bot, update, user_data = None):
    global window_selections
    if user_data:
        user_data.clear()
        window_selections.clear()
    window_selections = myWindowManager.get_windows(myWindowManager.AUTO_TIMESET)
    # create keyboard
    time_windows_keyboard = generate_keyboard_from_available_list(STATES.TIME)
    markup = ReplyKeyboardMarkup(time_windows_keyboard, one_time_keyboard= True, resize_keyboard= True)

    update.message.reply_text("Select window to change time setting", reply_markup = markup)
    return STATES.TIME

def timeset_to_add_or_remove(bot, update, user_data):
    instruction = update.message.text
    window_chosen = parse_for_window_name(instruction)

    user_data['window'] = window_chosen
    logger.info(user_data)

    keyboard = [['Add a time to operate window', 'Remove a time to operate window']]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard= True)

    update.message.reply_text("Editing time options for:\n" + instruction, reply_markup = markup)

    return STATES.TIME_EDITING


def timeset_add(bot, update):
    keyboard = [['Open', 'Close']]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard= True)
    update.message.reply_text("Adding Auto time function.\n"
                              "Would you want the window to:", reply_markup = markup)
    return STATES.TIME_ADDING


def timeset_remove(bot, update, user_data):
    if myWindowManager.time_operation_counter <=0:
        update.message.reply_text("No operations found.")
        return end_of_time_operation(bot, update)


    window_name = user_data['window']
    opening_windows, closing_windows = window_selections[window_name].values()
    opening_windows_display_text = get_time_display(opening_windows)
    closing_windows_display_text = get_time_display(closing_windows)

    keyboard = [["Remove every operation"]]
    open_keyboard = []
    close_keyboard = []
    for openingtime in opening_windows:
        open_keyboard.append ( "Opens at\n{}".format(openingtime) )
    for closingtime in closing_windows:
        close_keyboard.append( "Closes at \n{}".format(closingtime) )
    keyboard.append(open_keyboard)
    keyboard.append(close_keyboard)
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard= True, resize_keyboard= True)

    update.message.reply_text("Current operating time for {0}:"
                              "\nOpens at:{1}"
                              "\nCloses at:{2}".format(window_name, opening_windows_display_text, closing_windows_display_text))
    update.message.reply_text("Click on a time slot to remove its operation.", reply_markup = markup)
    return STATES.TIME_REMOVING


def remove_job_all(bot, update, user_data, job_queue):
    window_name = user_data['window']
    logger.info("removing all jobs")
    job_queue.stop()
    myWindowManager.remove_all_window_time(window_name)
    update.message.reply_text("All time operations for {} have been removed.".format(window_name), reply_markup = ReplyKeyboardRemove())
    return end_of_time_operation(bot, update)

def remove_job_one(bot, update, user_data, job_queue):
    window_name = user_data['window']
    instructions = update.message.text
    logger.info("Received instruction to remove: " + instructions)
    state = instructions.split(' ',1)[0][:-1].lower()
    time = instructions.split('\n',1)[1]

    #remove job by its name
    jobname = TimeManager.create_window_timestamp(window_name, state, time)
    logger.info("Window_timestamp created " + jobname)
    myjob = job_queue.get_jobs_by_name(jobname)
    logger.info(myjob)
    for job in myjob:
        job.schedule_removal()

    #remove data from database
    myWindowManager.remove_window_time(window_name,state,time)
    update.message.reply_text("{0} will no longer {1} at {2}".format(window_name, state, time), reply_markup = ReplyKeyboardRemove())
    return end_of_time_operation(bot, update)


def timeset_input_time(bot, update, user_data):

    user_data['state'] = update.message.text.lower()
    logger.info(user_data['state'])
    update.message.reply_text("Please input your time in HH:mm (24hrs) format. E.g. 13:30", reply_markup = ReplyKeyboardRemove())
    return STATES.TIME_AWAITING_INPUT


def window_job(bot, job):
    stamp = job.name
    name, state, time = TimeManager.parse_window_timestamp(stamp)
    logger.info(name + " " + state + " " + time)
    if state == 'open':
        bot.send_message(chat_id = job.context, text = "{0} is opening its window at {1}".format(name, time))
        myWindowManager.change_window_state(name, True)
    if state == 'close':
        bot.send_message(chat_id = job.context, text = "{0} is closing its window at {1}".format(name, time))
        myWindowManager.change_window_state(name, False)

def add_time_job(bot, update, job_queue, user_data):

    if not user_data:
        error_instruction(bot, update)

    window_name = user_data['window']
    window_state = user_data['state']
    time_input = update.message.text

    #add job
    window_datetime = TimeManager.convert_string_to_time(time_input)
    logger.info(window_datetime)
    window_timestamp = TimeManager.create_window_timestamp(window_name, window_state, time_input)

    job_queue.run_daily(window_job, window_datetime, context= update.message.chat_id, name= window_timestamp)

    #add to database
    myWindowManager.add_window_time(window_name,window_state,time_input)

    #add keyboard

    update.message.reply_text("Auto time function added for {0}.\n"
                              "It will {1} at {2}".format(window_name, window_state, time_input))

    return end_of_time_operation(bot, update)


def end_of_time_operation(bot, update):
    keyboard = [["Continue editing time settings"], ["Return to main menu"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard= True)
    update.message.reply_text("Now, would you like to:", reply_markup = markup)

    return STATES.END_TIME



def sensors_windows_selection (bot, update):
    logger.info("Sensors: Windows selection page")
    # STATE_SEQUENCE.append(STATES.CHILDLOCK)
    global window_selections
    window_selections = myWindowManager.get_windows(myWindowManager.ENABLE_SENSOR)

    # create keyboard
    sensors_keyboard = generate_keyboard_from_available_list(STATES.SENSORS)
    markup = ReplyKeyboardMarkup(sensors_keyboard, one_time_keyboard= True)

    update.message.reply_text("Select window to toggle childlock setting.", reply_markup = markup)
    return STATES.SENSORS


def sensors_execute_individual(bot, update):
    instruction = update.message.text
    window_chosen = parse_for_window_name(instruction)
    if window_chosen in window_selections.keys():
        if window_selections[window_chosen]:
            logger.info(" Disabling sensors for" + window_chosen)
            myWindowManager.toggle_sensor(window_chosen, False)
            update.message.reply_text("Disabled sensor for " + window_chosen)
            return main_menu(bot, update)

        elif not window_selections[window_chosen]:
            logger.info("Enabling sensors for "+ window_chosen)
            myWindowManager.toggle_sensor(window_chosen, True)
            update.message.reply_text("Enabled sensor for " + window_chosen)
            return main_menu(bot, update)
    else:
        logger.info("Window sensor not found")
        return error_instruction(bot, update)

def enable_all_sensors(bot, update):
    myWindowManager.toggle_all_sensors(True)
    update.message.reply_text("All sensors enabled")
    return main_menu(bot, update)

def disable_all_sensors(bot, update):
    myWindowManager.toggle_all_sensors(False)
    update.message.reply_text("All sensors disabled")
    return main_menu(bot, update)

def execute(windowManager):
    global myWindowManager
    myWindowManager = windowManager

    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[ CommandHandler('start', start)
                       ],

        states={
            STATES.COMMAND_WAIT: [RegexHandler('^Open$', open_select_windows),
                                  RegexHandler('^Close$', close_select_windows),
                                  RegexHandler('^Set Child Lock$', childlock_windows_selection),
                                  RegexHandler('^Set Time$',timeset_windows_selection),
                                  RegexHandler('^Toggle Sensor$', sensors_windows_selection)
                                  ],
            STATES.OPEN: [MessageHandler(Filters.text, open_execute)
                          ],
            STATES.CLOSE: [MessageHandler(Filters.text, close_execute)
                          ],
            STATES.CHILDLOCK: [MessageHandler(Filters.text, childlock_execute)
                               ],
            STATES.SENSORS:[RegexHandler('^Enable all sensors$', enable_all_sensors),
                                  RegexHandler('^Disable all sensors$', disable_all_sensors),
                                  MessageHandler(Filters.text,sensors_execute_individual)
                                  ],
            STATES.TIME: [MessageHandler(Filters.text, timeset_to_add_or_remove, pass_user_data = True)
                          ],
            STATES.TIME_EDITING: [RegexHandler('^Add a time to operate window$',timeset_add),
                                  RegexHandler('^Remove a time to operate window$', timeset_remove, pass_user_data= True)
                                  ],
            STATES.TIME_ADDING: [RegexHandler('^Open|Close$',timeset_input_time,pass_user_data=True)],
            STATES.TIME_AWAITING_INPUT: [RegexHandler(TimeManager.time_pattern,add_time_job,
                                              pass_job_queue = True, pass_user_data = True) ],
            STATES.TIME_REMOVING: [RegexHandler('^Remove every operation$', remove_job_all, pass_user_data= True, pass_job_queue= True),
                                   RegexHandler('^Opens at|Closes at', remove_job_one, pass_job_queue= True, pass_user_data= True),],
            STATES.END_TIME: [RegexHandler('^Continue editing time settings$',timeset_windows_selection, pass_user_data = True),
                              RegexHandler("^Return to main menu$",main_menu, pass_user_data= True)]



        },

        fallbacks=[CommandHandler('main', main_menu, pass_user_data = True),
                   CommandHandler('exit', exit),
                   MessageHandler(Filters.text, error_instruction)
                   ]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__' :
    execute(WindowManagerMaster.WindowManger())