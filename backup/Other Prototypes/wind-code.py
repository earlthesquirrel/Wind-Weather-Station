import board
import busio
import digitalio
import asyncio
import board
import time
import countio


global count
global avg_wind_speed_5min
global temp_sum_5min
global temp_sum_10min
global last_time_5min
global last_time_10min

count = 0
temp_sum_5min = 0
temp_sum_10min = 0
avg_wind_speed_5min = 0
avg_wind_speed_10min = 0
sleep_time = 5

async def catch_interrupt(pin):
    global count
    """Print a message when pin goes low."""
    with countio.Counter(pin) as interrupt:
        while True:
            if interrupt.count > 0:
                count=count+interrupt.count
                interrupt.count = 0
                print("interrupted!"+str(count))
            # Let another task run.
            await asyncio.sleep(1)



async def speed():
    global count
    global temp_sum_5min
    global temp_sum_10min
    global last_time_5min
    global last_time_10min

    # Set up time values for calculations
    last_time_5min = time.time()
    last_time_10min = time.time()
    last_loop = time.time()

    # On initial startup, wait 5 sec
    await asyncio.sleep(5)
    count=0

    while True:
        # Sensor Resolution is 0.0875 m/s
        # 1 Round in 1 Sec = 20 pulses, Wind Speed = 1.75 m/s
        # 4.5 Round in 1 Sec = 90 pulses, Wind Speed = 7.875 m/s

        current_time = time.time()
        speedVal = (( count * 8.75 ) / 100 ) / (current_time - last_loop)
                #  1.75 / 20 = 0.0875 (resolution)
                # Divided by the number of seconds since we last checked.
        print("Current Time = "+str(current_time))
        print("Last Time 5 min = "+str(last_time_5min))
        print("Last Time 10 min = "+str(last_time_10min))
        print("Last Loop = "+str(last_loop))
        print("Count = "+str(count))
        print("Speed = "+str(speedVal))
        last_loop = current_time
        count = 0

        temp_sum_5min = temp_sum_5min + speedVal

        # 300 is 5 minutes -- This is for 5 min wind speed Average.
        if (current_time > (last_time_5min + 300)  ):
                last_time_5min = current_time
                # Avg Wind Speed = sum of all speeds / (total time 5 min * 60/ sampling time 5 sec)
                avg_wind_speed_5min = temp_sum_5min / (( 5 * 60)/ sleep_time )
                print("5 min Avg Speed" + str(avg_wind_speed_5min))
                temp_sum_5min = 0;

        # 600 is 10 minutes -- This is for 10 min wind speed Average.
        if (current_time > (last_time_10min + 600)  ):
                last_time_10min = current_time
                # Avg Wind Speed = sum of all speeds / (total time 10 min * 60/ sampling time 5 sec)
                avg_wind_speed_10min = temp_sum_10min / (( 10 * 60)/sleep_time )
                print("10 min Avg Speed" + str(avg_wind_speed_10min))
                temp_sum_10min = 0;

        await asyncio.sleep(sleep_time)



async def main():

    speed_task = asyncio.create_task(speed())
    interrupt_task = asyncio.create_task(catch_interrupt(board.D1))

    print("In Main")
    await asyncio.gather(speed_task, interrupt_task)

asyncio.run(main())
