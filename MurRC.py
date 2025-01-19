import os
import psutil
import webbrowser
import tempfile
import sounddevice as sd
import numpy as np
import wavio
import mouse
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from PIL import ImageGrab
from pygetwindow import getWindowsWithTitle
from aiogram import filters

API_TOKEN = 'вот сюда вставь свой токен'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

recording = False

EMOJIS = {
    "SCREENSHOT": "📸",
    "WEBCAM": "🎥",
    "CPU": "💻",
    "PROCESS": "🔄",
    "MIC": "🎤",
    "POWER": "⚡",
    "APP": "📲",
    "SPOTIFY": "🎵",
    "DISCORD": "💬",
    "CHROME": "🌐",
    "BACK": "🔙",
    "VIDEO": "📺",
    "MOUSE": "🖱️",
}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        f"Управление мышью {EMOJIS['MOUSE']}",
        f"Получить скриншот {EMOJIS['SCREENSHOT']}",
        f"Получить скриншот с вебкамеры {EMOJIS['WEBCAM']}",
        f"Сведения о нагрузке {EMOJIS['CPU']}",
        f"Получить информацию о процессах {EMOJIS['PROCESS']}",
        f"Завершить процесс {EMOJIS['PROCESS']}",
        f"Записать звук {EMOJIS['MIC']}",
        f"Выключить {EMOJIS['POWER']}",
        f"Запустить программу {EMOJIS['APP']}",
        f"Видео по ссылке {EMOJIS['VIDEO']}",
    )
    await message.answer('Компьютер запущен', reply_markup=markup)

@dp.message_handler(filters.Regexp('Управление мышью ' + EMOJIS['MOUSE']))
async def handle_mouse_control(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("↑ Вверх", "⬅️ Влево", "➡️ Вправо")
    markup.row("⬇️ Вниз", "🖱 Клик", "🔙 Вернуться в главное меню")
    await message.answer('Выберите действие:', reply_markup=markup)

@dp.message_handler(filters.Regexp('🖱 Клик'))
async def handle_mouse_click(message: types.Message):
    mouse.click()
    await message.answer('Клик выполнен.')

@dp.message_handler(filters.Regexp('⬅️ Влево'))
async def handle_mouse_move_left(message: types.Message):
    mouse.move(-50, 0, absolute=False, duration=0.2)
    await message.answer('Мышь перемещена влево.')

@dp.message_handler(filters.Regexp('↑ Вверх'))
async def handle_mouse_move_up(message: types.Message):
    mouse.move(0, -50, absolute=False, duration=0.2)
    await message.answer('Мышь перемещена вверх.')

@dp.message_handler(filters.Regexp('⬇️ Вниз'))
async def handle_mouse_move_down(message: types.Message):
    mouse.move(0, 50, absolute=False, duration=0.2)
    await message.answer('Мышь перемещена вниз.')

@dp.message_handler(filters.Regexp('➡️ Вправо'))
async def handle_mouse_move_right(message: types.Message):
    mouse.move(50, 0, absolute=False, duration=0.2)
    await message.answer('Мышь перемещена вправо.')

@dp.message_handler(filters.Regexp('🔙 Вернуться в главное меню'))
async def return_to_main_menu(message: types.Message):
    await send_welcome(message)

@dp.message_handler(filters.Regexp('Получить скриншот ' + EMOJIS['SCREENSHOT']))
async def get_screenshot(message: types.Message):
    path = tempfile.gettempdir() + '/screenshot.png'
    screenshot = ImageGrab.grab()
    screenshot.save(path, 'PNG')
    await message.answer_photo(open(path, 'rb'))

@dp.message_handler(filters.Regexp('Получить скриншот с вебкамеры ' + EMOJIS['WEBCAM']))
async def get_webcam_screenshot(message: types.Message):
    camera_window = getWindowsWithTitle("Camera Preview")
    if camera_window:
        camera_window[0].activate()
        screenshot = ImageGrab.grab(bbox=camera_window[0]._rect)
        path = tempfile.gettempdir() + '/webcam_screenshot.png'
        screenshot.save(path, 'PNG')
        await message.answer_photo(open(path, 'rb'))
    else:
        await message.answer('На данном компьютере не установлена вебкамера')

@dp.message_handler(filters.Regexp('Сведения о нагрузке ' + EMOJIS['CPU']))
async def get_system_load_info(message: types.Message):
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    memory_total = round(memory.total / (1024**3), 2)
    memory_used = round(memory.used / (1024**3), 2)
    memory_percent = memory.percent
    load_info = f"{EMOJIS['CPU']} CPU {cpu_percent}%\nПамять: {memory_used} ГБ / {memory_total} ГБ ({memory_percent}%)"
    
    top_processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), key=lambda x: x.info['cpu_percent'], reverse=True)[:5]
    processes_info = "\n".join([f"PID: {proc.info['pid']}, Имя: {proc.info['name']}, CPU: {proc.info['cpu_percent']}%" for proc in top_processes])
    
    await message.answer(f"{load_info}\n\nСамые нагруженные программы:\n{processes_info}")

