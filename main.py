#!/usr/bin/env python3
"""
X Account Auto-Reply Bot - Production Version
Automatically replies to tweets mentioning @anoma
"""

import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
import hashlib
import tempfile

from selenium.webdriver.common.action_chains import ActionChains

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
# Add import for undetected-chromedriver
import undetected_chromedriver as uc
from google.generativeai import configure as gemini_config
import google.generativeai as genai
# Configuration
@dataclass
class Config:
    # X Account Credentials
    USERNAME: str = os.getenv('X_USERNAME')
    PASSWORD: str = os.getenv('X_PASSWORD')
    EMAIL_OR_PHONE: str = os.getenv('X_EMAIL_OR_PHONE')  # Add this line
    # Target Configuration
    TARGET_ACCOUNT: str = "anoma"
    SEARCH_QUERY: str = "@anoma -from:anoma"
    # Rate Limiting
    MAX_REPLIES_PER_DAY: int = 50
    MIN_DELAY_BETWEEN_REPLIES: int = 60 # seconds
    MAX_DELAY_BETWEEN_REPLIES: int = 150 # seconds
    SEARCH_REFRESH_INTERVAL: int = 100   
    # File Paths
    DATA_DIR: str = "data"
    REPLIED_TWEETS_FILE: str = f"{DATA_DIR}/replied_tweets.json"
    DAILY_STATS_FILE: str = f"{DATA_DIR}/daily_stats.json"
    LOG_FILE: str = f"{DATA_DIR}/bot.log"
    # Browser Settings
    HEADLESS: bool = False  # Set to False for debugging
    USER_AGENTS: List[str] = None  # Will be populated in __post_init__
    # Gemini API Key
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY')
    # Max cycles per run (None for infinite)
    MAX_CYCLES_PER_RUN: Optional[int] = int(os.getenv('MAX_CYCLES_PER_RUN', '10'))
    def __post_init__(self):
        """Initialize user agents list"""
        if self.USER_AGENTS is None:
            self.USER_AGENTS = [
                # Chrome Windows
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                # Chrome macOS
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                # Chrome Linux
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                # Firefox Windows
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
                # Firefox macOS
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0",                
                # Edge Windows
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
                # Safari macOS
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0.1 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Safari/605.1.15",
                # Mobile Chrome (Android)
                "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
                # Mobile Safari (iOS)
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",

            ]
