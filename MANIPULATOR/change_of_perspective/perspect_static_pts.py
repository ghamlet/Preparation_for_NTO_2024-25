"""Программа для выделения перспективы с изображения по фиксированным точкам"""


import cv2
import numpy as np


img = cv2.imread("for_MANIPULATOR/change_of_perspective/images/ObjectCam.jpg") #загружаем изображение
cv2.imshow("input",img)           #выводим загруженное изображение на экран
cv2.waitKey(1)                    #задержка для отображения изображения

#отмечаем точки на исходном изображении для трансформации
pts1 = np.float32([[180,164],
                   [300,30],
                   
                   [575,340],
                   [630,140],])


NEW_SIZE = 500 #размер в пикселях нового изображения, логично что получится квадрат
pts2 = np.float32([[0,0],[NEW_SIZE,0],[0,NEW_SIZE],[NEW_SIZE,NEW_SIZE]]) # координаты прошлых точек на новом изображении после трансформации

M = cv2.getPerspectiveTransform(pts1,pts2) #получение перспективы
dst = cv2.warpPerspective(img,M,(NEW_SIZE, NEW_SIZE))


#псевдофункция
def nothing(x):
    ...


def trackbar(minblue=0, mingreen=0, minred=0, maxblue=255, maxgreen=255, maxred=255):
    # создание трекеров для каждого цвета

    cv2.namedWindow( "trackbar")
    cv2.createTrackbar('minb', 'trackbar', minblue, 255, nothing)
    cv2.createTrackbar('ming', 'trackbar', mingreen, 255, nothing)
    cv2.createTrackbar('minr', 'trackbar', minred, 255, nothing)
    cv2.createTrackbar('maxb', 'trackbar', maxblue, 255, nothing)
    cv2.createTrackbar('maxg', 'trackbar', maxgreen, 255, nothing)
    cv2.createTrackbar('maxr', 'trackbar', maxred, 255, nothing)


trackbar()


hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)


while True:
    #в бесконечном цикле считываем положения ползунков для получения значений цветов

    minb = cv2.getTrackbarPos('minb', 'trackbar')
    ming = cv2.getTrackbarPos('ming', 'trackbar')
    minr = cv2.getTrackbarPos('minr', 'trackbar')
    maxb = cv2.getTrackbarPos('maxb', 'trackbar')
    maxg = cv2.getTrackbarPos('maxg', 'trackbar')
    maxr = cv2.getTrackbarPos('maxr', 'trackbar')

    # применяем пороги цветов
    mask = cv2.inRange(hsv,(minb,ming,minr),(maxb,maxg,maxr))

    #пиксели подходящего цвета останутся своего цвета а все остальные станут черными
    result = cv2.bitwise_and(dst, dst, mask=mask)

    cv2.imshow('result', result)
    cv2.imshow("transform", dst)

    k = cv2.waitKey(10)
    # при нажатии на клавишу q программа завершится
    if k == ord('q'):
        break

    elif k == ord('s'):  # при нажатии клавиши s вам предложат ввести описание для значения порогового цвета и само значение сохранится в текстовый файл
        with open("trackbars_save.txt", "a") as f:
            title = input("\nEnter the description \nTo cancel, write no: ")
            
            if title not in ("n", "N", "no", "No", "NO"):
                f.write(f"{title}:  {minb, ming, minr}, {maxb, maxg, maxr}" +"\n")
                print("save\n")
    