from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_calorie_details_with_selenium(fruit_name):
    options = webdriver.ChromeOptions()

    options.add_argument("--headless")
    options.add_argument("--disable-gpu")  
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage")  

   
    service = Service(r"C:\Users\sandr\OneDrive\Desktop\chromedriver\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    
    url = "https://www.nutritionix.com/search?q=" + fruit_name
    driver.get(url)

    try:
        # Wait for the search results to load and display
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'item-nutrition-wrap'))  # Wait for the nutrition item to load
        )
        
        # After the page loads, get the calorie value
        calorie_value = driver.find_element(By.CLASS_NAME, 'value').text
        
        return calorie_value + " Calories"
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Calorie information not found"
    finally:
        driver.quit()

# Test the Selenium-based function
fruit = "orange"  # Change the fruit name as needed
calories = get_calorie_details_with_selenium(fruit)
print(f"Calorie details for {fruit}: {calories}")
