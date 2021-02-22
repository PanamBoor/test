from datetime import *
from exchangeratesapi import Api
from aiogram import Bot, Dispatcher, executor, types
from sqldb import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests
import matplotlib.pyplot as plt


# Where USD is the base currency you want to use


# Get the latest foreign exchange rates:
def getLatestEchangeRates():
    return api.get_rates('USD')


def getGraphFor7Days():
    url = 'https://api.exchangeratesapi.io/history?start_at=2019-11-27&end_at=2019-12-03&base=USD&symbols=CAD'
    response = requests.get(url)
    data = response.json()
    return data


api = Api()

# подключаем токен бота
bot = Bot(token='1622822644:AAHw5erwlhYN8asOR9mHi8jaq6yCV-QxGYE')
dp = Dispatcher(bot, storage=MemoryStorage())
if not dp:
    exit("Error: no token provided")


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if get_have_user_in_a_base(id_telegram=message.from_user.id) == 0:
        time_last = datetime.today().hour * 60 + datetime.today().minute
        dictionary = getLatestEchangeRates()
        rates = dictionary.get('rates')
        user_info(id_telegram=message.from_user.id, username=message.from_user.first_name, date_last=time_last)
        id = 0
        for key, value in rates.items():
            id = id + 1
            course(id=id, name_val=key, price=round(value, 2))

        await bot.send_message(message.from_user.id, "Hello " + message.from_user.first_name +
                               '/list or /lst - returns list of all available rates\n'
                               '/history USD/CAD for 7 days - return an image graph chart which shows the exchange rate graph')
    else:
        await bot.send_message(message.from_user.id,
                               "Hello " + message.from_user.first_name + '/list or /lst - returns list of all available rates\n'
                                                                         '/history USD/CAD for 7 days - return an image graph chart which shows the exchange rate graph')


@dp.message_handler(commands=['list', 'lst'])
async def list(message: types.Message):
    conn = sqlite3.connect('courses.db')
    time_last = conn.execute(f"select date_last from user_reg where id_telegram={message.from_user.id}").fetchone()[0]
    time_now = datetime.today().hour * 60 + datetime.today().minute
    dictionary = getLatestEchangeRates()
    rates = dictionary.get('rates')
    if time_now - time_last >= 10:
        id = 0
        print("10 minutes")
        for key, value in rates.items():
            id = id + 1
            conn.execute(f'UPDATE user_reg SET date_last = {time_now} WHERE id_telegram = {message.from_user.id}')
            conn.execute(f'UPDATE course SET price = {round(value, 2)} WHERE id = {str(id)}')
            conn.commit()
            await bot.send_message(message.from_user.id, str(key) + "\n" + str(round(value, 2)))

    else:
        print("! 10 minutes")
        id = 0
        for key, value in rates.items():
            id = id + 1
            key = conn.execute(f"select name_val from course where id={str(id)}").fetchone()[0]
            value = conn.execute(f"select price from course where id={str(id)}").fetchone()[0]
            conn.commit()
            await bot.send_message(message.from_user.id, str(key) + "\n" + str(value))
    conn.close()


@dp.message_handler(commands=['exchange'])
async def exchange(message: types.Message):
    conn = sqlite3.connect('courses.db')
    cad1 = conn.execute(f"select price from course where id = {1}").fetchone()[0]
    cad_exchange = cad1 * 10
    await bot.send_message(message.from_user.id, f"10 USD TO CAD this is {cad_exchange} ")


@dp.message_handler(commands=['history'])
async def history(message: types.Message):
    list = []
    y = [1, 2, 3, 4, 5]
    graph = getGraphFor7Days()
    rates = graph.get('rates')
    for key, value in rates.items():
        for name, value in value.items():
            list.append(value)
    print(list)
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("A test graph")
    for i in range(y[0]):
        plt.plot(list, [[i] for pt in y], label='id %s' % i)
    plt.legend()

    plt.show()
    print(list)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
