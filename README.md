# IPO Listing Monitoring Script
This project automates monitoring IPO listings on [Link Intime](https://linkintime.co.in/initial_offer/). It tracks IPO stability and notifies users when new stable IPOs are detected.

## Features

- **Automated IPO Check**: The script checks the IPO listing page every 15 seconds.
- **Stability Detection**: IPOs are tracked over multiple checks to identify stable listings, with a stability threshold set to avoid notifying about temporary IPO listings.
- **Desktop Notifications with Sound**: The script sends desktop notifications with an optional sound alert whenever a new stable IPO is detected.
- **Logging**: Detailed logs for each check, notification sent, and any errors encountered are saved to a log file for easy monitoring.

## How It Works

1. **Initial Setup**: The script loads Chrome in headless mode and navigates to the IPO listing page.
2. **Initial Notification**: If any active IPOs are found, they’re displayed in a notification.
3. **Regular Checks**: The script checks the website every 15 seconds, using a stability threshold to confirm IPOs as stable.
4. **Notification on New Stable IPO**: When an IPO meets the stability threshold, a desktop notification and sound alert are triggered.
5. **Logging**: IPO listings and notification history are saved in `ipo_notify.log` and `notification_log.json`.

## Requirements

- Python 3.8+
- Selenium
- Plyer (for desktop notifications)
- Pygame (for sound alerts)
- WebDriver Manager (for ChromeDriver)

Install dependencies with:
```bash
pip install selenium plyer pygame webdriver_manager
```

## Installation

Clone the repository:
```bash
git clone https://github.com/rusty3699/ipo-listing-notifier
cd ipo-monitoring
```

Install the required packages:
```bash
pip install -r requirements.txt
```

Place a sound file named `beep.mp3` in a `sound/` directory.

## Configuration

- **Refresh Interval**: Modify `time.sleep(15)` for frequency of checks.
- **Stability Threshold**: Adjust `stable_state_threshold` to control consecutive checks for IPO stability.
- **Logs**: Logs are saved in `logs/ipo_notify.log` and `logs/notification_log.json`.

## Usage

Run the script with:
```bash
python ipo_monitor.py
```

## Files and Directories

- `ipo_monitor.py`: Main script file.
- `logs/`: Contains log files.
- `sound/beep.mp3`: Sound file for notifications.

## Logging

Logging includes:
- **Error Logging**: Issues with URL access or page elements are logged to `webdriver_manager.log`.
- **IPO State Logging**: `ipo_notify.log` records detected IPOs and stability status.
- **Notification Logging**: `notification_log.json` records each notification sent, including the type and timestamp.

## Troubleshooting

- **Check URL Accessibility**: Ensure Link Intime is reachable.
- **ChromeDriver**: Verify ChromeDriver installation. Run `webdriver_manager.chrome` if needed.
- **Permissions**: Ensure notification permissions are granted.

## Future Improvements

- **Dynamic Stability Threshold**: Customize threshold per IPO.
- **Support for Additional Sites**: Adapt script for other IPO listing websites.
- **GUI**: Develop a GUI for IPO management.
- **Pancard Check**: Automate with a PAN card check for IPO applications.

## Issues
1. If the elements for website change, the script will not work.
2. The script is under testing. Please use it at your own risk.
3. Using a heavy library -Pygame for sound alert. Need to find a lightweight alternative. 

## Contributing

1. Fork the project.
2. Create a branch (`git checkout -b feature/AmazingFeature`).
3. Commit changes (`git commit -m 'Add AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

