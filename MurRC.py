import telebot
import platform
import os
import psutil
import webbrowser
import time
import requests
import mouse
import tempfile
from PIL import ImageGrab
from pygetwindow import getWindowsWithTitle
import sounddevice as sd
import numpy as np
import wavio
from screeninfo import get_monitors as screeninfo
import urllib.request
my_id = 6323712252
bot = telebot.TeleBot('6367707654:AAGF8iXELjKakdxkGUBvVe92utXOw8Y_WjI')
recording = False
EMOJI_SCREENSHOT = "📸"
EMOJI_WEBCAM = "🎥"
EMOJI_CPU = "💻"
EMOJI_PROCESS = "🔄"
EMOJI_MIC = "🎤"
EMOJI_POWER = "⚡"
EMOJI_APP = "📲"
EMOJI_SPOTIFY = "🎵"
EMOJI_DISCORD = "💬"
EMOJI_CHROME = "🌐"
EMOJI_BACK = "🔙"
EMOJI_VIDEO = "📺"
EMOJI_MISH_EBANAYA = "🖱️"
@bot.message_handler(regexp='Управление мышью')
def handle_mouse_control(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("↑ Вверх", "⬅️ Влево", "➡️ Вправо")
    markup.row("⬇️ Вниз", "🖱 Клик", "⏪ Вернуться в главное меню")
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)

@bot.message_handler(regexp='Клик')
def handle_mouse_click(message):
    mouse.click()

@bot.message_handler(regexp='⬅️ Влево')
def handle_mouse_move_left(message):
    mouse.move(-50, 0, absolute=False, duration=0.2)

@bot.message_handler(regexp='↑ Вверх')
def handle_mouse_move_up(message):
    mouse.move(0, -50, absolute=False, duration=0.2)

@bot.message_handler(regexp='⬇️ Вниз')
def handle_mouse_move_down(message):
    mouse.move(0, 50, absolute=False, duration=0.2)

@bot.message_handler(regexp='➡️ Вправо')
def handle_mouse_move_right(message):
    mouse.move(50, 0, absolute=False, duration=0.2)

@bot.message_handler(regexp='⏪ Вернуться в главное меню')
def return_to_main_menu(message):
    send_welcome(message)

@bot.message_handler(func=lambda message: message.text == "Получить информацию о компьютере")
def send_computer_info_request(message):
    bot.send_message(message.chat.id, "Получение информации о компьютере…")
    computer_info(message)

@bot.message_handler(regexp='Клик мышью')
def handle_mouse_click(message):
    mouse.click()

@bot.message_handler(regexp='Переместить мышь влево')
def handle_mouse_move_left(message):
    mouse.move(-50, 0, absolute=False, duration=0.2)

@bot.message_handler(regexp='Переместить мышь вправо')
def handle_mouse_move_right(message):
    mouse.move(50, 0, absolute=False, duration=0.2)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Переместить мышь влево")
    markup.add("Переместить мышь вправо")
    
@bot.message_handler(regexp='⏪Назад⏪')
def return_to_main_menu(message):
    send_welcome(message)
    
@bot.message_handler(regexp=f'Видео по ссылке')
def play_video(message):
    bot.send_message(message.chat.id, 'Введите ссылку на видео:')
    bot.register_next_step_handler(message, open_video)

def open_video(message):
    try:
        url = message.text
        webbrowser.open(url)
        bot.send_message(message.chat.id, 'Видео запущено.')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка: {e}')



@bot.message_handler(regexp=f'получить информацию о процессах {EMOJI_PROCESS}')
def get_processes_info(message):
    processes = get_active_processes_info()
    for chunk in chunks(processes, 8):
        processes_info = '\n'.join(chunk)
        bot.send_message(message.chat.id, processes_info)

def get_system_load():
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    memory_total = round(memory.total / (1024**3), 2)
    memory_used = round(memory.used / (1024**3), 2)
    gpu_percent = 'недоступно'  
    return f"{EMOJI_CPU} CPU {cpu_percent}%\nПамять: {memory_used} ГБ / {memory_total} ГБ ({memory_percent}%)\nGPU: {gpu_percent}%"

