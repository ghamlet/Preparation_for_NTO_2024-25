# hello
"""Программа для выделения перспективы с изображения по точкам отмеченным с помощью мышки """


import cv2
import numpy as np


img = cv2.imread("change_of_perspective/images/ObjectCam.jpg") # загружаем изображение га котором будем искать совпадения

#отмечаем точки на исходном изображении для трансформации
pts1 = np.float32([[180,164],
                   [300,30],
                   
                   [575,340],
                   [630,140],])


NEW_SIZE = 500          # размер в пикселях нового изображения, логично что получится квадрат
pts2 = np.float32([[0,0],[NEW_SIZE, 0], [0, NEW_SIZE], [NEW_SIZE, NEW_SIZE]]) # координаты прошлых точек на новом изображении после трансформации

M = cv2.getPerspectiveTransform(pts1,pts2)           # получение перспективы
dst = cv2.warpPerspective(img,M,(NEW_SIZE, NEW_SIZE))


template = cv2.imread('change_of_perspective/images/car.png') # шаблон
h, w = template.shape[:2]
res = cv2.matchTemplate(dst, template, cv2.TM_CCOEFF_NORMED)

threshold = 0.8  
loc = np.where(res >= threshold)

# Рисование прямоугольников вокруг совпадений
for pt in zip(*loc[::-1]): 
    cv2.rectangle(dst, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)




pointsList = []

def mousePoints(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        # size = len(pointsList)
        # if size != 0 and size % 3 != 0:
        #     cv2.line(img, tuple(pointsList[round((size-1)/3)*3]), (x,y), (255, 0, 0))
        #     cv2.imshow("input",img)
        #     cv2.waitKey(1)
        
        cv2.circle(img, (x,y), 5,(0,0,255), cv2.FILLED)
        pointsList.append([x,y])



hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)


while True:

    

    cv2.imshow("input",img)
    cv2.setMouseCallback("input", mousePoints)


    cv2.imshow("transform", dst)

    k = cv2.waitKey(10)
    
    # при нажатии на клавишу q программа завершится
    if k == ord('q'):
        break

    
