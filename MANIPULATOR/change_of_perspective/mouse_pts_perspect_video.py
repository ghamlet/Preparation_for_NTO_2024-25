""" Программа для выделения перспективы с видео по точкам отмеченным с помощью мышки.
При расставлении точек важно соблюдать порядок их выделения: первая точка ставится в любом месте,
вторая на смежной стороне, очень важно чтобы третья точка была по диагонали от второй,
четвертая в оставшееся место"""


import cv2  
import numpy as np
import os


cap = cv2.VideoCapture(0)   # захват видео

     
NEW_SIZE = 500      # размер в пикселях нового изображения
MAIN_DIR = os.path.dirname(__file__)

pts2 = np.float32([[0,0],[NEW_SIZE,0],[0,NEW_SIZE],[NEW_SIZE,NEW_SIZE]]) # координаты прошлых точек на новом изображении после трансформации

pointsList = []
minb, ming, minr, maxb, maxg, maxr = None, None,None, None,None, None

points_of_quadr = False
is_pressed_y = False
setting_up_trackers = True


def delete_last_added_point():
    """ 
    При нажатии на клавишу `x` удаляется последняя размеченная точка
    """
    
    global pointsList
    pointsList = pointsList[:-1]
    
    
    
def render_points_on_video():
    """
    Отображение видеопотока с наложенными на него отмеченными точками
    """
    
    global copy_img 
    
    
    s, img = cap.read()  # чтение кадра
    if not s:  # если не удалось считать - выходим
        exit()
    
    copy_img = img.copy()   # копия изображения

    # отрисовываем отмеченные точки
    for pt in pointsList:
        cv2.circle(img, pt, 5,(0,0,255), cv2.FILLED)
        
    cv2.imshow("input", img)  # показываем входное изображение
    


def handle_key_press(close_all_windows = False):
    """
    Обрабатывает нажатия клавиш и выполняет соответствующие действия
    """
    
    global points_of_quadr, setting_up_trackers, is_pressed_y

    k = cv2.waitKey(1)
    
    if k == ord('q'):  # Выход из программы
        exit()
    
    elif k == ord('y'):  # Обработка нажатия 'y'
        is_pressed_y = True
        
        
    elif k == ord('x'):  # Удаление последней добавленной точки
        if close_all_windows:
            cv2.destroyAllWindows()
            
        delete_last_added_point()
        
        points_of_quadr = False
        is_pressed_y = False
        setting_up_trackers = False


    elif k == ord('s'):  # при нажатии клавиши s вам предложат ввести описание для значения порогового цвета и само значение сохранится в текстовый файл
        if all(var is not None for var in [minb, ming, minr, maxb, maxg, maxr]): # проверка что переменные существуют
        
            with open(os.path.join(MAIN_DIR, "trackbars_save.txt"), "a") as f:
                title = input("\nEnter the description \nTo cancel, write message no: ")
                
                if title not in ("n", "N", "no", "No", "NO"):
                    # print(ming, minr}, {maxb, maxg, maxr)
                    f.write(f"{title}:  {minb, ming, minr}, {maxb, maxg, maxr}" +"\n")
                    print("save\n")



def mousePoints(event, x, y, flags, params):
    global points_of_quadr
     
    # если отмечено 4 точки то выходим из цикла и ждем нажатия клавиши y
    if len(pointsList) % 4 == 0 and len(pointsList) != 0:
        points_of_quadr = True
            
    if event == cv2.EVENT_LBUTTONDOWN: 
        if len(pointsList) < 4: 
            pointsList.append([x,y])

    

def trackbar(minblue=0, mingreen=0, minred=0, maxblue=255, maxgreen=255, maxred=255):
    """
    Создание трекеров для каждого цвета
    """

    cv2.namedWindow( "Trackbar")
    cv2.createTrackbar('minb', 'Trackbar', minblue, 255, lambda x: None)
    cv2.createTrackbar('ming', 'Trackbar', mingreen, 255, lambda x: None)
    cv2.createTrackbar('minr', 'Trackbar', minred, 255, lambda x: None)
    cv2.createTrackbar('maxb', 'Trackbar', maxblue, 255, lambda x: None)
    cv2.createTrackbar('maxg', 'Trackbar', maxgreen, 255, lambda x: None)
    cv2.createTrackbar('maxr', 'Trackbar', maxred, 255, lambda x: None)




while True:
    
    # программа будет висеть во вложенном цикле пока на фото не будет отмечено четыре точки
    while not points_of_quadr:
        
        render_points_on_video()        
        # важно чтобы эти два окна имели одинаковое название
        cv2.setMouseCallback("input", mousePoints)
                
        handle_key_press()
      


    # ждем подтверждения выбранных точек
    while not is_pressed_y:
        
        render_points_on_video()
        handle_key_press()

    
    
    # если в массиве появилось 4 точки то можно находить перспективу
    print(pointsList)

    pts1 = np.float32(pointsList)
    M = cv2.getPerspectiveTransform(pts1, pts2) #получение перспективы
    
    trackbar() # создаем окно с трекбарами
    setting_up_trackers = True
    

    # в бесконечном цикле считываем положения ползунков для получения значений цветов
    while setting_up_trackers:

        render_points_on_video()
                
        dst = cv2.warpPerspective(copy_img, M,(NEW_SIZE, NEW_SIZE))
        cv2.imshow("transform", dst)


        hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)

        minb = cv2.getTrackbarPos('minb', 'Trackbar')
        ming = cv2.getTrackbarPos('ming', 'Trackbar')
        minr = cv2.getTrackbarPos('minr', 'Trackbar')
        maxb = cv2.getTrackbarPos('maxb', 'Trackbar')
        maxg = cv2.getTrackbarPos('maxg', 'Trackbar')
        maxr = cv2.getTrackbarPos('maxr', 'Trackbar')

        # применяем пороги цветов
        mask = cv2.inRange(hsv,(minb,ming,minr),(maxb,maxg,maxr))

        #пиксели подходящего цвета останутся своего цвета а все остальные станут черными
        result = cv2.bitwise_and(dst, dst, mask=mask)
        cv2.imshow('result', result)
        
        
        handle_key_press(close_all_windows=True)

      
           
