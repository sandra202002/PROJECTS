import streamlit as st
import cv2
import mediapipe as mp
import pyautogui
import webbrowser
#st.title("Media player control using hand gesture")
html_temp7 = """
    <body style="background-color:white;padding:5px;">
    <h3 style="color: #FF0000 ;text-align:left;">Mediaplayer Control Using Hand Gestures </h3>
        <ul> Gestures and their Function
        <li>one: next slide  </li>
        <li>two : previous slide</li>
        <li>three :exit full screen</li>
        <li>four :full screen </li>
        <li>  No Hand : No gesture: No action  </li>
        <h4 style="font-weight:bold;"><li>Press Button q to Exit</li></h4>       
        </ul>          
    """

st.markdown(html_temp7, unsafe_allow_html=True)
html_temp5 = """
    <body style="background-color:white;padding:5px;">
    <h3 text-align:left;">Demo Video</h3>
    """

st.markdown(html_temp5, unsafe_allow_html=True)
st.video("C:/project/Project/Project/src/video/test_video.mp4")

p="C:"
r=st.button("select file")
if r:
    webbrowser.open_new(p)
    

run=st.button("click")
if run:
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    ##################################
    tipIds = [4, 8, 12, 16, 20]
    state = None
    Gesture = None
    ############################
    def fingerPosition(image, handNo=0):
        lmList = []
        if results.multi_hand_landmarks:
            myHand = results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id,lm)
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
        return lmList
    # For webcam input:
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(
        min_detection_confidence=0.8,
        min_tracking_confidence=0.5) as hands:
      while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
          # If loading a video, use 'break' instead of 'continue'.
            continue
        # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        lmList = fingerPosition(image)
        #print(lmList)
        if len(lmList) != 0:
            fingers = []
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                if (lmList[tipIds[id]][2] > lmList[tipIds[id] - 2][2] ):
                    fingers.append(0)
            totalFingers = fingers.count(1)
            print(totalFingers)
            #print(lmList[9][2])

            if totalFingers == 4:
                state = "Play"
              
            if totalFingers == 0 and state == "Play":
                state = "Pause"
                pyautogui.press('space')
                print("Space")
            if totalFingers == 1:
                if lmList[8][1]<300:
                    print("left")
                    pyautogui.press('left')
                if lmList[8][1]>400:
                    print("Right")
                    pyautogui.press('Right')
            if totalFingers == 2:
                if lmList[9][2] < 210:
                    print("Up")
                    pyautogui.press('Up')
                if lmList[9][2] > 230:
                    print("Down")
                    pyautogui.press('Down')
            if totalFingers == 3 and state == "Play":
                state = "fullscreen"
                pyautogui.press('f')
                print("fullscreen")
        
        cv2.imshow("Media Controller", image)  
        if cv2.waitKey(1) == 113:
            cv2.destroyAllWindows()
            cap.release()
            break

           


  

    
