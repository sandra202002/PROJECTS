import streamlit as st
import cv2 
import mediapipe as mp
import pyautogui
import webbrowser
import time
#st.title("Presentation control ")
html_temp6 = """
    <body style="background-color:white;padding:5px;">
    <h3 style="color:#800080 ;text-align:left;">Presentation Control Using Hand Gestures </h3>
        <ul> Gestures and their Function
        <li>one: next slide  </li>
        <li>two : previous slide</li>
        <li>three :home</li>
        <li>four :exit full screen</li>
        <li>five :full screen</li>
        <li>  No Hand : No gesture: No action  </li>
        <h4 style="font-weight:bold;"><li>Press Button "q" to Exit</li></h4>
        </ul>
    """
st.markdown(html_temp6, unsafe_allow_html=True)

p="C:/project/Project/Project/src/ppt/sample2.pptx"
r=st.button("select file")
if r:
    webbrowser.open_new(p)

run=st.button("click")
if run:
    def count_fingers(lst):
        cnt = 0

        thresh = (lst.landmark[0].y*100 - lst.landmark[9].y*100)/2

        if (lst.landmark[5].y*100 - lst.landmark[8].y*100) > thresh:
            cnt += 1

        if (lst.landmark[9].y*100 - lst.landmark[12].y*100) > thresh:
            cnt += 1

        if (lst.landmark[13].y*100 - lst.landmark[16].y*100) > thresh:
            cnt += 1

        if (lst.landmark[17].y*100 - lst.landmark[20].y*100) > thresh:
            cnt += 1

        if (lst.landmark[5].x*100 - lst.landmark[4].x*100) > 6:
            cnt += 1


        return cnt 

    cap = cv2.VideoCapture(0)

    drawing = mp.solutions.drawing_utils
    hands = mp.solutions.hands
    hand_obj = hands.Hands(max_num_hands=1)


    start_init = False 

    prev = -1

    while True:
        end_time = time.time()
        _, frm = cap.read()
        frm = cv2.flip(frm, 1)

        res = hand_obj.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

        if res.multi_hand_landmarks:

            hand_keyPoints = res.multi_hand_landmarks[0]

            cnt = count_fingers(hand_keyPoints)

            if not(prev==cnt):
                if not(start_init):
                    start_time = time.time()
                    start_init = True

                elif (end_time-start_time) > 0.2:
                    if (cnt == 1):
                        pyautogui.press("right")
                
                    elif (cnt == 2):
                        pyautogui.press("left")

                    elif (cnt == 5):
                        pyautogui.press(["fn","f5"])
                    elif (cnt == 4):
                        pyautogui.press("esc")
                    elif (cnt == 3):
                        pyautogui.press("home")
                    

                    prev = cnt
                    start_init = False  


        


            drawing.draw_landmarks(frm, hand_keyPoints, hands.HAND_CONNECTIONS)

        cv2.imshow("window", frm)
        if cv2.waitKey(1) == 113:
            cv2.destroyAllWindows()
            cap.release()
            break
