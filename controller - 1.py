import pyautogui
import time
import numpy as np

class Controller:
    def __init__(self, cam_width, cam_height, frame_reduction):
        # Basic initialization
        self.screen_width, self.screen_height = pyautogui.size()
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.frame_reduction = frame_reduction
        
        # Movement control
        self.prev_x, self.prev_y = 0, 0
        self.smoothening = 7
        
        # Hand tracking
        self.hand_landmarks = None
        self.prev_hand = None
        
        # Gesture states
        self.right_clicked = False
        self.left_clicked = False
        self.double_clicked = False
        self.dragging = False
        
        # Finger states
        self.little_finger_down = None
        self.little_finger_up = None
        self.index_finger_down = None
        self.index_finger_up = None
        self.middle_finger_down = None
        self.middle_finger_up = None
        self.ring_finger_down = None
        self.ring_finger_up = None
        self.thumb_finger_down = None
        self.thumb_finger_up = None
        
        # Combined states
        self.all_fingers_down = None
        self.all_fingers_up = None
        self.index_finger_within_thumb = None
        self.middle_finger_within_thumb = None
        self.little_finger_within_thumb = None
        self.ring_finger_within_thumb = None
        
        # Status
        self.gesture_description = "Tracking"

    def update_fingers_status(self):
        if not self.hand_landmarks:
            return
        
        # Finger status updates
        self.little_finger_down = self.hand_landmarks.landmark[20].y > self.hand_landmarks.landmark[17].y
        self.little_finger_up = self.hand_landmarks.landmark[20].y < self.hand_landmarks.landmark[17].y
        self.index_finger_down = self.hand_landmarks.landmark[8].y > self.hand_landmarks.landmark[5].y
        self.index_finger_up = self.hand_landmarks.landmark[8].y < self.hand_landmarks.landmark[5].y
        self.middle_finger_down = self.hand_landmarks.landmark[12].y > self.hand_landmarks.landmark[9].y
        self.middle_finger_up = self.hand_landmarks.landmark[12].y < self.hand_landmarks.landmark[9].y
        self.ring_finger_down = self.hand_landmarks.landmark[16].y > self.hand_landmarks.landmark[13].y
        self.ring_finger_up = self.hand_landmarks.landmark[16].y < self.hand_landmarks.landmark[13].y
        self.thumb_finger_down = self.hand_landmarks.landmark[4].y > self.hand_landmarks.landmark[13].y
        self.thumb_finger_up = self.hand_landmarks.landmark[4].y < self.hand_landmarks.landmark[13].y
        
        # Combined states
        self.all_fingers_down = (self.index_finger_down and self.middle_finger_down and 
                               self.ring_finger_down and self.little_finger_down)
        self.all_fingers_up = (self.index_finger_up and self.middle_finger_up and 
                             self.ring_finger_up and self.little_finger_up)
        
        # Finger-thumb interactions
        self.index_finger_within_thumb = (self.hand_landmarks.landmark[8].y > self.hand_landmarks.landmark[4].y and 
                                        self.hand_landmarks.landmark[8].y < self.hand_landmarks.landmark[2].y)
        self.middle_finger_within_thumb = (self.hand_landmarks.landmark[12].y > self.hand_landmarks.landmark[4].y and 
                                         self.hand_landmarks.landmark[12].y < self.hand_landmarks.landmark[2].y)
        self.little_finger_within_thumb = (self.hand_landmarks.landmark[20].y > self.hand_landmarks.landmark[4].y and 
                                         self.hand_landmarks.landmark[20].y < self.hand_landmarks.landmark[2].y)
        self.ring_finger_within_thumb = (self.hand_landmarks.landmark[16].y > self.hand_landmarks.landmark[4].y and 
                                       self.hand_landmarks.landmark[16].y < self.hand_landmarks.landmark[2].y)

        # Combined states with descriptions
        if self.all_fingers_down:
            self.gesture_description = "All Fingers Down"
        elif self.all_fingers_up:
            self.gesture_description = "All Fingers Up"
        
        # Finger-thumb interaction descriptions
        if self.index_finger_within_thumb:
            self.gesture_description = "Index-Thumb Pinch"
        elif self.middle_finger_within_thumb:
            self.gesture_description = "Middle-Thumb Pinch"
        elif self.ring_finger_within_thumb:
            self.gesture_description = "Ring-Thumb Pinch"
        elif self.little_finger_within_thumb:
            self.gesture_description = "Little-Thumb Pinch"

    def get_position(self, hand_x_position, hand_y_position):
        # Convert to screen coordinates with boundary protection
        x3 = np.interp(hand_x_position, 
                      (self.frame_reduction/self.cam_width, 1-self.frame_reduction/self.cam_width), 
                      (0, self.screen_width))
        y3 = np.interp(hand_y_position, 
                      (self.frame_reduction/self.cam_height, 1-self.frame_reduction/self.cam_height), 
                      (0, self.screen_height))
        
        # Smoothen values
        curr_x = self.prev_x + (x3 - self.prev_x) / self.smoothening
        curr_y = self.prev_y + (y3 - self.prev_y) / self.smoothening
        
        # Update previous positions
        self.prev_x, self.prev_y = curr_x, curr_y
        
        # Ensure within screen bounds
        curr_x = max(0, min(curr_x, self.screen_width))
        curr_y = max(0, min(curr_y, self.screen_height))
        
        return int(curr_x), int(curr_y)

    def cursor_moving(self):
        if not self.hand_landmarks:
            return
            
        # Use index finger tip for cursor control
        x = self.hand_landmarks.landmark[9].x
        y = self.hand_landmarks.landmark[9].y
        
        # Only move if cursor not frozen
        if not (self.all_fingers_up and self.thumb_finger_down):
            screen_x, screen_y = self.get_position(x, y)
            pyautogui.moveTo(screen_x, screen_y, duration=0)
            self.gesture_description = "Moving Cursor"
        else:
            self.gesture_description = "Cursor Frozen"

    def detect_scrolling(self):
        scroll_step = 20  # Smaller steps for bit-by-bit scrolling (adjustable)
        scroll_cooldown = 0.5  # Time in seconds between scroll steps
        current_time = time.time()
        
        # Check if enough time has passed since last scroll
        if not hasattr(self, '_last_scroll_time'):
            self._last_scroll_time = 0
        
        if current_time - self._last_scroll_time < scroll_cooldown:
            return

        # Scrolling up: middle, ring, and little fingers down, index finger up
        scroll_up_condition = (self.middle_finger_down and self.ring_finger_down and 
                               self.little_finger_down and self.index_finger_up)

        # Scrolling down: index, middle, and ring fingers down, little finger up
        scroll_down_condition = (self.index_finger_down and self.middle_finger_down and 
                                 self.ring_finger_down and self.little_finger_up)

        if scroll_up_condition:
            pyautogui.scroll(scroll_step)  # Scroll up
            self.gesture_description = "Scrolling UP"
            self._last_scroll_time = current_time

        elif scroll_down_condition:
            pyautogui.scroll(-scroll_step)  # Scroll down
            self.gesture_description = "Scrolling DOWN"
            self._last_scroll_time = current_time

    def detect_zooming(self):
        # Zoom in: index and middle fingers up, ring and little fingers down
        zooming_in = (self.index_finger_up and self.middle_finger_up and 
                     self.ring_finger_down and self.little_finger_down)
        
        # Zoom out: index and little fingers up, middle and ring fingers down
        zooming_out = (self.index_finger_up and self.little_finger_up and 
                      self.middle_finger_down and self.ring_finger_down)
        
        if zooming_out:
            pyautogui.keyDown('command')
            pyautogui.press('-')
            pyautogui.keyUp('command')
            self.gesture_description = "Zooming Out"

        if zooming_in:
            pyautogui.keyDown('command')
            pyautogui.press('+')
            pyautogui.keyUp('command')
            self.gesture_description = "Zooming In"

    def detect_clicking(self):
        left_click_condition = (self.index_finger_within_thumb and self.middle_finger_up and 
                              self.ring_finger_up and self.little_finger_up and 
                              not self.middle_finger_within_thumb and not self.ring_finger_within_thumb and 
                              not self.little_finger_within_thumb)
        if not self.left_clicked and left_click_condition:
            pyautogui.click()
            self.left_clicked = True
            self.gesture_description = "Left Clicking"
        elif not self.index_finger_within_thumb:
            self.left_clicked = False

        right_click_condition = (self.middle_finger_within_thumb and self.index_finger_up and 
                               self.ring_finger_up and self.little_finger_up and 
                               not self.index_finger_within_thumb and not self.ring_finger_within_thumb and 
                               not self.little_finger_within_thumb)
        if not self.right_clicked and right_click_condition:
            pyautogui.rightClick()
            self.right_clicked = True
            self.gesture_description = "Right Clicking"
        elif not self.middle_finger_within_thumb:
            self.right_clicked = False

        double_click_condition = (self.ring_finger_within_thumb and self.index_finger_up and 
                                self.middle_finger_up and self.little_finger_up and 
                                not self.index_finger_within_thumb and not self.middle_finger_within_thumb and 
                                not self.little_finger_within_thumb)
        if not self.double_clicked and double_click_condition:
            pyautogui.doubleClick()
            self.double_clicked = True
            self.gesture_description = "Double Clicking"
        elif not self.ring_finger_within_thumb:
            self.double_clicked = False

    def detect_dragging(self):
        if not self.dragging and self.all_fingers_down:
            pyautogui.mouseDown(button="left")
            self.dragging = True
            self.gesture_description = "Dragging"
        elif not self.all_fingers_down and self.dragging:
            pyautogui.mouseUp(button="left")
            self.dragging = False

    def update_gesture_description(self):
        """Update gesture description based on current state and actions"""
        if self.dragging:
            self.gesture_description = "Dragging"
        elif self.left_clicked:
            self.gesture_description = "Left Click"
        elif self.right_clicked:
            self.gesture_description = "Right Click"
        elif self.double_clicked:
            self.gesture_description = "Double Click"
        elif self.all_fingers_up and self.thumb_finger_down:
            self.gesture_description = "Cursor Frozen"
        elif self.all_fingers_down:
            self.gesture_description = "Ready to Drag"
        elif self.index_finger_up and self.middle_finger_up and self.ring_finger_down and self.little_finger_down:
            self.gesture_description = "Ready to Zoom In"
        elif self.index_finger_up and self.little_finger_up and self.middle_finger_down and self.ring_finger_down:
            self.gesture_description = "Ready to Zoom Out"
        else:
            self.gesture_description = "Tracking"

