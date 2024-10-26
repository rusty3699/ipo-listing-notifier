# from flask import Flask, jsonify, render_template
# import threading
# import json
# import os

# app = Flask(__name__)

# # In-memory state variables
# stable_ipos = set()
# unstable_ipos = set()

# # Function to load the current state from a JSON file
# def load_current_state():
#     filename = 'logs/ipo_state.json'
#     if os.path.exists(filename):
#         with open(filename, 'r') as file:
#             state = json.load(file)
#             global stable_ipos, unstable_ipos
#             stable_ipos = set(state["stable_ipos"])
#             unstable_ipos = set(state["unstable_ipos"])
#             return state
#     return {"stable_ipos": [], "unstable_ipos": []}

# @app.route('/')
# def index():
#     return render_template('index.html', stable_ipos=stable_ipos, unstable_ipos=unstable_ipos)

# @app.route('/api/ipos')
# def get_ipos():
#     return jsonify({"stable_ipos": list(stable_ipos), "unstable_ipos": list(unstable_ipos)})

# # Function to run the Flask web server
# def run_flask():
#     app.run(host='0.0.0.0', port=5000)

# # Function to run the IPO notification script
# def run_ipo_notify():
#     import time
#     import requests
#     from selenium import webdriver
#     from selenium.webdriver.chrome.service import Service
#     from webdriver_manager.chrome import ChromeDriverManager
#     from selenium.webdriver.chrome.options import Options
#     import logging
#     from datetime import datetime

#     global stable_ipos, unstable_ipos

#     # Set up logging for WebDriver manager
#     if not os.path.exists('logs'):
#         os.makedirs('logs')

#     logging.basicConfig(
#         filename='logs/webdriver_manager.log',
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s'
#     )

#     # Set up logging for IPO notifications
#     ipo_logger = logging.getLogger('ipo_logger')
#     ipo_logger.setLevel(logging.INFO)
#     ipo_handler = logging.FileHandler('logs/ipo_notify.log')
#     ipo_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#     ipo_logger.addHandler(ipo_handler)

#     # Set up headless Chrome options
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("start-maximized")
#     options.add_argument("disable-infobars")
#     options.add_argument("--disable-extensions")

#     # Initialize WebDriver
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#     # Function to check if the URL is accessible
#     def is_url_accessible(url):
#         try:
#             response = requests.get(url)
#             if response.status_code == 200:
#                 return True
#             else:
#                 ipo_logger.error(f"URL returned status code {response.status_code}")
#                 return False
#         except requests.RequestException as e:
#             ipo_logger.error(f"Error accessing URL: {e}")
#             return False

#     # Function to load the previous state from a JSON file
#     def load_previous_state():
#         filename = 'logs/ipo_state.json'
#         if os.path.exists(filename):
#             with open(filename, 'r') as file:
#                 state = json.load(file)
#                 global stable_ipos, unstable_ipos
#                 stable_ipos = set(state["stable_ipos"])
#                 unstable_ipos = set(state["unstable_ipos"])
#                 return state
#         return {"stable_ipos": [], "unstable_ipos": []}

#     # Function to save the current state to a JSON file
#     def save_current_state():
#         state = {"stable_ipos": list(stable_ipos), "unstable_ipos": list(unstable_ipos)}
#         filename = 'logs/ipo_state.json'
#         with open(filename, 'w') as file:
#             json.dump(state, file)

#     # Function to log notifications sent
#     def log_notification(ipo_name, notification_type):
#         log_entry = {
#             'ipo_name': ipo_name,
#             'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             'type': notification_type
#         }
#         if os.path.exists('logs/notification_log.json'):
#             with open('logs/notification_log.json', 'r+') as file:
#                 data = json.load(file)
#                 data.append(log_entry)
#                 file.seek(0)
#                 json.dump(data, file, indent=4)
#         else:
#             with open('logs/notification_log.json', 'w') as file:
#                 json.dump([log_entry], file, indent=4)

