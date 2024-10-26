import os
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from plyer import notification  # For notifications
import pygame  # For playing sound
import time
import requests

# Set up logging for WebDriver manager
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/webdriver_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set up logging for IPO notifications
ipo_logger = logging.getLogger('ipo_logger')
ipo_logger.setLevel(logging.INFO)
ipo_handler = logging.FileHandler('logs/ipo_notify.log')
ipo_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
ipo_logger.addHandler(ipo_handler)

# Initialize pygame mixer
pygame.mixer.init()

# Set up headless Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to check if the URL is accessible
def is_url_accessible(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            ipo_logger.error(f"URL returned status code {response.status_code}")
            return False
    except requests.RequestException as e:
        ipo_logger.error(f"Error accessing URL: {e}")
        return False

# Function to load the previous state from a JSON file
def load_previous_state():
    filename = 'logs/ipo_state.json'
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {"stable_ipos": [], "unstable_ipos": []}

# Function to save the current state to a JSON file
def save_current_state(state):
    filename = 'logs/ipo_state.json'
    with open(filename, 'w') as file:
        json.dump(state, file)

# Function to log notifications sent
def log_notification(ipo_name, notification_type):
    log_entry = {
        'ipo_name': ipo_name,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'type': notification_type
    }
    if os.path.exists('logs/notification_log.json'):
        with open('logs/notification_log.json', 'r+') as file:
            data = json.load(file)
            data.append(log_entry)
            file.seek(0)
            json.dump(data, file, indent=4)
    else:
        with open('logs/notification_log.json', 'w') as file:
            json.dump([log_entry], file, indent=4)

# Function to check for IPO options
def check_ipo_options():
    driver.get("https://linkintime.co.in/initial_offer/")
    time.sleep(15)  # Wait for 15 seconds to ensure the page fully loads

    try:
        # Locate the dropdown menu for companies
        company_dropdown = driver.find_element("id", "ddlCompany")
        options = company_dropdown.find_elements("tag name", "option")

        current_ipo_names = [option.text for option in options[1:]]  # Get the names of the IPOs

        # Log the current IPOs
        ipo_logger.info(f"Current IPOs: {', '.join(current_ipo_names)}")

        return current_ipo_names

    except Exception as e:
        ipo_logger.error(f"Error checking IPO options: {e}")
        ipo_logger.error("The website may be broken")
        print("Error checking IPO options:", e)
        print("The website may be broken")
        return []

# Main loop
try:
    url = "https://linkintime.co.in/initial_offer/"
    if is_url_accessible(url):
        initial_message = "Script started. Waiting 15 seconds before checking for IPOs..."
        notification.notify(
            title="IPO Notification",
            message=initial_message,
            timeout=10
        )
        log_notification('Script Start', 'initial')
        pygame.mixer.music.load('sound/beep.mp3')  # Load the beep sound
        pygame.mixer.music.play()  # Play the beep sound
        time.sleep(15)  # Initial wait for 15 seconds

        state = load_previous_state()
        stable_ipos = set(state["stable_ipos"])
        unstable_ipos = set(state["unstable_ipos"])
        ipo_stability_counter = {ipo: 0 for ipo in unstable_ipos}
        stable_state_threshold = 5  # Number of consecutive checks for stable state

        # Notify for existing stable IPOs when the script starts
        if stable_ipos:
            existing_message = f"Active Stable IPO(s) found:\n{', '.join(stable_ipos)}. Checking for more..."
            notification.notify(
                title="IPO Notification",
                message=existing_message,
                timeout=15
            )
            ipo_logger.info(existing_message)
            log_notification('Active Stable IPOs', 'existing')
            pygame.mixer.music.load('sound/beep.mp3')  # Load the beep sound
            pygame.mixer.music.play()  # Play the beep sound for active IPOs

        while True:
            current_ipo_names = check_ipo_options()

            # Update stability counters and classify IPOs
            new_stable_ipos = set()
            new_unstable_ipos = set()
            for ipo in current_ipo_names:
                if ipo in ipo_stability_counter:
                    ipo_stability_counter[ipo] += 1
                else:
                    ipo_stability_counter[ipo] = 1

                if ipo_stability_counter[ipo] >= stable_state_threshold:
                    if ipo not in stable_ipos:
                        new_stable_ipos.add(ipo)
                    stable_ipos.add(ipo)
                else:
                    new_unstable_ipos.add(ipo)

            # Update the state
            unstable_ipos = {ipo for ipo in new_unstable_ipos if ipo not in stable_ipos}
            state = {"stable_ipos": list(stable_ipos), "unstable_ipos": list(unstable_ipos)}
            save_current_state(state)

            # Log the stable state counter
            ipo_logger.info(f"Stable IPOs: {', '.join(stable_ipos)}")
            ipo_logger.info(f"Unstable IPOs: {', '.join(unstable_ipos)}")
            print(f"Stable IPOs: {', '.join(stable_ipos)}")
            print(f"Unstable IPOs: {', '.join(unstable_ipos)}")

            if new_stable_ipos:  # Only notify if there are new stable IPOs
                notification_message = f"New Stable IPO(s) added:\n{', '.join(new_stable_ipos)}"
                notification.notify(
                    title="IPO Notification",
                    message=notification_message,
                    timeout=10
                )
                pygame.mixer.music.load('sound/beep.mp3')  # Load the beep sound
                pygame.mixer.music.play()  # Play the beep sound
                ipo_logger.info(notification_message)
                log_notification(' | '.join(new_stable_ipos), 'new')  # Log new IPO notification

            ipo_logger.info("Next refresh in 15 seconds...")
            print("Next refresh in 15 seconds...")
            time.sleep(15)  # Refresh every 15 seconds
    else:
        ipo_logger.error("URL is not accessible. Exiting...")
        print("URL is not accessible. Exiting...")
except KeyboardInterrupt:
    ipo_logger.info("Process interrupted manually.")
    print("Process interrupted manually.")
finally:
    driver.quit()
    ipo_logger.info("Driver quit.")