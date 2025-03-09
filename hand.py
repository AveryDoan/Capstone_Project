import cv2
import mediapipe as mp
from controller import Controller

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils


# Smoothing parameters
smoothening = 7
plocX, plocY = 0, 0
clocX, clocY = 0, 0


while True:
   success, img = cap.read()
   img = cv2.flip(img, 1)

   imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
   results = hands.process(imgRGB)

   if results.multi_hand_landmarks:
        Controller.hand_Landmarks = results.multi_hand_landmarks[0]
        mpDraw.draw_landmarks(img, Controller.hand_Landmarks, mpHands.HAND_CONNECTIONS)

        Controller.update_fingers_status()
        
        # Get the tip of the index finger
        x1, y1 = Controller.hand_Landmarks.landmark[8].x, Controller.hand_Landmarks.landmark[8].y
        h, w, c = img.shape
        x1, y1 = int(x1 * w), int(y1 * h)
        
        # Smoothen the cursor movement
        clocX = plocX + (x1 - plocX) / smoothening
        clocY = plocY + (y1 - plocY) / smoothening
        
        # Move the cursor
        Controller.cursor_moving(clocX, clocY)
        
        # Update previous location
        plocX, plocY = clocX, clocY
        
        Controller.update_fingers_status()
        Controller.cursor_moving(clocX, clocY)
        Controller.detect_scrolling()
        Controller.detect_zoomming()
        Controller.detect_clicking()
        Controller.detect_dragging()

   cv2.imshow('Hand Tracker', img)
   if cv2.waitKey(5) & 0xff == 27:
      break


cap.release()
cv2.destroyAllWindows()

# DragDrop
# rightclick
# leftclick
# doubleclick
# scroll up
# scroll down
# Zoom in 
# Zoom out