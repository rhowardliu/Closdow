import get_weather_data
import telegram_interface
import WindowManagerMaster
import wired_connection
import asyncio
import argparse



async def sensor_task():
    while True:
        stateChange = await wired_connection.fetch_window_state_change()
        if stateChange == 'O':
            myWindowManager.state_changed_sensor('bedroom_one', True)
        if stateChange == 'X':
            myWindowManager.state_changed_sensor('bedroom_one', False)


async def weather_data_task():
    while True:
        get_weather_data.fetch_rainfall_data_run()
        get_weather_data.fetch_pm_25_data_run()
        await asyncio.sleep(30)




def run():
    parser = argparse.ArgumentParser(description='WindowOpener')
    parser.add_argument(
        "--add",
        dest = 'address',
        type=str,
        action = "store"
    )


    global myWindowManager
    myWindowManager = WindowManagerMaster.WindowManger()
    # telegram_interface.execute(myWindowManager)
    # print('hi')
    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(weather_data_task()), ioloop.create_task(sensor_task()), ioloop.create_task(telegram_interface.execute(myWindowManager))]
    ioloop.run_until_complete(asyncio.wait(tasks))
    ioloop.close()


if __name__ == '__main__':
    run()