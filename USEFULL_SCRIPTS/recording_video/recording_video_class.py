import cv2
import time
import os


class VideoRecorder:
    def __init__(self, camera_index=0, output_file="output_video.mp4"):
        """
        Инициализация видеорекордера. 
        
        :param camera_index: Индекс камеры (по умолчанию 0).
        :param output_file: Базовое имя выходного файла.
        """
        self.camera_index = camera_index
        self.output_file = output_file


        self.cap = None
        self.video_writer = None
        self.codecs_to_test = ['mp4v', 'avc1', 'X264', 'XVID', 'MJPG']
        self.frame_width = None
        self.frame_height = None


    def find_supported_codec(self, fps):
        """
        Находит первый поддерживаемый кодек из списка.
        
        :param fps: Количество кадров в секунду.
        :return: Кодек или None, если ни один не поддерживается.
        """
        
        for codec in self.codecs_to_test:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec)
                out = cv2.VideoWriter(f"test_{codec}.mp4", fourcc, fps, (self.frame_width, self.frame_height))
                
                if out.isOpened():
                    print(f"Кодек {codec} поддерживается и будет использован.")
                    out.release()
                    return codec
                else:
                    print(f"Кодек {codec} не поддерживается.")
                    
            except Exception as e:
                print(f"Ошибка с кодеком {codec}: {e}")
                
        return None


    def initialize_video_writer(self, codec, fps):
        """
        Инициализирует объект VideoWriter для записи видео.
        
        :param codec: Кодек для записи.
        :param fps: Количество кадров в секунду.
        """
        
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self.video_writer = cv2.VideoWriter(self.output_file, fourcc, fps, (self.frame_width, self.frame_height))


    def calculate_fps(self, start_time, frame_count):
        """
        Вычисляет реальный FPS на основе времени и количества кадров.
        
        :param start_time: Время начала записи.
        :param frame_count: Количество кадров.
        :return: Текущий FPS.
        """
        
        elapsed_time = time.time() - start_time
        return frame_count / elapsed_time


    def measure_average_fps(self, duration=5):
        """
        Измеряет средний FPS за указанное время (в секундах).
        
        :param duration: Длительность измерения FPS.
        :return: Средний FPS.
        """
        
        start_time = time.time()
        frame_count = 0

        print(f"Измерение среднего FPS в течение {duration} секунд...")

        while time.time() - start_time < duration:
            ret, frame = self.cap.read()
            if not ret:
                break

            if frame is not None:
                frame_count += 1
            time.sleep(0.001)  # Небольшая задержка, чтобы не нагружать CPU

        average_fps = frame_count / duration
        print(f"Средний FPS: {average_fps:.2f}")
        return average_fps


    def get_unique_output_filename(self):
        """
        Генерирует уникальное имя файла, чтобы избежать перезаписи.
        
        :return: Уникальное имя файла.
        """
        
        # Этот код гарантирует, что каждый раз, когда вы создаете новый файл, его имя будет уникальным. 
        # Если файлы с именами output_video1.mp4, output_video2.mp4 и т.д. уже существуют, он автоматически создаст файл с следующим доступным номером (например, output_video3.mp4).
        
        base_name, ext = os.path.splitext(self.output_file)  #
        counter = 1
        
        while os.path.exists(f"{base_name}{counter}{ext}"):
            counter += 1
            
        return f"{base_name}{counter}{ext}"


    def start_recording(self):
        """
        Запускает процесс записи видео.
        """
        
        # Инициализация видеозахвата
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("Ошибка: Не удалось открыть камеру.")
            return

        # Определение максимального разрешения камеры
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Измерение среднего FPS
        average_fps = self.measure_average_fps(duration=5)

        # Поиск поддерживаемого кодека
        selected_codec = self.find_supported_codec(average_fps)
        if selected_codec is None:
            print("Ни один из кодеков не поддерживается. Запись видео невозможна.")
            return

        # Генерация уникального имени файла
        self.output_file = self.get_unique_output_filename()
        print(f"Используемое имя файла: {self.output_file}")

        # Инициализация VideoWriter с измеренным FPS
        self.initialize_video_writer(selected_codec, average_fps)

        # Основной цикл обработки кадров
        print("Начало записи видео...")
        start_time = time.time()
        frame_count = 0

        while True:
            ret, frame = self.cap.read()
            if not ret:  # Если кадр не получен, выходим из цикла
                break

            # Отображение кадра
            cv2.imshow("Recording Frame", frame)

            # Запись кадра в видео
            self.video_writer.write(frame)

            # Подсчет FPS
            frame_count += 1
            current_fps = self.calculate_fps(start_time, frame_count)
            print(f"Текущий FPS: {current_fps:.2f}")

            # Выход по нажатию клавиши 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

       


# Пример использования
if __name__ == "__main__":
    CAMERA_ID = 0
    OUTPUT_VIDEO = "output_video.mp4"

    recorder = VideoRecorder(camera_index=CAMERA_ID, output_file=OUTPUT_VIDEO)
    recorder.start_recording()