import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Custom CSS Styling
st.markdown(
    """
    <style>
    .title {
        text-align: center;
        color: #FF5733;  /* Tomato color */
        font-size: 40px;
        font-family: 'Arial';
        margin: 20px 0;
    }
    .header {
        color: #4CAF50;  /* Green color */
    }
    .prediction {
        font-size: 24px;
        color: #FF5733;  /* Tomato color */
        font-weight: bold;
    }
    .calorie-info {
        font-size: 20px;
        color: #FF5733;  /* Same Tomato color as prediction */
        font-weight: bold;
    }
    button {
        transition: background-color 0.3s, transform 0.3s; /* Animation for buttons */
    }
    button:hover {
        background-color: #FF5733; /* Tomato color on hover */
        transform: scale(1.05); /* Slightly enlarge button on hover */
    }
    </style>
    """, unsafe_allow_html=True
)

def model_prediction(test_image):
    model = tf.keras.models.load_model("my_model.keras")
    image = Image.open(test_image)  
    image = image.resize((100, 100))  
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr]) 
    predictions = model.predict(input_arr)
    return np.argmax(predictions)

def get_calorie_details_with_selenium(fruit_name):
    options = webdriver.ChromeOptions()

    service = Service(r"C:\Users\sandr\OneDrive\Desktop\chromedriver\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    
    url = "https://www.nutritionix.com/search?q=" + fruit_name
    driver.get(url)

    try:
    
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'item-nutrition-wrap')) 
        )
        
        calorie_value = driver.find_element(By.CLASS_NAME, 'value').text
        
        return calorie_value + " Calories"
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Calorie information not found"
    finally:
        driver.quit()

# Sidebar
st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "About Project", "Prediction"])

# Main Page
if app_mode == "Home":
    st.markdown("<div class='title'>FRUITS RECOGNITION SYSTEM</div>", unsafe_allow_html=True)
    image_path = "home_img.jpg"
    st.image(image_path)

# About Project
elif app_mode == "About Project":
    st.markdown("<div class='header'>About the Project</div>", unsafe_allow_html=True)
    st.subheader("Dataset Overview")
    st.text("This project classifies images of the following 8 fruit classes:")
    st.code("Apple, Orange, Banana, Pineapple, Papaya, Strawberry, Watermelon, Blueberry")
    
    st.subheader("Dataset Details")
    st.text("The dataset used is the Fruit-360 dataset.")
    st.text("1. Training Set: 3835 images in total, with 100x100 resolution for each fruit class.")
    st.text("2. Test Set: 1277 images, balanced across all classes.")
    st.text("3. Validation Set: Separate subset used for tuning, containing balanced samples from each class.")
    st.subheader("Project Goal")
    st.text("The goal is to classify the images of fruits using a pretrained ResNet50 model.")
    st.text("The goal of a fruit classifier is to automatically identify and categorize different types of fruits based on their visual features for applications in agriculture, retail, and dietary tracking.")

# Prediction Page
elif app_mode == "Prediction":
    st.markdown("<div class='title'>Model Prediction</div>", unsafe_allow_html=True)
    
    test_image = st.file_uploader("Choose an Image:", type=["jpg", "jpeg", "png"])
    
    # Display the image when uploaded
    if test_image is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Show Image"):
                st.image(test_image, width=400, use_column_width=True)

        with col2:
            
            prediction_placeholder = st.empty()
           
            if st.button("Predict"):
            
                prediction_placeholder.markdown("<div style='background-color:#FF5733; padding:10px; color:white;'>Predicting...</div>", unsafe_allow_html=True)

                result_index = model_prediction(test_image)

                # Reading Labels
                with open("labels.txt") as f:
                    label = [line.strip() for line in f if line.strip()]  # Read and strip empty lines

                if result_index < len(label):
                    predicted_fruit = label[result_index]
                    
                    # Clear the placeholder or update it with the predicted fruit name
                    prediction_placeholder.empty()  # Clear the "Predicting..." message
                    st.markdown(f"<div class='prediction'>Model is predicting it as {predicted_fruit}</div>", unsafe_allow_html=True)

                    # Get and display calorie information
                    calorie_info = get_calorie_details_with_selenium(predicted_fruit)
                    st.markdown(f"<div class='calorie-info'>Calorie Information: {calorie_info}</div>", unsafe_allow_html=True)
                else:
                    prediction_placeholder.error("Prediction index out of bounds.")
