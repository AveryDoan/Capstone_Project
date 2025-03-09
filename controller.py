import pyautogui
import time

class Controller:
    def __init__(self):
        self.prev_hand = None
        self.right_clicked = False
        self.left_clicked = False
        self.double_clicked = False
        self.dragging = False
        self.hand_landmarks = None
        self.little_finger_down = None
        self.little_finger_up = None
        self.index_finger_down = None
        self.index_finger_up = None
        self.middle_finger_down = None
        self.middle_finger_up = None
        self.ring_finger_down = None
        self.ring_finger_up = None
        self.thumb_finger_down = None  # Fixed typo
        self.thumb_finger_up = None    # Fixed typo
        self.all_fingers_down = None
        self.all_fingers_up = None
        self.index_finger_within_thumb = None
        self.middle_finger_within_thumb = None
        self.little_finger_within_thumb = None
        self.ring_finger_within_thumb = None
        self.screen_width, self.screen_height = pyautogui.size()
        self.gesture_description = "Tracking"  # Instance attribute

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

    def get_position(self, hand_x_position, hand_y_position):
        old_x, old_y = pyautogui.position()
        current_x = int(hand_x_position * self.screen_width)
        current_y = int(hand_y_position * self.screen_height)

        ratio = 1
        self.prev_hand = (current_x, current_y) if self.prev_hand is None else self.prev_hand
        delta_x = current_x - self.prev_hand[0]
        delta_y = current_y - self.prev_hand[1]
        
        self.prev_hand = [current_x, current_y]
        current_x, current_y = old_x + delta_x * ratio, old_y + delta_y * ratio

        threshold = 5
        current_x = max(threshold, min(current_x, self.screen_width - threshold))
        current_y = max(threshold, min(current_y, self.screen_height - threshold))

        return (current_x, current_y)

    def cursor_moving(self, x=None, y=None):
        if not self.hand_landmarks:
            return
            
        if x is None or y is None:  # Use hand tracking if no coordinates provided
            point = 9  # Middle finger MCP
            current_x, current_y = self.hand_landmarks.landmark[point].x, self.hand_landmarks.landmark[point].y
            x, y = self.get_position(current_x, current_y)
        
        cursor_freezed = self.all_fingers_up and self.thumb_finger_down
        if not cursor_freezed:
            pyautogui.moveTo(x, y, duration=0)

    def detect_scrolling(self):
        """Detect and perform gradual scrolling"""
        scroll_step = 20  # Smaller steps for bit-by-bit scrolling (adjustable)
        scroll_cooldown = 0.5  # Time in seconds between scroll steps
        current_time = time.time()
        
        # Check if enough time has passed since last scroll
        if not hasattr(self, '_last_scroll_time'):
            self._last_scroll_time = 0
        
        if current_time - self._last_scroll_time < scroll_cooldown:
            return

        scrolling_up = (self.little_finger_up and self.index_finger_down and 
                      self.middle_finger_down and self.ring_finger_down)
        if scrolling_up:
            pyautogui.scroll(scroll_step)  # Smaller positive value for gradual up
            self.gesture_description = "Scrolling UP"
            self._last_scroll_time = current_time

        scrolling_down = (self.index_finger_up and self.middle_finger_down and 
                        self.ring_finger_down and self.little_finger_down)
        if scrolling_down:
            pyautogui.scroll(-scroll_step)  # Smaller negative value for gradual down
            self.gesture_description = "Scrolling DOWN"
            self._last_scroll_time = current_time

    def detect_zooming(self):  # Fixed typo in method name
        zooming = (self.index_finger_up and self.middle_finger_up and 
                  self.ring_finger_down and self.little_finger_down)
        window = 0.05
        index_touches_middle = abs(self.hand_landmarks.landmark[8].x - self.hand_landmarks.landmark[12].x) <= window
        zooming_out = zooming and index_touches_middle
        zooming_in = zooming and not index_touches_middle
        
        if zooming_out:
            pyautogui.keyDown('ctrl')
            pyautogui.scroll(-50)
            pyautogui.keyUp('ctrl')
            self.gesture_description = "Zooming Out"

        if zooming_in:
            pyautogui.keyDown('ctrl')
            pyautogui.scroll(50)
            pyautogui.keyUp('ctrl')
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
        """Update gesture description based on current state"""
        if self.dragging:
            self.gesture_description = "Dragging"
        elif self.left_clicked:
            self.gesture_description = "Left Click"
        elif self.right_clicked:
            self.gesture_description = "Right Click"
        elif self.double_clicked:
            self.gesture_description = "Double Click"
        else:
            self.gesture_description = "Tracking"
            
        