def remove_non_bmp(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)
def human_type(element, text, min_delay=0.05, max_delay=0.18):
    """Type text into a Selenium element like a human, with random delays."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))
def human_move_and_click(driver, element):
    """Move mouse to element and click, with a small random delay."""
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.pause(random.uniform(0.1, 0.4))
    actions.click(element)
    actions.perform()
    time.sleep(random.uniform(0.1, 0.3))
def human_scroll(driver, min_scroll=100, max_scroll=600):
    """Randomly scroll the page up or down by a random amount."""
    scroll_amount = random.randint(min_scroll, max_scroll)
    direction = random.choice([-1, 1])
    driver.execute_script(f"window.scrollBy(0, {direction * scroll_amount});")
    time.sleep(random.uniform(0.2, 0.6))
class XAutoReplyBot:
    def __init__(self, config: Config):
        self.config = config
        self.config.__post_init__()  # Initialize user agents
        self.driver = None
        self.wait = None
        self.replied_tweets: Set[str] = set()
        self.daily_stats: Dict = {}
        self.current_user_agent = None
        # Create data directory BEFORE setting up logging
        os.makedirs(config.DATA_DIR, exist_ok=True)
        # Now setup logging
        self.logger = self._setup_logging()
        # Load existing data
        self._load_replied_tweets()
        self._load_daily_stats()
        # Reply templates
        self.reply_templates = [
            "Absolutely loving what Anoma is building! 💖✨",
            "This is so inspiring! Go Anoma! 🌸🙌",
            "Wow, Anoma just keeps getting better. So proud to be part of this! 😊🌷",
            "Anoma is absolutely crushing it! 🔥💪",
            "This is exactly what we need! Anoma for the win! 🏆✨",
            "Obsessed with everything Anoma is doing! 😍🚀",
            "Anoma is the future and I'm here for it! 🌟💫",
            "This community is everything! Go Anoma! 💖🙏",
            "Anoma is building something truly special! ✨💎",
            "So excited to be part of the Anoma journey! 🎉🌈",
            "Anoma is making waves and I love it! 🌊💙",
            "This is the energy we need! Anoma is unstoppable! ⚡🔥",
            "Anoma is creating magic! ✨🎭",
            "Incredible work from the Anoma team! 👏💫",
            "Anoma is the real deal! 💯🔥",
            "This is what innovation looks like! Anoma is leading! 🚀💡",
            "Anoma is building the future! 🌍✨",
            "So much love for the Anoma community! 💕🤗",
            "Anoma is absolutely killing it! 💀🔥",
            "This is revolutionary! Anoma is changing everything! 🌟💥",
            "Anoma is the definition of excellence! 👑💎",
            "This is pure genius! Anoma is unstoppable! 🧠⚡",
            "Anoma is creating something legendary! 🏛️✨",
            "This is the kind of innovation that changes the world! 🌍💫",
            "Anoma is building dreams into reality! 💭✨",
            "This is what success looks like! Anoma is winning! 🏆🔥",
            "Anoma is the blueprint for greatness! 📋💎",
            "This is absolutely phenomenal! Anoma is incredible! 🌟🙌",
            "Anoma is making history! 📚✨",
        ]
        # Gemini setup
        self.gemini_model = None
        if self.config.GEMINI_API_KEY:
            gemini_config(api_key=self.config.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.logger.info("Gemini model initialized successfully with gemini-1.5-flash")
        else:
            self.logger.warning('GEMINI_API_KEY not set. Gemini tweet generation will not work.')
    
    def _setup_logging(self) -> logging.Logger:
        """Setup production logging"""
        logger = logging.getLogger('XAutoReplyBot')
        logger.setLevel(logging.INFO)
        # File handler
        file_handler = logging.FileHandler(self.config.LOG_FILE)
        file_handler.setLevel(logging.INFO)
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger
    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the list"""
        return random.choice(self.config.USER_AGENTS)
    def _setup_driver(self) -> 'uc.Chrome':
        """Setup Chrome driver with stealth/undetected settings"""
        options = uc.ChromeOptions()
        # Select random user agent
        self.current_user_agent = self._get_random_user_agent()
        self.logger.info(f"Using User-Agent: {self.current_user_agent}")
        options.add_argument(f'--user-agent={self.current_user_agent}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript-harmony-shipping')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "geolocation": 2,
            }
        }
        options.add_experimental_option("prefs", prefs)
        # Randomize window size and position
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        options.add_argument(f'--window-size={width},{height}')
        options.add_argument(f'--window-position={x},{y}')
        # Use undetected-chromedriver
        try:
            driver = uc.Chrome(options=options, use_subprocess=True)
        except Exception as e:
            self.logger.error(f"Failed to initialize undetected Chrome driver: {e}")
            raise
        driver.set_window_size(width, height)
        driver.set_window_position(x, y)
        self.wait = WebDriverWait(driver, 20)
        # Stealth: set navigator.webdriver to undefined
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            },
        )
        return driver
    def _load_replied_tweets(self):
        """Load previously replied tweets"""
        try:
            if os.path.exists(self.config.REPLIED_TWEETS_FILE):
                with open(self.config.REPLIED_TWEETS_FILE, 'r') as f:
                    data = json.load(f)
                    self.replied_tweets = set(data.get('replied_tweets', []))
                    self.logger.info(f"Loaded {len(self.replied_tweets)} replied tweets")
        except Exception as e:
            self.logger.error(f"Error loading replied tweets: {e}")
            self.replied_tweets = set()
    def _save_replied_tweets(self):
        """Save replied tweets to file"""
        try:
            data = {
                'replied_tweets': list(self.replied_tweets),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config.REPLIED_TWEETS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving replied tweets: {e}")
    def _load_daily_stats(self):
        """Load daily statistics"""
        try:
            if os.path.exists(self.config.DAILY_STATS_FILE):
                with open(self.config.DAILY_STATS_FILE, 'r') as f:
                    self.daily_stats = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading daily stats: {e}")
            self.daily_stats = {}
    def _save_daily_stats(self):
        """Save daily statistics"""
        try:
            # Include user agent info in stats
            today_stats = self._get_today_stats()
            today_stats['user_agent'] = self.current_user_agent
            
            with open(self.config.DAILY_STATS_FILE, 'w') as f:
                json.dump(self.daily_stats, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving daily stats: {e}")
    def _get_today_key(self) -> str:
        """Get today's date key for stats"""
        return datetime.now().strftime('%Y-%m-%d')
    def _get_today_stats(self) -> Dict:
        """Get today's statistics"""
        today = self._get_today_key()
        if today not in self.daily_stats:
            self.daily_stats[today] = {
                'replies_sent': 0,
                'tweets_processed': 0,
                'errors': 0,
                'posts_made': 0,
                'started_at': datetime.now().isoformat()
            }
        else:
            # Ensure posts_made is present for backward compatibility
            if 'posts_made' not in self.daily_stats[today]:
                self.daily_stats[today]['posts_made'] = 0
        return self.daily_stats[today]
    def _can_reply_today(self) -> bool:
        """Check if we can still reply today"""
        today_stats = self._get_today_stats()
        return today_stats['replies_sent'] < self.config.MAX_REPLIES_PER_DAY
    def _generate_tweet_id(self, tweet_element) -> str:
        """Generate unique ID for a tweet"""
        try:
            # Try to get the actual tweet URL/ID
            tweet_link = tweet_element.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
            tweet_url = tweet_link.get_attribute('href')
            return tweet_url.split('/status/')[-1].split('?')[0]
        except:
            # Fallback: generate hash from tweet content
            try:
                tweet_text = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]').text
                return hashlib.md5(tweet_text.encode()).hexdigest()[:16]
            except:
                return str(int(time.time() * 1000))
    def login(self) -> bool:
        """Login to X account"""
        try:
            self.logger.info("Attempting to login to X")
            self.driver.get("https://x.com/i/flow/login")
            # Wait longer and add more debugging
            self.logger.info("Waiting for username field...")
            username_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            # Human-like scroll and mouse movement
            human_scroll(self.driver)
            human_move_and_click(self.driver, username_field)
            self.logger.info(f"Found username field, entering: {self.config.USERNAME}")
            username_field.clear()
            time.sleep(random.uniform(0.3, 1.2))  # Human-like pause before typing
            human_type(username_field, self.config.USERNAME)
            time.sleep(random.uniform(0.5, 1.5))  # Human-like pause after typing
            username_field.send_keys(Keys.ENTER)
            # Wait for either password or email/phone confirmation field
            self.logger.info("Waiting for password or email/phone confirmation field...")
            field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"], input[name="text"]'))
            )
            field_type = field.get_attribute("type")
            field_name = field.get_attribute("name")
            if field_type == "password":
                password_field = field
            elif field_name == "text":
                # This is likely the email/phone confirmation field
                self.logger.info("Email/phone confirmation required. Entering email/phone...")
                field.clear()
                if not self.config.EMAIL_OR_PHONE:
                    self.logger.error("EMAIL_OR_PHONE is not set in environment variables or config.")
                    return False
                human_type(field, self.config.EMAIL_OR_PHONE)
                time.sleep(random.uniform(0.5, 1.5))
                field.send_keys(Keys.ENTER)
                # Now wait for password field
                password_field = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
                )
            else:
                self.logger.error("Unexpected field after username.")
                return False
            # Human-like scroll and mouse movement
            human_scroll(self.driver)
            human_move_and_click(self.driver, password_field)
            self.logger.info("Found password field, entering password...")
            password_field.clear()
            time.sleep(random.uniform(0.3, 1.2))
            human_type(password_field, self.config.PASSWORD)
            time.sleep(random.uniform(0.5, 1.5))
            password_field.send_keys(Keys.ENTER)
            # Wait for home page to load with longer timeout
            self.logger.info("Waiting for home page to load...")
            try:
                # Try multiple selectors for home page
                home_element = WebDriverWait(self.driver, 60).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="AppTabBar_Home_Link"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="primaryColumn"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Home timeline"]'))
                    )
                )
                self.logger.info("Successfully logged in to X")
                return True
            except TimeoutException:
                # Check if we're on a challenge page or need 2FA
                current_url = self.driver.current_url
                page_source = self.driver.page_source
                if "challenge" in current_url.lower() or "challenge" in page_source.lower():
                    self.logger.error("Login challenge detected - may need manual intervention")
                elif "verification" in current_url.lower() or "verification" in page_source.lower():
                    self.logger.error("2FA verification required - bot cannot proceed automatically")
                else:
                    self.logger.error(f"Unknown login issue. Current URL: {current_url}")

                return False
        except TimeoutException as e:
            self.logger.error(f"Login timeout - check credentials or captcha: {e}")
            self.logger.error(f"Current URL: {self.driver.current_url}")
            return False
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            self.logger.error(f"Current URL: {self.driver.current_url}")
            return False
    def search_mentions(self) -> List:
        """Search for tweets mentioning target account (Top tweets), with scrolling to load more."""
        try:
            self.logger.info(f"Searching for mentions: {self.config.SEARCH_QUERY}")
            # Navigate to search (Top tweets by default, no &f=live)
            search_url = f"https://x.com/search?q={self.config.SEARCH_QUERY}&src=typed_query"
            self.driver.get(search_url)
            # Wait for initial tweets to load
            time.sleep(4)
            # Scroll down several times to load more tweets
            num_scrolls = 4
            for i in range(num_scrolls):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2.5)
            # Find tweet elements
            tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            self.logger.info(f"Found {len(tweet_elements)} tweets")
            return tweet_elements
        except Exception as e:
            self.logger.error(f"Error searching mentions: {e}")
            return []
    
    def reply_to_tweet(self, tweet_element) -> bool:
        """Reply to a specific tweet"""
        try:
            # Generate tweet ID
            tweet_id = self._generate_tweet_id(tweet_element)
            # Check if already replied
            if tweet_id in self.replied_tweets:
                return False
            # Human-like scroll before interacting
            human_scroll(self.driver)
            # Find and click reply button
            try:
                reply_button = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="reply"]')
                human_move_and_click(self.driver, reply_button)
            except StaleElementReferenceException:
                self.logger.error(f"Tweet element became stale while trying to reply to {tweet_id}")
                return False
            # Wait for reply dialog
            reply_textbox = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
            )
            # Human-like scroll and mouse movement
            human_scroll(self.driver)
            human_move_and_click(self.driver, reply_textbox)
            # Select random reply template
            reply_text = random.choice(self.reply_templates)
            reply_text = remove_non_bmp(reply_text)  # Filter out non-BMP characters
            # Human-like pause before typing
            time.sleep(random.uniform(0.5, 2.0))
            human_type(reply_textbox, reply_text)
            time.sleep(random.uniform(0.3, 1.0))  # Human-like pause after typing
            # Find and click reply button
            send_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
            )
            human_move_and_click(self.driver, send_button)
            # Wait for reply to be sent
            time.sleep(3)
            # Mark as replied
            self.replied_tweets.add(tweet_id)
            # Update stats
            today_stats = self._get_today_stats()
            today_stats['replies_sent'] += 1
            self.logger.info(f"Successfully replied to tweet {tweet_id}: {reply_text}")
            return True
        except StaleElementReferenceException as e:
            self.logger.error(f"Stale element reference while replying to tweet: {e}")
            today_stats = self._get_today_stats()
            today_stats['errors'] += 1
            return False
        except Exception as e:
            self.logger.error(f"Error replying to tweet: {e}")
            today_stats = self._get_today_stats()
            today_stats['errors'] += 1
            return False
    def _is_original_tweet(self, tweet_element) -> bool:
        """Check if the tweet is an original tweet (not a reply/comment)."""
        try:
            # If it contains a 'replying to' label, it's a reply
            replying_to = tweet_element.find_elements(By.XPATH, ".//*[contains(text(), 'Replying to') or contains(text(), 'replying to')]")
            if replying_to:
                return False
            # Some tweets may have an aria-label or role for replies
            aria_label = tweet_element.get_attribute('aria-label')
            if aria_label and 'replying to' in aria_label.lower():
                return False
            return True
        except Exception:
            return True  # If in doubt, treat as original
    def _get_like_count(self, tweet_element) -> int:
        """Extract the like count from a tweet element."""
        try:
            # Find the like button and extract the count
            like_btn = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="like"]')
            # The like count is usually in a span inside the button
            count_spans = like_btn.find_elements(By.XPATH, './/span')
            for span in count_spans:
                text = span.text.strip().replace(',', '')
                if text.isdigit():
                    return int(text)
            return 0
        except Exception:
            return 0
    def _find_tweet_by_id(self, tweet_id):
        """Re-locate a tweet element by its ID on the current page."""
        try:
            tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            for tweet in tweet_elements:
                try:
                    found_id = self._generate_tweet_id(tweet)
                    if found_id == tweet_id:
                        return tweet
                except Exception:
                    continue
            return None
        except Exception:
            return None
    def run_batched_reply_cycle(self, max_replies=20, batch_size=5, batch_wait=60, post_cycle_wait=300):
        """Reply to up to max_replies tweets in batches, waiting batch_wait seconds between batches. Wait post_cycle_wait after all replies."""
        if not self._can_reply_today():
            self.logger.info("Daily reply limit reached")
            return 0
        replies_sent = 0
        while self._can_reply_today() and replies_sent < max_replies:
            tweets = self.search_mentions()
            if not tweets:
                self.logger.info("No tweets found")
                break
            # Filter tweets: only originals, not already replied
            filtered_tweets = []
            for tweet in tweets:
                try:
                    tweet_id = self._generate_tweet_id(tweet)
                    if tweet_id in self.replied_tweets:
                        continue
                    if not self._is_original_tweet(tweet):
                        continue
                    filtered_tweets.append((tweet, tweet_id))
                except Exception:
                    continue
            if not filtered_tweets:
                self.logger.info("No new tweets to reply to (originals, not already replied)")
                break
            batch = filtered_tweets[:batch_size]
            self.logger.info(f"Replying to batch of {len(batch)} tweets...")
            for tweet, tweet_id in batch:
                try:
                    today_stats = self._get_today_stats()
                    today_stats['tweets_processed'] += 1
                    if self.reply_to_tweet(tweet):
                        replies_sent += 1
                        if replies_sent >= max_replies:
                            break
                    else:
                        continue
                except Exception as e:
                    self.logger.error(f"Error processing tweet: {e}")
                    continue
            if replies_sent >= max_replies:
                break
            # Wait between batches if more to do
            if self._can_reply_today() and replies_sent < max_replies:
                self.logger.info(f"Batch complete. Waiting {batch_wait} seconds before next batch...")
                time.sleep(batch_wait)
        # Save data
        self._save_replied_tweets()
        self._save_daily_stats()
        self.logger.info(f"Batched reply cycle complete: {replies_sent} replies sent. Waiting {post_cycle_wait} seconds before next hype tweet cycle...")
        time.sleep(post_cycle_wait)
        return replies_sent

    def post_hype_tweet(self):
        """Post a single hype tweet, tagging @anoma, but not at the start (so it shows in Posts tab)."""
        if not self.gemini_model:
            self.logger.warning("GEMINI_API_KEY not set. Cannot post hype tweet.")
            return False # Indicate failure
        try:
            self.logger.info("Generating hype tweet...")
            prompt = f"Generate a short, engaging tweet about Anoma, mentioning @anoma somewhere (but NOT at the start). Keep it under 140 characters. Make it sound positive and excited. Do NOT start the tweet with @anoma."
            response = self.gemini_model.generate_content(prompt)
            tweet_text = response.text.strip()
            # Ensure @anoma is present but not at the start
            if not tweet_text.lower().startswith(f"@{self.config.TARGET_ACCOUNT.lower()}"):
                if f"@{self.config.TARGET_ACCOUNT.lower()}" not in tweet_text.lower():
                    # Add @anoma at the end if not present
                    tweet_text = f"{tweet_text} @{self.config.TARGET_ACCOUNT}".strip()
            else:
                # Move @anoma to the end if it starts the tweet
                tweet_text = tweet_text[len(f"@{self.config.TARGET_ACCOUNT}"):].strip()
                tweet_text = f"{tweet_text} @{self.config.TARGET_ACCOUNT}".strip()
            tweet_text = remove_non_bmp(tweet_text)
            self.logger.info(f"Generated hype tweet: {tweet_text}")
            # Navigate to compose tweet page
            self.driver.get("https://x.com/compose/tweet")
            time.sleep(2) # Wait for page to load
            # Find and click the tweet text area
            tweet_textarea = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
            )
            human_move_and_click(self.driver, tweet_textarea)
            # Human-like scroll and type
            human_scroll(self.driver)
            human_type(tweet_textarea, tweet_text)
            time.sleep(random.uniform(0.5, 1.5)) # Human-like pause after typing
            # Find and click the tweet button
            send_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
            )
            human_move_and_click(self.driver, send_button)
            # Wait for tweet to be posted
            time.sleep(5) # Give it a moment to load
            # Mark as replied (using a placeholder ID, as it's not a direct reply to a tweet)
            tweet_id_placeholder = "hype_tweet_" + str(int(time.time() * 1000))
            self.replied_tweets.add(tweet_id_placeholder)
            # Update stats for posts made
            today_stats = self._get_today_stats()
            today_stats['posts_made'] += 1
            self._save_replied_tweets()
            self._save_daily_stats()
            self.logger.info(f"Successfully posted hype tweet: {tweet_text}")
            return True # Indicate success
        except TimeoutException as e:
            self.logger.error(f"Timeout posting hype tweet: {e}")
            self.logger.error(f"Current URL: {self.driver.current_url}")
            return False # Indicate failure
        except Exception as e:
            self.logger.error(f"Error posting hype tweet: {e}")
            self.logger.error(f"Current URL: {self.driver.current_url}")
            return False # Indicate failure
    def post_hype_tweet_cycle(self):
        """Post 3 hype tweets, each tagging @anoma, with short random delays between, then wait ~5 minutes (with jitter)."""
        for i in range(3):
            self.logger.info(f"Posting hype tweet {i+1}/3...")
            success = self.post_hype_tweet()
            # If posting fails, wait a bit longer before retrying
            if not success:
                delay = random.randint(60, 120)
                self.logger.warning(f"Failed to post hype tweet. Waiting {delay} seconds before next attempt...")
                time.sleep(delay)
            elif i < 2:
                delay = random.randint(40, 120)
                self.logger.info(f"Waiting {delay} seconds before next hype tweet...")
                time.sleep(delay)
        # Add jitter to the 5-minute wait
        jitter = random.randint(-30, 60)
        wait_time = 300 + jitter
        self.logger.info(f"Hype tweet cycle complete. Waiting {wait_time} seconds (~5 min + jitter) before next cycle...")
        time.sleep(wait_time)
    def start(self):
        """Start the bot"""
        try:
            self.logger.info("Starting X Auto-Reply Bot")
            self.driver = self._setup_driver()
            if not self.login():
                self.logger.error("Failed to login. Exiting.")
                return
            cycle_count = 0
            while True:
                if self.config.MAX_CYCLES_PER_RUN and cycle_count >= self.config.MAX_CYCLES_PER_RUN:
                    self.logger.info(f"Max cycles per run ({self.config.MAX_CYCLES_PER_RUN}) reached. Stopping.")
                    break
                cycle_count += 1
                self.logger.info(f"Starting cycle {cycle_count}")
                # 1. Post 3 hype tweets
                try:
                    self.post_hype_tweet_cycle()
                except Exception as e:
                    self.logger.error(f"Error in hype tweet cycle {cycle_count}: {e}")
                    time.sleep(random.randint(60, 180))
                # 2. Run batched reply cycle (20 replies, 5 per batch, 1 min between, 5 min after)
                try:
                    self.run_batched_reply_cycle(max_replies=20, batch_size=5, batch_wait=60, post_cycle_wait=300)
                except Exception as e:
                    self.logger.error(f"Error in batched reply cycle {cycle_count}: {e}")
                    time.sleep(random.randint(60, 180))
                # 3. Add a small random pause before next cycle for human-likeness
                if not (self.config.MAX_CYCLES_PER_RUN and cycle_count >= self.config.MAX_CYCLES_PER_RUN):
                    pause = random.randint(30, 90)
                    self.logger.info(f"Waiting {pause} seconds before starting next cycle...")
                    time.sleep(pause)
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                if self.driver.service.service_url.startswith('http://127.0.0.1:') or self.driver.service.service_url.startswith('http://localhost:'):
                    try:
                        import shutil
                        shutil.rmtree(self.driver.service.service_url.replace('http://127.0.0.1:', '').replace('http://localhost:', ''))
                        self.logger.info(f"Cleaned up temporary user data directory: {self.driver.service.service_url}")
                    except Exception as cleanup_e:
                        self.logger.warning(f"Error cleaning up temporary user data directory: {cleanup_e}")
            self.logger.info("Bot stopped")

def main():
    """Main entry point"""
    config = Config()
    # Validate configuration
    if not config.USERNAME or not config.PASSWORD:
        print("Error: X_USERNAME and X_PASSWORD environment variables must be set")
        print("Make sure your .env file contains:")
        print("X_USERNAME=your_username")
        print("X_PASSWORD=your_password")
        return

    print(f"Loaded USERNAME: {config.USERNAME}")    
    bot = XAutoReplyBot(config)
    bot.start()
if __name__ == "__main__":
    main()