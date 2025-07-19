# XAuto: Automated X (Twitter) Support Bot

## Overview
This project automates replying to @anoma mentions on X (Twitter) using Selenium. It is modular, maintainable, and designed for safe, human-like automation.

## Features
- Secure login using environment variables
- Automated search and reply to @anoma mentions
- Reply templates and tracking to avoid duplicates
- Safety delays and daily limits
- Modular codebase for easy extension

## Setup

1. **Clone the repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download ChromeDriver**
   - Download the version matching your Chrome browser from [here](https://sites.google.com/chromium.org/driver/).
   - Place `chromedriver.exe` in your project folder or ensure it’s in your system PATH.

4. **Set up environment variables**
   - Copy `.env.example` to `.env` and fill in your X (Twitter) credentials:
     ```
     X_USERNAME=your_username_here
     X_PASSWORD=your_password_here
     ```

5. **Run the setup script**
   ```bash
   python setup_files.py
   ```
   This will create the reply templates and tracking files if they do not exist.

6. **Run the main automation**
   ```bash
   python main.py
   ```

## Project Structure
```
xauto/
├── xauto/                # Main package
│   ├── __init__.py
│   ├── config.py         # Loads env, config, etc.
│   ├── setup_files.py    # File setup logic
│   ├── browser.py        # Selenium driver setup
│   ├── login.py          # Login logic
│   ├── search.py         # Search & tweet collection
│   ├── reply.py          # Reply logic
│   ├── tracker.py        # Tracking logic
│   └── utils.py          # Helper functions
├── .env
├── requirements.txt
├── main.py               # Entry point for automation
└── README.md
```

## Notes
- Never share your `.env` file or credentials.
- Use responsibly and respect X (Twitter) terms of service. 