def get_active_processes_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(f"PID: {proc.info['pid']}, Имя: {proc.info['name']}, CPU: {proc.info['cpu_percent']}%, Память: {proc.info['memory_percent']}%")
    return processes

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_top_processes():
    processes = []
    for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), key=lambda x: x.info['cpu_percent'], reverse=True)[:5]:
        processes.append(f"PID: {proc.info['pid']}, Имя: {proc.info['name']}, CPU: {proc.info['cpu_percent']}%")
    return processes       

@bot.message_handler(regexp=f'Сведения о нагрузке {EMOJI_CPU}')
def get_system_load_info(message):
    load_info = get_system_load()
    top_processes = get_top_processes()
    processes_info = "\n".join(top_processes)
    bot.send_message(message.chat.id, f"{load_info}\n\nСамые нагруженные программы:\n{processes_info}")

@bot.message_handler(regexp=f'завершить процесс {EMOJI_PROCESS}')
def terminate_process(message):
    bot.send_message(message.chat.id, 'Введите номер процесса для завершения:')
    bot.register_next_step_handler(message, confirm_termination)

@bot.message_handler(regexp=f'записать звук {EMOJI_MIC}')
def start_recording(message):
    global recording
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(f"Отправить запись {EMOJI_MIC}")
    bot.send_message(message.chat.id, 'Начинаю запись...', reply_markup=markup)
    recording = True

@bot.message_handler(regexp=f'выключить {EMOJI_POWER}')
def shutdown_with_countdown(message):
    bot.send_message(message.chat.id, 'Выключаю компьютер...')
    for i in range(3, 0, -1):
        bot.send_message(message.chat.id, str(i))
        time.sleep(1)
    os.system('shutdown /s /t 1')

@bot.message_handler(regexp=f'отправить запись {EMOJI_MIC}')
def send_audio(message):
    global recording
    if recording:
        bot.send_message(message.chat.id, 'Заканчиваю запись...')
        path = tempfile.gettempdir() + '/audio.wav'
        duration = 5
        fs = 44100
        recording_data = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype=np.int16)
        sd.wait()
        wavio.write(path, recording_data, fs, sampwidth=2)
        with open(path, 'rb') as audio_file:
            bot.send_audio(message.chat.id, audio_file)
        os.remove(path)
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(f"Получить скриншот {EMOJI_SCREENSHOT}")
        markup.add(f"Получить скриншот с вебкамеры {EMOJI_WEBCAM}")
        markup.add(f"получить информацию о процессах {EMOJI_PROCESS}")
        markup.add(f"выключить {EMOJI_POWER}")
        markup.add(f"записать звук {EMOJI_MIC}")
        bot.send_message(message.chat.id, 'Запись отправлена', reply_markup=markup)
        recording = False
    else:
        bot.send_message(message.chat.id, 'Нет активной записи.')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(f"Получить скриншот {EMOJI_SCREENSHOT}")
    markup.add(f"Получить скриншот с вебкамеры {EMOJI_WEBCAM}")
    markup.add(f"Сведения о нагрузке {EMOJI_CPU}")  
    markup.add(f"Получить информацию о процессах {EMOJI_PROCESS}")
    markup.add(f"Завершить процесс {EMOJI_PROCESS}")
    markup.add(f"Записать звук {EMOJI_MIC}")
    markup.add(f"Выключить {EMOJI_POWER}")
    markup.add(f"Запустить программу {EMOJI_APP}")
    markup.add(f"Видео по ссылке {EMOJI_VIDEO}")
    markup.add(f"Управление мышью {EMOJI_MISH_EBANAYA}")
    bot.send_message(message.chat.id, 'Компьютер запущен', reply_markup=markup)

