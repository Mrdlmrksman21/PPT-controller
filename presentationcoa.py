import cv2
import os
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# var
width, height = 1920, 1080
folder_path = r"C:\Users\Mridul Vaid\Downloads\python\pptminorproject"
imagenum = 0
buttonPress = False
counter = 0
Flipflop = 10
pen = [[]]
penNumber = -1
penStart = False

#Opticals
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(2, height)

# list of the presentation images
pathImage = sorted(os.listdir(path=folder_path), key=len)
print(pathImage)

detector = HandDetector(detectionCon=0.2, maxHands=2)

def resize_with_aspect_ratio(image, width, height):
    # Get the aspect ratio of the image
    aspect_ratio = image.shape[1] / image.shape[0]
    
    # Calculate the new height and width while maintaining the aspect ratio
    new_width = width
    new_height = int(new_width / aspect_ratio)

    if new_height > height:
        new_height = height
        new_width = int(new_height * aspect_ratio)

    # Resize the image
    resized_image = cv2.resize(image, (new_width, new_height))
    return resized_image

# Get screen resolution
screen_width = 1920  # You can adjust this based on your screen resolution
screen_height = 1080  # You can adjust this based on your screen resolution

while True:
    # hand detector for importing the images
    success, img = cap.read()
    img = cv2.flip(img, 1)
    path_ppt = os.path.join(folder_path, pathImage[imagenum])
    imgcurrent = cv2.imread(path_ppt)
    gestureThreshold = 800

    # hand detection
    hands, img = detector.findHands(img)
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 5)

    # operations
    if hands and buttonPress == False:
        hand = hands[0]
        handType = hand["type"]
        fingure1 = detector.fingersUp(hand)
        cx, cy = hand["center"]
        lmList = hand['lmList']

        # pointer projection
        indexFinger = lmList[8][0], lmList[8][1]

        if len(hands) == 2:
            hand2 = hands[1]
            cx, cy = hand["center"]
            lmList2 = hand2['lmList']
            handType = hand2["type"]

        if cy <= gestureThreshold:  # check the height if the hand is at the detection line or not
            # gesture of 1 - Left
            if fingure1 == [0, 1, 1, 1, 1] and handType == "Left":
                penStart = False
                buttonPress = True
                if imagenum < len(pathImage) - 1:
                    pen = [[]]
                    penNumber = 0
                    imagenum += 1
                print("left")
            # gesture of 2 - Right
            if fingure1 == [0, 1, 1, 1, 1] and handType == "Right":
                buttonPress = True
                penStart = False
                if imagenum > 0:
                    pen = [[]]
                    penNumber = 0
                    imagenum -= 1
                print("Left")

        # Pointer on the ppt
        if fingure1 == [1, 1, 0, 0, 0] and handType == "Left":
            cv2.circle(imgcurrent, indexFinger, 12, (0, -400, -355), cv2.FILLED)
        # Draw on the ppt
        if fingure1 == [0, 1, 0, 0, 0] and handType == "Left":
            if penStart is False:
                penStart = True
                penNumber += 1
                pen.append([])
            cv2.circle(imgcurrent, indexFinger, 12, (0, 400, 355), cv2.FILLED)
            pen[penNumber].append(indexFinger)
        # Remove Drawing from the ppt
        if fingure1 == [1, 1, 1, 0, 0] and handType == "Right":
            if pen:
                if penNumber >= 0:
                    pen.pop(-1)
                    penNumber -= 1
                    buttonPress = True

    # this is to delay the slide change operation
    if buttonPress == True:
        counter += 1
        if counter > Flipflop and buttonPress == True:
            counter = 0
            buttonPress = False

    # pen command or operation stored in it
    for i in range(len(pen)):
        for j in range(len(pen[i])):
            if j != 0:
                cv2.line(imgcurrent, pen[i][j-1], pen[i][j], (0, 200, 200), 12)

    # Resize both the webcam feed (face) and PPT slides to fit the full screen with aspect ratio
    img_resized = resize_with_aspect_ratio(img, screen_width // 2, screen_height)  # Resize webcam feed with aspect ratio
    imgcurrent_resized = resize_with_aspect_ratio(imgcurrent, screen_width // 2, screen_height)  # Resize PPT image

    # Stack both images side by side
    combined = np.hstack((img_resized, imgcurrent_resized))  # Use numpy's hstack for combining images

    # Display the stacked image in full screen
    cv2.namedWindow("Presentation and Face", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Presentation and Face", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Presentation and Face", combined)

    key = cv2.waitKey(1)
    if key == ord("a"):
        break

cv2.destroyAllWindows()
