import streamlit as st
import tensorflow as tf
import numpy as np


from PIL import Image

def model_prediction(test_image):
    model = tf.keras.models.load_model("my_model.keras")
    image = Image.open(test_image)  # Open the uploaded file
    image = image.resize((100, 100))  # Resize to match your model's input size
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])  # Convert single image to batch
    predictions = model.predict(input_arr)
    return np.argmax(predictions)  # Return index of max element


#Sidebar
st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Page",["Home","About Project","Prediction"])
#Main Page
if(app_mode=="Home"):
    st.header("FRUITS RECOGNITION SYSTEM")
    image_path = "home_img.jpg"
    st.image(image_path)

#About Project
elif(app_mode == "About Project"):
    st.header("About the Project")
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

#Prediction Page
elif(app_mode=="Prediction"):
    st.header("Model Prediction")
    test_image = st.file_uploader("Choose an Image:")
    
    # Display the image when uploaded
    if test_image is not None:
        if st.button("Show Image"):
            st.image(test_image, width=4, use_column_width=True)

        # Predict button
        if st.button("Predict"):
            st.snow()
            st.write("Our Prediction")
            
            # Call the model_prediction function to get the result index
            result_index = model_prediction(test_image)

            # Reading Labels
            with open("labels.txt") as f:
                label = [line.strip() for line in f if line.strip()]  # Read and strip empty lines
            
            # Debugging prints
            print("Result Index:", result_index)
            print("Labels:", label)

            # Check if the result index is valid and show the prediction
            if result_index < len(label):  # Ensure index is valid
                st.success("Model is predicting it's a {}".format(label[result_index]))
            else:
                st.error("Prediction index out of bounds.")