@dp.message_handler(filters.Regexp('Записать звук ' + EMOJIS['MIC']))
async def start_recording(message: types.Message):
    global recording
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(f"Отправить запись {EMOJIS['MIC']}")
    await message.answer('Начинаю запись...', reply_markup=markup)
    recording = True

@dp.message_handler(filters.Regexp('Отправить запись ' + EMOJIS['MIC']))
async def send_audio(message: types.Message):
    global recording
    if recording:
        await message.answer('Заканчиваю запись...')
        path = tempfile.gettempdir() + '/audio.wav'
        duration = 5
        fs = 44100
        recording_data = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype=np.int16)
        sd.wait()
        wavio.write(path, recording_data, fs, sampwidth=2)
        await message.answer_audio(open(path, 'rb'))
        os.remove(path)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(f"Получить скриншот {EMOJIS['SCREENSHOT']}")
        await message.answer('Запись отправлена', reply_markup=markup)
        recording = False
    else:
        await message.answer('Нет активной записи.')

@dp.message_handler(filters.Regexp('Выключить ' + EMOJIS['POWER']))
async def shutdown_with_countdown(message: types.Message):
    await message.answer('Выключаю компьютер...')
    os.system('shutdown /s /t 1')

@dp.message_handler(filters.Regexp('Видео по ссылке ' + EMOJIS['VIDEO']))
async def play_video(message: types.Message):
    await message.answer('Введите ссылку на видео:')
    await dp.current_state(user=message.from_user.id).set_data({'next_action': 'open_video'})

@dp.message_handler(lambda message: 'next_action' in dp.current_state(user=message.from_user.id).get_data() and dp.current_state(user=message.from_user.id).get_data()['next_action'] == 'open_video')
async def open_video(message: types.Message):
    url = message.text
    webbrowser.open(url)
    await message.answer('Видео запущено.')

@dp.message_handler(filters.Regexp('Завершить процесс ' + EMOJIS['PROCESS']))
async def terminate_process(message: types.Message):
    await message.answer('Введите номер процесса для завершения:')
    await dp.current_state(user=message.from_user.id).set_data({'next_action': 'confirm_termination'})

@dp.message_handler(lambda message: 'next_action' in dp.current_state(user=message.from_user.id).get_data() and dp.current_state(user=message.from_user.id).get_data()['next_action'] == 'confirm_termination')
async def confirm_termination(message: types.Message):
    try:
        process_number = int(message.text)
        processes = psutil.process_iter(['pid', 'name'])
        for proc in processes:
            if proc.info['pid'] == process_number:
                process_name = proc.info['name']
                proc.terminate()
                await message.answer(f'Процесс "{process_name}" был завершен.')
                return
        await message.answer('Процесс с указанным номером не найден.')
    except ValueError:
        await message.answer('Некорректный ввод. Пожалуйста, введите число.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