@bot.message_handler(regexp=f'Запустить программу {EMOJI_APP}')
def choose_program(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(f"Spotify {EMOJI_SPOTIFY}")
    markup.add(f"Discord {EMOJI_DISCORD}")
    markup.add(f"Chrome {EMOJI_CHROME}")
    markup.add(f"Вернуться назад {EMOJI_BACK}")
    bot.send_message(message.chat.id, 'Выберите программу:', reply_markup=markup)

@bot.message_handler(regexp=f'Spotify {EMOJI_SPOTIFY}')
def open_spotify(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(f"Вернуться назад {EMOJI_BACK}")
    bot.send_message(message.chat.id, 'Запущено Spotify.', reply_markup=markup)
    webbrowser.open('C:/Users/Savva/AppData/Roaming/Spotify/Spotify.exe')

@bot.message_handler(regexp=f'Discord {EMOJI_DISCORD}')
def open_discord(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(f"Вернуться назад {EMOJI_BACK}")
    bot.send_message(message.chat.id, 'Запущен Discord.', reply_markup=markup)
    webbrowser.open('C:/ProgramData/Savva/Discord/Updater.exe')

@bot.message_handler(regexp=f'Chrome {EMOJI_CHROME}')
def open_chrome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(f"Вернуться назад {EMOJI_BACK}")
    bot.send_message(message.chat.id, 'Запущен Chrome.', reply_markup=markup)
    webbrowser.open('C:/Program Files/Google/Chrome/Application/chrome.exe')

@bot.message_handler(regexp=f'получить скриншот {EMOJI_SCREENSHOT}')
def get_screenshot(message):
    path = tempfile.gettempdir() + '/screenshot.png'
    screenshot = ImageGrab.grab()
    screenshot.save(path, 'PNG')
    bot.send_photo(message.chat.id, open(path, 'rb'))

@bot.message_handler(regexp=f'получить скриншот с вебкамеры {EMOJI_WEBCAM}')
def get_webcam_screenshot(message):
    camera_window = getWindowsWithTitle("Camera Preview")
    if len(camera_window) > 0:
        camera_window[0].activate()
        screenshot = ImageGrab.grab(bbox=camera_window[0]._rect)
        path = tempfile.gettempdir() + '/webcam_screenshot.png'
        screenshot.save(path, 'PNG')
        bot.send_photo(message.chat.id, open(path, 'rb'))
    else:
        bot.send_message(message.chat.id, 'Не удалось найти окно с камерой')

@bot.message_handler(regexp=f'Вернуться назад {EMOJI_BACK}')
def return_to_main_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(f"Получить скриншот {EMOJI_SCREENSHOT}")
    markup.add(f"Получить скриншот с вебкамеры {EMOJI_WEBCAM}")
    markup.add(f"Сведения о нагрузке {EMOJI_CPU}")
    markup.add(f"Получить информацию о процессах {EMOJI_PROCESS}")
    markup.add(f"Завершить процесс {EMOJI_PROCESS}")
    markup.add(f"Записать звук {EMOJI_MIC}")
    markup.add(f"Выключить {EMOJI_POWER}")
    markup.add(f"Запустить программу {EMOJI_APP}")
    markup.add(f"Видео по ссылке {EMOJI_VIDEO}")
    markup.add(f"Управление мышью {EMOJI_MISH_EBANAYA}")
    bot.send_message(message.chat.id, 'Вы вернулись в основное меню', reply_markup=markup)

def confirm_termination(message):
    try:
        process_number = int(message.text)
        processes = psutil.process_iter(['pid', 'name'])
        for proc in processes:
            if proc.info['pid'] == process_number:
                process_name = proc.info['name']
                proc.terminate()
                bot.send_message(message.chat.id, f'Процесс "{process_name}" был завершен.')
                return
        bot.send_message(message.chat.id, 'Процесс с указанным номером не найден.')
    except ValueError:
        bot.send_message(message.chat.id, 'Некорректный ввод. Пожалуйста, введите число.')

bot.infinity_polling()
