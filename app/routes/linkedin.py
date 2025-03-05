from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

# Load environment variables for LinkedIn credentials
load_dotenv()

linkedin_router = Blueprint('linkedin', __name__)

def setup_selenium_driver():
    """Set up and return a Selenium WebDriver with Chrome options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_to_linkedin(driver):
    """Log in to LinkedIn with credentials from environment variables."""
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    
    if not email or not password:
        raise ValueError("LinkedIn credentials not found in environment variables")
    
    driver.get("https://www.linkedin.com/login")
    
    # Wait for the email field and enter email
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    email_field.send_keys(email)
    
    # Enter password
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)
    
    # Click login button
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    
    # Wait for login to complete
    WebDriverWait(driver, 10).until(
        EC.url_contains("feed")
    )

def extract_post_data(post_element):
    """Extract metadata from a LinkedIn post element."""
    try:
        # This is a simplified example - actual selectors will depend on LinkedIn's HTML structure
        timestamp_elem = post_element.find_element(By.CSS_SELECTOR, ".post-timestamp")
        timestamp = timestamp_elem.get_attribute("datetime") if timestamp_elem else None
        
        text_elem = post_element.find_element(By.CSS_SELECTOR, ".post-content")
        text = text_elem.text if text_elem else ""
        
        likes_elem = post_element.find_element(By.CSS_SELECTOR, ".social-details-social-counts__reactions-count")
        likes = likes_elem.text if likes_elem else "0"
        
        comments_elem = post_element.find_element(By.CSS_SELECTOR, ".social-details-social-counts__comments")
        comments = comments_elem.text if comments_elem else "0"
        
        return {
            "timestamp": timestamp,
            "posted_date": datetime.fromisoformat(timestamp) if timestamp else None,
            "text": text,
            "likes": likes,
            "comments": comments
        }
    except Exception as e:
        return {"error": str(e)}

@linkedin_router.route('/analyze', methods=['POST'])
def analyze_linkedin_profile():
    """Analyze LinkedIn profile posts."""
    data = request.json
    profile_url = data.get('profile_url')
    
    if not profile_url:
        return jsonify({"error": "LinkedIn profile URL is required"}), 400
    
    try:
        driver = setup_selenium_driver()
        login_to_linkedin(driver)
        
        # Navigate to the profile page
        driver.get(profile_url)
        time.sleep(3)  # Allow page to load
        
        # Navigate to posts tab (adjust selector based on LinkedIn's structure)
        posts_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'detail/recent-activity/shares')]"))
        )
        posts_tab.click()
        time.sleep(3)  # Allow posts to load
        
        # Scroll down to load more posts (adjust number based on needs)
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Find all post elements
        post_elements = driver.find_elements(By.CSS_SELECTOR, ".occludable-update")
        
        # Extract post data
        posts = []
        for post_element in post_elements:
            post_data = extract_post_data(post_element)
            if post_data and "error" not in post_data:
                posts.append(post_data)
        
        # Calculate metrics
        total_posts = len(posts)
        
        # Calculate posts in the last month
        one_month_ago = datetime.now() - timedelta(days=30)
        posts_last_month = sum(1 for post in posts if post.get("posted_date") and post["posted_date"] > one_month_ago)
        
        results = {
            "total_posts": total_posts,
            "posts_last_month": posts_last_month,
            "all_posts": posts
        }
        
        driver.quit()
        return jsonify(results)
        
    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        return jsonify({"error": f"Failed to analyze LinkedIn profile: {str(e)}"}), 500

@linkedin_router.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "LinkedIn analytics service is running"})