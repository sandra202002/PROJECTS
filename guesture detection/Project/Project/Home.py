import streamlit as st
from PIL import Image
import base64

st.set_page_config(
    page_title="Gesture Controlling")
st.sidebar.success("select a page above")

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
#add_bg_from_local("D:/1.my project/file control/istockphoto-1301592082-170667a.jpg")

st.title("MULTI MEDIA CONTROL USING HAND GESTURES")

html_temp2 = """
    <body style="background-color:white;padding:10px;">
    <h3 style="color:#0000FF ;text-align:left;">About Web App</h3>
    The Main aim of this application is to use the most natural form i.e., Hand gestures to interact with the
computer system. These gestures are implemented in such a way that they are easy to perform, fast,
efficient and ensuring an immediate response.
The application uses your device's camera to give you touch-free and remote-free control over your media player application ,Images and Powerpoint presentation etc..
(without any special hardware).
    </body>
<div style="background-color:black;padding:10px;margin-bottom:10px;">
<h4 style="color:white;">Prepared using:</h4>
<ul style="color:#FFFF00;">
<li>Opencv </li>
<li>mediapipe </li>
<li>Streamlit </li>
<li>PyAutoGui </li>
</ul>
</div>
    """
    
st.markdown(html_temp2, unsafe_allow_html=True)

st.markdown("1. Video control \n"
            "2. PowerPoint control \n"
            "3. Image control")
image = Image.open("C:/project/Project/Project/src/images/test.png")
st.image(image, caption='21 Hand Landmarks ',width=700, use_column_width=700, clamp=False, channels='RGB', output_format='auto')

st.sidebar.title("Made By:")
html_temp3 = """
<ul style="font-weight:bold;">
<li> Meera</li>
<li> Sandra</li>
<li> Midhun</li>
<li> Alen</li>
</ul>
    """

st.sidebar.markdown(html_temp3, unsafe_allow_html=True)

html_temp4 = """
        <body style="background-color:white;padding:5px;">
    <h3 style="color:#f63366 ;text-align:center;">Control video using Hand Gestures </h3>
        <ul> Gestures and their Function
        <li>one: forward/rewind  </li>
        <li>two : Volume up/Volume down</li>
        <li>three :Full Screen</li>
        <li>Zero:Play/Pause</li>
        <li>  No Hand : No gesture: No action  </li>
        <h4 style="font-weight:bold;"><li>Press Button "q" to Exit</li></h4>
        </ul>
    """
st.markdown(html_temp4, unsafe_allow_html=True)
html_temp5 = """
        <body style="background-color:white;padding:5px;">
    <h3 style="color:#f63366 ;text-align:center;">Control PowerPoint using Hand Gestures </h3>
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
st.markdown(html_temp5, unsafe_allow_html=True)

html_temp6 = """
        <body style="background-color:white;padding:5px;">
    <h3 style="color:#f63366 ;text-align:center;">Control Image using Hand Gestures </h3>
        <ul> Gestures and their Function
        <li>one: next slide  </li>
        <li>two : previous slide</li>
        <li>three :exit full screen</li>
        <li>four :rotate </li>
        <li>five :full screen </li>
        <li>  No Hand : No gesture: No action  </li>
        <h4 style="font-weight:bold;"><li>Press Button "q" to Exit</li></h4>
        </ul>
    """
st.markdown(html_temp6, unsafe_allow_html=True)
