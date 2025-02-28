import time
import os
import subprocess
import platform  # Импортируем модуль для определения платформы

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Локальная директория для отслеживания
WATCH_DIR = os.path.expanduser("~/programms/Preparation_for_NTO_2024-25/MANIPULATOR")  # на удаленном устройстве будет одноименная папка MANIPULATOR с тем же содержимым 

# Конфигурация удаленного сервера
REMOTE_USER = "pi"                  # Имя пользователя на удалённом сервере
REMOTE_HOST = "192.168.4.1"          # IP-адрес или хост удалённого сервера
REMOTE_DIR = "~"                    # Базовая директория на удалённом сервере (домашняя папка пользователя)


###---------------------------------------------------------------

# Определение платформы
CURRENT_PLATFORM = platform.system()  # Получаем название платформы
LINUX = CURRENT_PLATFORM == "Linux"  # True, если платформа Linux
WINDOWS = CURRENT_PLATFORM == "Windows" 

print(f"Текущая платформа: {CURRENT_PLATFORM}")


FOLDER_NAME = os.path.basename(WATCH_DIR)
# Полный путь на удалённом сервере
REMOTE_FULL_PATH = f"{REMOTE_DIR}/{FOLDER_NAME}"

# Проверка существования локальной директории
if not os.path.exists(WATCH_DIR):
    print(f"Ошибка: Локальная директория {WATCH_DIR} не существует.")
    exit(1)


# Функция для синхронизации
def sync_directories():
    print("Начинаю синхронизацию...")
    try:

        # scp — это утилита для копирования файлов по SSH. Она доступна в Git for Windows. Но нужно чтобы гит был в переменных среды
        # на линукс тоже работает
        
        if WINDOWS:
            subprocess.run(
        ["scp", "-r", f"{WATCH_DIR}/", f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/"], check=True)
        
        
        # На линуксе есть более быстрый инструмент - rsync
        elif LINUX:
            subprocess.run(
                ["rsync", "-r", f"{WATCH_DIR}/", f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_FULL_PATH}/"], check=True)

        else:
            print("Ошибка: Неподдерживаемая платформа.")
            
            
        print("Синхронизация завершена успешно.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка: Синхронизация не удалась. Код ошибки: {e.returncode}")


# Класс для обработки событий файловой системы
class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"Обнаружено изменение: {event.src_path}")
        sync_directories()

    def on_created(self, event):
        print(f"Обнаружено создание файла: {event.src_path}")
        sync_directories()

    def on_deleted(self, event):
        print(f"Обнаружено удаление файла: {event.src_path}")
        sync_directories()


# Запуск отслеживания изменений
if __name__ == "__main__":
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_DIR, recursive=True)
    observer.start()

    print(f"Отслеживание изменений в {WATCH_DIR}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()