#     # Function to check for IPO options
#     def check_ipo_options():
#         driver.get("https://linkintime.co.in/initial_offer/")
#         time.sleep(15)  # Wait for 15 seconds to ensure the page fully loads

#         try:
#             # Locate the dropdown menu for companies
#             company_dropdown = driver.find_element("id", "ddlCompany")
#             options = company_dropdown.find_elements("tag name", "option")

#             current_ipo_names = [option.text for option in options[1:]]  # Get the names of the IPOs

#             # Log the current IPOs
#             ipo_logger.info(f"Current IPOs: {', '.join(current_ipo_names)}")

#             return current_ipo_names

#         except Exception as e:
#             ipo_logger.error(f"Error checking IPO options: {e}")
#             ipo_logger.error("The website may be broken")
#             print("Error checking IPO options:", e)
#             print("The website may be broken")
#             return []

#     # Main loop
#     try:
#         url = "https://linkintime.co.in/initial_offer/"
#         if is_url_accessible(url):
#             initial_message = "Script started. Waiting 15 seconds before checking for IPOs..."
#             log_notification('Script Start', 'initial')
#             time.sleep(15)  # Initial wait for 15 seconds

#             load_previous_state()
#             ipo_stability_counter = {ipo: 0 for ipo in unstable_ipos}
#             stable_state_threshold = 5  # Number of consecutive checks for stable state

#             # Notify for existing stable IPOs when the script starts
#             if stable_ipos:
#                 existing_message = f"Active Stable IPO(s) found:\n{', '.join(stable_ipos)}. Checking for more..."
#                 ipo_logger.info(existing_message)
#                 log_notification('Active Stable IPOs', 'existing')

#             while True:
#                 current_ipo_names = check_ipo_options()

#                 # Update stability counters and classify IPOs
#                 new_stable_ipos = set()
#                 new_unstable_ipos = set()
#                 for ipo in current_ipo_names:
#                     if ipo in ipo_stability_counter:
#                         ipo_stability_counter[ipo] += 1
#                     else:
#                         ipo_stability_counter[ipo] = 1

#                     if ipo_stability_counter[ipo] >= stable_state_threshold:
#                         if ipo not in stable_ipos:
#                             new_stable_ipos.add(ipo)
#                         stable_ipos.add(ipo)
#                     else:
#                         new_unstable_ipos.add(ipo)

#                 # Update the state
#                 unstable_ipos = {ipo for ipo in new_unstable_ipos if ipo not in stable_ipos}
#                 save_current_state()

#                 # Log the stable state counter
#                 ipo_logger.info(f"Stable IPOs: {', '.join(stable_ipos)}")
#                 ipo_logger.info(f"Unstable IPOs: {', '.join(unstable_ipos)}")
#                 print(f"Stable IPOs: {', '.join(stable_ipos)}")
#                 print(f"Unstable IPOs: {', '.join(unstable_ipos)}")

#                 if new_stable_ipos:  # Only notify if there are new stable IPOs
#                     notification_message = f"New Stable IPO(s) added:\n{', '.join(new_stable_ipos)}"
#                     ipo_logger.info(notification_message)
#                     log_notification(' | '.join(new_stable_ipos), 'new')  # Log new IPO notification

#                 ipo_logger.info("Next refresh in 15 seconds...")
#                 print("Next refresh in 15 seconds...")
#                 time.sleep(15)  # Refresh every 15 seconds
#         else:
#             ipo_logger.error("URL is not accessible. Exiting...")
#             print("URL is not accessible. Exiting...")
#     except KeyboardInterrupt:
#         ipo_logger.info("Process interrupted manually.")
#         print("Process interrupted manually.")
#     finally:
#         driver.quit()
#         ipo_logger.info("Driver quit.")

# # Run the Flask web server and IPO notification script in parallel
# if __name__ == '__main__':
#     flask_thread = threading.Thread(target=run_flask)
#     ipo_notify_thread = threading.Thread(target=run_ipo_notify)

#     flask_thread.start()
#     ipo_notify_thread.start()

#     flask_thread.join()
#     ipo_notify_thread.join()