# Streamlit app for fruit recognition with image transformations (rotation and flip)
import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image, ImageOps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Custom CSS Styling (as it is in your original code)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');
    body {
        background-color: #f8f9fa; 
        font-family: 'Merriweather', serif; 
    }
    .title {
        text-align: center;
        color: #007BFF;
        font-size: 42px;
        margin: 20px 0;
    }
    .header {
        color: #28a745;
        font-size: 28px;
        margin-bottom: 10px;
    }
    .prediction {
        font-size: 24px;
        color: #007BFF;
        font-weight: bold;
    }
    .calorie-info {
        font-size: 20px;
        color: #007BFF;
        font-weight: bold;
    }
    .url-info {
        font-size: 16px;
        color: #17a2b8;
        text-decoration: underline;
    }
    button {
        background-color: #007BFF;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s, transform 0.3s;
    }
    button:hover {
        background-color: #0056b3;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True
)

# Function to perform model prediction (unchanged)
def model_prediction(test_image):
    model = tf.keras.models.load_model("my_model.keras")
    image = Image.open(test_image)  
    image = image.resize((100, 100))  
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr]) 
    predictions = model.predict(input_arr)
    return np.argmax(predictions)

# Function to get calorie details with Selenium (unchanged)
# Function to get calorie details with Selenium (headless mode)
def get_calorie_details_with_selenium(fruit_name):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Enable headless mode
    options.add_argument('--disable-gpu')  # Disable GPU acceleration (for headless environments)
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    
    service = Service(r"C:\Users\sandr\OneDrive\Desktop\chromedriver\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    
    url = "https://www.nutritionix.com/search?q=" + fruit_name
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'item-nutrition-wrap')) 
        )
        
        calorie_value = driver.find_element(By.CLASS_NAME, 'value').text
        return calorie_value + " Calories", url
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Calorie information not found", url
    finally:
        driver.quit()

# Sidebar navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "About Project", "Prediction"])

# Main Page logic
# Home Page
# Home Page with Enhanced Welcome Message
if app_mode == "Home":
    st.markdown("<div class='title'>FRUITS RECOGNITION SYSTEM</div>", unsafe_allow_html=True)
    image_path = "home_img.jpg"
    st.image(image_path)

    # Enhanced welcome message
    st.markdown(
        """
        <div style='background-color:#f0f8ff; border-radius: 10px; padding: 20px; margin: 20px 0;'>
            <h2 style='color:#007BFF; text-align:center; font-family:Merriweather, serif;'>Welcome to the Fruit Recognition and Calorie Counter App!</h2>
            <p style='color:#333; text-align:center; font-size:18px; font-family:Merriweather, serif;'>
                Our system combines the power of AI and nutrition tracking. Easily classify fruits with a single image upload and gain insights into their nutritional content. 
                <br><br>
                In today's health-conscious world, knowing what you eat is essential. Fruit classification helps identify different varieties instantly, while our calorie counter ensures you stay informed about the calories you consume, assisting with healthier choices and effective meal planning.
                <br><br>
                Start exploring and make smarter dietary decisions today!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# About Project (unchanged)
# About Project Page with Container and Custom Styling
elif app_mode == "About Project":
    with st.container():
        # Header with custom font and color
        st.markdown(
            """
            <div style='background-color:#e3f2fd; border-radius: 10px; padding: 20px; margin: 20px 0;'>
                <h2 style='color:#007BFF; text-align:center; font-family:Merriweather, serif;'>About the Project</h2>
            """, unsafe_allow_html=True
        )

        # Dataset Overview Section
        st.markdown(
            """
            <h3 style='color:#28a745; font-family:Merriweather, serif;'>Dataset Overview</h3>
            <p style='font-family:Merriweather, serif; font-size:16px;'>This project classifies images of the following 8 fruit classes:</p>
            """, unsafe_allow_html=True
        )
        st.code("Apple, Orange, Banana, Pineapple, Papaya, Strawberry, Watermelon, Blueberry")
        
        # Dataset Details Section
        st.markdown(
            """
            <h3 style='color:#28a745; font-family:Merriweather, serif;'>Dataset Details</h3>
            <p style='font-family:Merriweather, serif; font-size:16px;'>
                The dataset used is the Fruit-360 dataset. 
                <br>1. Training Set: 3853 images in total, with 100x100 resolution for each fruit class.
                <br>2. Test Set: 1288 images, balanced across all classes.
                <br>3. Validation Set: Separate subset used for tuning, containing balanced samples from each class.
            </p>
            """, unsafe_allow_html=True
        )

        # Project Goal Section
        st.markdown(
            """
            <h3 style='color:#28a745; font-family:Merriweather, serif;'>Project Goal</h3>
            <p style='font-family:Merriweather, serif; font-size:16px;'>
                The goal is to classify the images of fruits using a pretrained ResNet50 model.
                The aim of the fruit classifier is to automatically identify and categorize different fruits based on their visual features, which is helpful for applications in agriculture, retail, and dietary tracking.
            </p>
            """, unsafe_allow_html=True
        )

        # Calorie Information Section
        st.markdown(
            """
            <h3 style='color:#28a745; font-family:Merriweather, serif;'>Calorie Information Feature</h3>
            <p style='font-family:Merriweather, serif; font-size:16px;'>
                In addition to fruit classification, this project includes a feature that fetches calorie information for the predicted fruits.
                We utilize the Nutritionix website to obtain accurate calorie data for each fruit, which is crucial for individuals monitoring their dietary intake.
            </p>
            """, unsafe_allow_html=True
        )

        # Web Scraping with Selenium Section
        st.markdown(
            """
            <h3 style='color:#28a745; font-family:Merriweather, serif;'>Web Scraping with Selenium</h3>
            <p style='font-family:Merriweather, serif; font-size:16px;'>
                For fetching calorie details, the Selenium library is employed to automate web interactions.
                Selenium allows the application to navigate to the Nutritionix website, perform a search for the predicted fruit, and extract the calorie information efficiently.
            </p>
            </div>
            """, unsafe_allow_html=True
        )

# Prediction Page
elif app_mode == "Prediction":
    st.markdown("<div class='title'>Model Prediction</div>", unsafe_allow_html=True)

    test_image = st.file_uploader("Choose an Image:", type=["jpg", "jpeg", "png"])

    if test_image is not None:
    # Display original image
        st.image(test_image, caption="Original Image", width=250, use_column_width=False)

    # Open the image
        image = Image.open(test_image)

    # Apply a 20-degree rotation and horizontal flip
        rotated_20 = image.rotate(20)
        flipped_horizontal = ImageOps.mirror(image)  # Horizontal flip

    # Display the transformed images
        st.markdown("### Transformed Images")
    
        col1, col2 = st.columns(2)
        with col1:
            st.image(rotated_20, caption="Rotated 20°", width=150)
        with col2:
            st.image(flipped_horizontal, caption="Flipped Horizontal", width=150)
        # Button to trigger prediction
        if st.button("Predict"):
            prediction_placeholder = st.empty()
            prediction_placeholder.markdown("<div style='background-color:#007BFF; padding:10px; color:white;'>Predicting...</div>", unsafe_allow_html=True)
            
            # Perform prediction
            result_index = model_prediction(test_image)

            # Reading labels
            with open("labels.txt") as f:
                label = [line.strip() for line in f if line.strip()]

            if result_index < len(label):
                predicted_fruit = label[result_index]

                # Display prediction
                prediction_placeholder.empty()
                st.markdown(f"<div class='prediction'>Model predicts it as: {predicted_fruit}</div>", unsafe_allow_html=True)

                # Get calorie information and URL
                calorie_info, url = get_calorie_details_with_selenium(predicted_fruit)
                st.markdown(f"<div class='calorie-info'>Calorie Information: {calorie_info}</div>", unsafe_allow_html=True)
                formatted_url = f"https://www.nutritionix.com/search?q={predicted_fruit}"
                st.markdown(f"<div class='url-info'>URL: {formatted_url}</div>", unsafe_allow_html=True)  # Display the URL directly
                st.markdown(f"[Source: Nutritionix]({formatted_url})", unsafe_allow_html=True)
            else:
                prediction_placeholder.error("Prediction index out of bounds.")
