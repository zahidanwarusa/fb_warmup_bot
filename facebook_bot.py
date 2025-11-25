"""
Facebook Warmup Bot Module
Importable bot class for use with Flask web interface
SUPPORTS: Edge browser profiles
FEATURES:
- Stock image fetching from Pexels/Unsplash API
- Enhanced Post button clicking with 20+ different methods
- Emoji handling fix for Edge driver (BMP character issue)
- Comprehensive logging
- Screenshot capture
"""

import time
import random
import os
import sys
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import logging

# Configure logging to handle Unicode characters properly
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('facebook_warmup.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class StockImageFetcher:
    """Fetch stock images from Unsplash or Pexels API"""
    
    def __init__(self, unsplash_api_key=None, pexels_api_key=None):
        self.unsplash_api_key = unsplash_api_key
        self.pexels_api_key = pexels_api_key
        self.download_folder = Path("temp_images")
        self.download_folder.mkdir(exist_ok=True)
        
        self.search_queries = [
            "nature", "landscape", "sunset", "ocean", "mountains", "forest",
            "city", "architecture", "travel", "food", "coffee", "technology",
            "fitness", "yoga", "motivation", "success", "business", "workspace",
            "flowers", "animals", "beach", "sky", "art", "abstract", "minimal"
        ]
    
    def fetch_from_unsplash(self, query=None):
        """Fetch a random image from Unsplash API"""
        try:
            if not self.unsplash_api_key:
                logger.warning("Unsplash API key not provided")
                return None, None, None
            
            query = query or random.choice(self.search_queries)
            logger.info(f"Fetching Unsplash image for: {query}")
            
            url = "https://api.unsplash.com/photos/random"
            params = {
                "query": query,
                "orientation": "landscape",
                "content_filter": "high",
                "client_id": self.unsplash_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            image_url = data["urls"]["regular"]
            description = data.get("description") or data.get("alt_description") or query.title()
            photographer = data["user"]["name"]
            
            logger.info(f"Found image by {photographer}: {description}")
            
            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()
            
            image_filename = f"unsplash_{int(time.time())}.jpg"
            image_path = self.download_folder / image_filename
            
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            
            logger.info(f"Image downloaded: {image_path}")
            
            return str(image_path), description, photographer
            
        except Exception as e:
            logger.error(f"Error fetching from Unsplash: {str(e)}")
            return None, None, None
    
    def fetch_from_pexels(self, query=None):
        """Fetch a random image from Pexels API"""
        try:
            if not self.pexels_api_key:
                logger.warning("Pexels API key not provided")
                return None, None, None
            
            query = query or random.choice(self.search_queries)
            logger.info(f"Fetching Pexels image for: {query}")
            
            url = "https://api.pexels.com/v1/search"
            headers = {
                "Authorization": self.pexels_api_key
            }
            params = {
                "query": query,
                "per_page": 20,
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("photos"):
                logger.warning("No photos found")
                return None, None, None
            
            photo = random.choice(data["photos"])
            
            image_url = photo["src"]["large"]
            description = photo.get("alt") or query.title()
            photographer = photo["photographer"]
            
            logger.info(f"Found image by {photographer}: {description}")
            
            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()
            
            image_filename = f"pexels_{int(time.time())}.jpg"
            image_path = self.download_folder / image_filename
            
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            
            logger.info(f"Image downloaded: {image_path}")
            
            return str(image_path), description, photographer
            
        except Exception as e:
            logger.error(f"Error fetching from Pexels: {str(e)}")
            return None, None, None
    
    def get_random_image(self):
        """Get a random image from available sources"""
        sources = []
        if self.unsplash_api_key:
            sources.append("unsplash")
        if self.pexels_api_key:
            sources.append("pexels")
        
        if not sources:
            logger.error("No API keys provided!")
            return None, None
        
        random.shuffle(sources)
        
        for source in sources:
            if source == "unsplash":
                image_path, description, photographer = self.fetch_from_unsplash()
            else:
                image_path, description, photographer = self.fetch_from_pexels()
            
            if image_path:
                # FIXED: No emoji in caption - Edge driver can't handle non-BMP characters
                caption = f"{description}"
                if photographer:
                    caption += f"\nPhoto by {photographer}"
                
                return image_path, caption
        
        return None, None
    
    def cleanup(self):
        """Clean up temporary downloaded images"""
        try:
            for file in self.download_folder.glob("*"):
                if file.is_file():
                    file.unlink()
            logger.info("Cleaned up temporary images")
        except Exception as e:
            logger.error(f"Error cleaning up: {str(e)}")


class FacebookWarmupBot:
    """Main bot class for Facebook warmup activities"""
    
    def __init__(self, profile_path=None, unsplash_api_key=None, pexels_api_key=None):
        self.driver = None
        self.profile_path = profile_path
        self.wait_time = 10
        
        # Initialize image fetcher
        self.image_fetcher = StockImageFetcher(unsplash_api_key, pexels_api_key)
        
        # Screenshots folder
        self.screenshots_folder = Path("warmupss")
        self.screenshots_folder.mkdir(exist_ok=True)
        logger.info(f"Screenshots will be saved to: {self.screenshots_folder}")
        
        # EXACT XPATHs for Facebook elements (can be customized)
        self.LIKE_BUTTON_XPATH = "//div[@aria-label='Like'][@role='button']"
        self.COMMENT_BUTTON_XPATH = "//span[contains(text(), 'Comment')]"
        self.FIRST_STORY_XPATH = "//div[contains(@aria-label, 'Stories')]//div[@role='button']"
    
    def setup_browser(self):
        """Setup Microsoft Edge browser with profile"""
        try:
            logger.info("Setting up Microsoft Edge browser...")
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            driver_path = os.path.join(current_dir, "edgedriver_win64", "msedgedriver.exe")
            
            if not os.path.exists(driver_path):
                logger.error(f"Edge driver not found at: {driver_path}")
                logger.error("Please ensure msedgedriver.exe is in the edgedriver_win64 folder")
                return False
            
            logger.info(f"Using Edge driver from: {driver_path}")
            
            edge_options = EdgeOptions()
            
            if self.profile_path:
                logger.info(f"Loading Edge profile from: {self.profile_path}")
                
                # Parse the profile path to extract user-data-dir and profile-directory
                # Edge requires both arguments to load an existing profile correctly
                profile_path = self.profile_path.replace("\\", "/")  # Normalize path
                
                # Check if path contains a Profile folder (Profile 1, Profile 2, Default, etc.)
                if "/Profile " in profile_path or profile_path.endswith("/Default"):
                    # Split into user-data-dir and profile-directory
                    path_parts = profile_path.rsplit("/", 1)
                    user_data_dir = path_parts[0]
                    profile_dir = path_parts[1]
                    
                    logger.info(f"User Data Dir: {user_data_dir}")
                    logger.info(f"Profile Dir: {profile_dir}")
                    
                    edge_options.add_argument(f"--user-data-dir={user_data_dir}")
                    edge_options.add_argument(f"--profile-directory={profile_dir}")
                else:
                    # Path is just the User Data folder, use Default profile
                    logger.info(f"Using User Data Dir with Default profile")
                    edge_options.add_argument(f"--user-data-dir={self.profile_path}")
                    edge_options.add_argument("--profile-directory=Default")
            
            edge_options.add_argument("--start-maximized")
            edge_options.add_argument("--disable-blink-features=AutomationControlled")
            edge_options.add_argument("--no-first-run")
            edge_options.add_argument("--no-default-browser-check")
            edge_options.add_argument("--disable-popup-blocking")
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_experimental_option("useAutomationExtension", False)
            
            edge_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2
            })
            
            service = EdgeService(executable_path=driver_path)
            self.driver = webdriver.Edge(service=service, options=edge_options)
            
            self.driver.implicitly_wait(self.wait_time)
            self.driver.set_page_load_timeout(30)
            
            logger.info("Browser setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up browser: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def navigate_to_facebook(self):
        """Navigate to Facebook homepage"""
        try:
            logger.info("Navigating to Facebook...")
            self.driver.get("https://www.facebook.com")
            
            logger.info("Waiting for page to load...")
            time.sleep(random.uniform(3, 5))
            
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            if "facebook.com" in current_url:
                logger.info("Successfully loaded Facebook")
                return True
            else:
                logger.warning(f"Unexpected URL: {current_url}")
                return False
            
        except Exception as e:
            logger.error(f"Error navigating to Facebook: {str(e)}")
            return False
    
    def wait_for_element(self, by, value, timeout=None):
        """Wait for an element to be present"""
        try:
            timeout = timeout or self.wait_time
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {value}")
            return None
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add a random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)
    
    def scroll_page(self, scroll_amount=None):
        """Scroll the page by a random or specified amount"""
        try:
            if scroll_amount is None:
                scroll_amount = random.randint(300, 800)
            
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            logger.debug(f"Scrolled {scroll_amount} pixels")
            self.random_delay(1, 2)
            
        except Exception as e:
            logger.error(f"Error scrolling page: {str(e)}")
    
    def check_login_status(self):
        """Check if user is logged in to Facebook"""
        try:
            logger.info("Checking login status...")
            time.sleep(2)
            
            # Check for login page indicators
            login_indicators = [
                (By.NAME, "email"),
                (By.NAME, "pass"),
                (By.CSS_SELECTOR, "[data-testid='royal_login_button']"),
                (By.XPATH, "//button[@name='login']")
            ]
            
            for by, value in login_indicators:
                try:
                    element = self.driver.find_element(by, value)
                    if element.is_displayed():
                        logger.error("NOT LOGGED IN - Login page detected!")
                        return False
                except NoSuchElementException:
                    continue
            
            # Check for logged in indicators
            logged_in_indicators = [
                (By.CSS_SELECTOR, "[aria-label='Account']"),
                (By.CSS_SELECTOR, "[aria-label='Your profile']"),
                (By.CSS_SELECTOR, "[aria-label='Profile']"),
                (By.XPATH, "//a[contains(@href, '/me/')]"),
                (By.CSS_SELECTOR, "[role='navigation']"),
                (By.XPATH, "//span[contains(text(), \"What's on your mind\")]")
            ]
            
            for by, value in logged_in_indicators:
                try:
                    element = self.driver.find_element(by, value)
                    if element:
                        logger.info("SUCCESS: User is logged in to Facebook!")
                        return True
                except NoSuchElementException:
                    continue
            
            logger.warning("Unable to confirm login status")
            return False
            
        except Exception as e:
            logger.error(f"Error checking login status: {str(e)}")
            return False
    
    def verify_feed_access(self):
        """Verify that the user can access their news feed"""
        try:
            logger.info("Verifying feed access...")
            time.sleep(3)
            
            feed_indicators = [
                (By.CSS_SELECTOR, "[role='feed']"),
                (By.CSS_SELECTOR, "[aria-label='Stories']"),
                (By.XPATH, "//span[contains(text(), \"What's on your mind\")]"),
                (By.CSS_SELECTOR, "[role='article']"),
                (By.CSS_SELECTOR, "[role='main']"),
            ]
            
            elements_found = 0
            
            for by, value in feed_indicators:
                try:
                    element = self.driver.find_element(by, value)
                    if element.is_displayed():
                        elements_found += 1
                except NoSuchElementException:
                    continue
            
            if elements_found >= 2:
                logger.info(f"SUCCESS: Feed verified! Found {elements_found} feed elements")
                
                try:
                    posts = self.driver.find_elements(By.CSS_SELECTOR, "[role='article']")
                    if posts:
                        logger.info(f"INFO: Visible posts in feed: {len(posts)}")
                except:
                    pass
                
                return True
            else:
                logger.warning(f"Feed verification incomplete - only found {elements_found} elements")
                return False
            
        except Exception as e:
            logger.error(f"Error verifying feed access: {str(e)}")
            return False
    
    def visit_first_post_profile(self):
        """Visit the profile of the first post author - Enhanced with multiple fallback methods"""
        try:
            logger.info("VISITING FIRST POST AUTHOR'S PROFILE")
            logger.info("Trying multiple methods to find and click profile...")
            
            # Scroll to load first post
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.random_delay(2, 3)
            self.scroll_page(300)
            self.random_delay(2, 3)
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.random_delay(2, 3)
            
            current_url_before = self.driver.current_url
            
            # METHOD 0: Use exact XPATH provided by user (HIGHEST PRIORITY)
            if self._try_profile_method_exact_xpath():
                return self._verify_profile_navigation(current_url_before)
            
            # METHOD 1: Find profile link in first article using various selectors
            if self._try_profile_method_1():
                return self._verify_profile_navigation(current_url_before)
            
            # METHOD 2: Find profile link by looking for strong/h4 tags with links
            if self._try_profile_method_2():
                return self._verify_profile_navigation(current_url_before)
            
            # METHOD 3: Find by aria-label containing profile-related text
            if self._try_profile_method_3():
                return self._verify_profile_navigation(current_url_before)
            
            # METHOD 4: Find profile picture and click it
            if self._try_profile_method_4():
                return self._verify_profile_navigation(current_url_before)
            
            # METHOD 5: Use XPath to find specific profile link patterns
            if self._try_profile_method_5():
                return self._verify_profile_navigation(current_url_before)
            
            # METHOD 6: Click on the first clickable user name
            if self._try_profile_method_6():
                return self._verify_profile_navigation(current_url_before)
            
            logger.warning("All profile visit methods failed")
            self.take_screenshot("profile_all_methods_failed.png")
            return False
            
        except Exception as e:
            logger.error(f"Error visiting profile: {str(e)}")
            self.take_screenshot("profile_visit_error.png")
            return False
    
    def _try_profile_method_exact_xpath(self):
        """Method 0: Use exact XPATH provided for profile name (HIGHEST PRIORITY)"""
        try:
            logger.info("METHOD 0: Trying exact XPATHs for profile name...")
            
            # Exact XPATHs for profile name - these are Facebook's actual structure
            exact_xpaths = [
                # User provided XPATH
                "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div/div[4]/div/div[2]/div[4]/div/span/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[1]/span/div/h4/span/span/span/span/a/b/span",
                # Try clicking the parent <a> tag instead
                "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div/div[4]/div/div[2]/div[4]/div/span/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[1]/span/div/h4/span/span/span/span/a",
                # Variations for different post positions (div[2], div[3], etc.)
                "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div/div[4]/div/div[2]/div[2]/div/span/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[1]/span/div/h4/span/span/span/span/a",
                "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div/div[4]/div/div[2]/div[3]/div/span/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[1]/span/div/h4/span/span/span/span/a",
                "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div/div[4]/div/div[2]/div[1]/div/span/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[1]/span/div/h4/span/span/span/span/a",
            ]
            
            for xpath in exact_xpaths:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    if element and element.is_displayed():
                        logger.info(f"Method 0: Found element with exact XPATH")
                        
                        # Try to get the link - might need to find parent <a>
                        try:
                            # If element is the span, find parent link
                            if element.tag_name != 'a':
                                parent_link = element.find_element(By.XPATH, "./ancestor::a")
                                if parent_link:
                                    element = parent_link
                        except:
                            pass
                        
                        href = element.get_attribute("href") if element.tag_name == 'a' else None
                        logger.info(f"Method 0: Profile link: {href}")
                        
                        # Scroll into view and click
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        self.random_delay(1, 2)
                        
                        self._click_element_safe(element)
                        self.random_delay(3, 5)
                        return True
                        
                except NoSuchElementException:
                    continue
                except Exception as e:
                    logger.debug(f"XPATH attempt failed: {e}")
                    continue
            
            # Also try relative XPATHs based on the structure
            relative_xpaths = [
                "//div[@role='article']//h4//a[.//span]",
                "//div[@role='article']//h4/span/span/span/span/a",
                "//div[@role='article'][1]//h4//a",
                "//div[contains(@data-pagelet, 'FeedUnit')]//h4//a",
            ]
            
            for xpath in relative_xpaths:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for elem in elements[:5]:
                        if elem.is_displayed():
                            href = elem.get_attribute("href")
                            if href and "facebook.com" in href and "/photo" not in href and "/video" not in href:
                                logger.info(f"Method 0: Found profile via relative XPATH: {href}")
                                self._click_element_safe(elem)
                                self.random_delay(3, 5)
                                return True
                except:
                    continue
            
            logger.warning("Method 0: Exact XPATHs did not match")
            return False
            
        except Exception as e:
            logger.warning(f"Method 0 failed: {e}")
            return False
    
    def _try_profile_method_1(self):
        """Method 1: Find profile link in first article by checking all links"""
        try:
            logger.info("METHOD 1: Searching links in first article...")
            
            posts = self.driver.find_elements(By.CSS_SELECTOR, "[role='article']")
            if not posts:
                logger.warning("Method 1: No posts found")
                return False
            
            # Try first 3 posts
            for post_index, post in enumerate(posts[:3]):
                logger.info(f"Method 1: Checking post {post_index + 1}...")
                
                links = post.find_elements(By.TAG_NAME, "a")
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                        
                        # Skip non-profile links
                        skip_patterns = ["/photo", "/video", "/posts", "/watch", "/reel", 
                                        "/groups/", "/events/", "/hashtag/", "story_fbid",
                                        "/shares", "/comments", "?comment_id"]
                        
                        if any(pattern in href for pattern in skip_patterns):
                            continue
                        
                        # Check if it looks like a profile URL
                        if "facebook.com" in href:
                            # Profile URLs usually are facebook.com/username or facebook.com/profile.php
                            if "/profile.php" in href or (href.count("/") <= 4 and "?" not in href):
                                if link.is_displayed():
                                    logger.info(f"Method 1: Found profile link: {href}")
                                    self._click_element_safe(link)
                                    self.random_delay(3, 5)
                                    return True
                    except StaleElementReferenceException:
                        continue
                    except Exception as e:
                        continue
            
            logger.warning("Method 1: No suitable profile link found")
            return False
            
        except Exception as e:
            logger.warning(f"Method 1 failed: {e}")
            return False
    
    def _try_profile_method_2(self):
        """Method 2: Find profile by looking for name elements (h4, strong, span with links)"""
        try:
            logger.info("METHOD 2: Searching for name elements with links...")
            
            # XPath patterns for profile names
            name_selectors = [
                "//div[@role='article']//h4//a[contains(@href, 'facebook.com')]",
                "//div[@role='article']//strong//a[contains(@href, 'facebook.com')]",
                "//div[@role='article']//span[@dir='auto']//a[contains(@href, 'facebook.com')]",
                "//div[@role='article']//a[contains(@href, '/user/')]",
                "//div[@role='article']//a[contains(@href, 'profile.php')]",
            ]
            
            for selector in name_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            href = elem.get_attribute("href")
                            if href and "/photo" not in href and "/video" not in href:
                                logger.info(f"Method 2: Found name link: {href}")
                                self._click_element_safe(elem)
                                self.random_delay(3, 5)
                                return True
                except:
                    continue
            
            logger.warning("Method 2: No name elements found")
            return False
            
        except Exception as e:
            logger.warning(f"Method 2 failed: {e}")
            return False
    
    def _try_profile_method_3(self):
        """Method 3: Find profile by aria-label attributes"""
        try:
            logger.info("METHOD 3: Searching by aria-label...")
            
            aria_selectors = [
                "//a[contains(@aria-label, 'profile')]",
                "//a[contains(@aria-label, 'Profile')]",
                "//a[@aria-label and contains(@href, 'facebook.com/')]",
                "//div[@role='article']//a[@role='link'][contains(@href, 'facebook.com')]",
            ]
            
            for selector in aria_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            href = elem.get_attribute("href")
                            if href and "/photo" not in href and "/video" not in href and "/watch" not in href:
                                logger.info(f"Method 3: Found aria-label link: {href}")
                                self._click_element_safe(elem)
                                self.random_delay(3, 5)
                                return True
                except:
                    continue
            
            logger.warning("Method 3: No aria-label links found")
            return False
            
        except Exception as e:
            logger.warning(f"Method 3 failed: {e}")
            return False
    
    def _try_profile_method_4(self):
        """Method 4: Click on profile picture/avatar"""
        try:
            logger.info("METHOD 4: Searching for profile picture...")
            
            avatar_selectors = [
                "//div[@role='article']//a[.//svg[@aria-label]]",
                "//div[@role='article']//a[.//image]",
                "//div[@role='article']//a[contains(@href, 'facebook.com')][.//img[contains(@alt, '')]]",
                "//div[@role='article']//a[@tabindex='0'][.//img]",
                "//div[@role='article']//a[contains(@class, 'avatar')]",
            ]
            
            for selector in avatar_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements[:5]:  # Check first 5 matches
                        if elem.is_displayed():
                            href = elem.get_attribute("href")
                            if href and "facebook.com" in href:
                                if "/photo" not in href and "/video" not in href:
                                    logger.info(f"Method 4: Found avatar link: {href}")
                                    self._click_element_safe(elem)
                                    self.random_delay(3, 5)
                                    return True
                except:
                    continue
            
            logger.warning("Method 4: No avatar links found")
            return False
            
        except Exception as e:
            logger.warning(f"Method 4 failed: {e}")
            return False
    
    def _try_profile_method_5(self):
        """Method 5: Use JavaScript to find and click profile link"""
        try:
            logger.info("METHOD 5: Using JavaScript to find profile links...")
            
            # JavaScript to find profile links
            js_code = """
            var articles = document.querySelectorAll('[role="article"]');
            for (var i = 0; i < Math.min(articles.length, 3); i++) {
                var links = articles[i].querySelectorAll('a[href*="facebook.com"]');
                for (var j = 0; j < links.length; j++) {
                    var href = links[j].href;
                    if (href && !href.includes('/photo') && !href.includes('/video') && 
                        !href.includes('/posts') && !href.includes('/watch') &&
                        !href.includes('story_fbid') && !href.includes('/groups/')) {
                        // Check if it's likely a profile link (short path)
                        var pathParts = href.replace('https://www.facebook.com/', '').split('/');
                        if (pathParts.length <= 2 && pathParts[0] && !pathParts[0].includes('?')) {
                            return links[j];
                        }
                    }
                }
            }
            return null;
            """
            
            element = self.driver.execute_script(js_code)
            if element:
                href = element.get_attribute("href")
                logger.info(f"Method 5: JS found profile link: {href}")
                self.driver.execute_script("arguments[0].click();", element)
                self.random_delay(3, 5)
                return True
            
            logger.warning("Method 5: JS found no profile links")
            return False
            
        except Exception as e:
            logger.warning(f"Method 5 failed: {e}")
            return False
    
    def _try_profile_method_6(self):
        """Method 6: Find first clickable username text"""
        try:
            logger.info("METHOD 6: Looking for clickable username text...")
            
            # Find text elements that look like usernames
            username_selectors = [
                "//div[@role='article'][1]//a//span[string-length(text()) > 2 and string-length(text()) < 50]",
                "//div[@role='article'][1]//h4//a",
                "//div[@role='article'][1]//a[@role='link']//strong",
            ]
            
            for selector in username_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements[:10]:
                        try:
                            # Find the parent link
                            parent_link = elem.find_element(By.XPATH, "./ancestor::a")
                            if parent_link and parent_link.is_displayed():
                                href = parent_link.get_attribute("href")
                                if href and "facebook.com" in href:
                                    if "/photo" not in href and "/video" not in href:
                                        logger.info(f"Method 6: Found username link: {href}")
                                        self._click_element_safe(parent_link)
                                        self.random_delay(3, 5)
                                        return True
                        except:
                            # Element itself might be the link
                            if elem.tag_name == "a":
                                href = elem.get_attribute("href")
                                if href and "facebook.com" in href and "/photo" not in href:
                                    logger.info(f"Method 6: Found direct link: {href}")
                                    self._click_element_safe(elem)
                                    self.random_delay(3, 5)
                                    return True
                except:
                    continue
            
            logger.warning("Method 6: No username links found")
            return False
            
        except Exception as e:
            logger.warning(f"Method 6 failed: {e}")
            return False
    
    def _click_element_safe(self, element):
        """Safely click an element using multiple methods"""
        try:
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            self.random_delay(0.5, 1)
            
            # Try JavaScript click first
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except:
            try:
                # Try regular click
                element.click()
                return True
            except:
                try:
                    # Try ActionChains
                    ActionChains(self.driver).move_to_element(element).click().perform()
                    return True
                except:
                    return False
    
    def _verify_profile_navigation(self, original_url):
        """Verify that we navigated to a profile page"""
        try:
            self.random_delay(2, 3)
            current_url = self.driver.current_url
            
            if current_url == original_url:
                logger.warning("URL did not change after click")
                return False
            
            # Check if we're on a profile page
            profile_indicators = [
                "/profile.php",
                "facebook.com/",
            ]
            
            is_profile = any(indicator in current_url for indicator in profile_indicators)
            
            # Make sure we're not on a photo/video page
            not_profile = ["/photo", "/video", "/posts/", "/watch", "/stories"]
            is_not_profile = any(indicator in current_url for indicator in not_profile)
            
            if is_profile and not is_not_profile:
                logger.info(f"SUCCESS: Navigated to profile: {current_url}")
                
                # Browse profile briefly
                self.scroll_page(400)
                self.random_delay(2, 3)
                
                self.take_screenshot("profile_visit_success.png")
                return True
            else:
                logger.warning(f"Navigated to non-profile page: {current_url}")
                # Go back and try might work for next method
                self.driver.back()
                self.random_delay(2, 3)
                return False
                
        except Exception as e:
            logger.warning(f"Profile verification failed: {e}")
            return False
    
    def go_back_to_home(self):
        """Navigate back to Facebook home feed"""
        try:
            logger.info("RETURNING TO HOME FEED")
            
            self.driver.get("https://www.facebook.com")
            self.random_delay(3, 5)
            
            current_url = self.driver.current_url
            if "facebook.com" in current_url:
                logger.info("SUCCESS: RETURNED TO HOME FEED!")
                self.driver.execute_script("window.scrollTo(0, 0);")
                self.random_delay(2, 3)
                return True
            else:
                logger.warning("May not be on home page")
                return False
            
        except Exception as e:
            logger.error(f"Error returning to home: {str(e)}")
            return False
    
    def watch_and_like_first_story(self):
        """Watch and like the first available story - Enhanced with multiple fallback methods"""
        try:
            logger.info("WATCHING FIRST STORY")
            logger.info("Trying multiple methods to find and open stories...")
            
            # Scroll to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.random_delay(2, 3)
            
            current_url_before = self.driver.current_url
            
            # METHOD 1: Find story by aria-label
            if self._try_story_method_1():
                return self._watch_and_interact_story()
            
            # METHOD 2: Find story cards/thumbnails
            if self._try_story_method_2():
                return self._watch_and_interact_story()
            
            # METHOD 3: Find story by href containing /stories/
            if self._try_story_method_3():
                return self._watch_and_interact_story()
            
            # METHOD 4: Find story container and click first item
            if self._try_story_method_4():
                return self._watch_and_interact_story()
            
            # METHOD 5: Use JavaScript to find stories
            if self._try_story_method_5():
                return self._watch_and_interact_story()
            
            # METHOD 6: Find by image/avatar in story section
            if self._try_story_method_6():
                return self._watch_and_interact_story()
            
            logger.warning("All story methods failed - no stories found or clickable")
            self.take_screenshot("story_all_methods_failed.png")
            return False
            
        except Exception as e:
            logger.error(f"Error with story: {str(e)}")
            self._close_story()
            return False
    
    def _try_story_method_1(self):
        """Method 1: Find story by aria-label attributes"""
        try:
            logger.info("METHOD 1: Searching by aria-label...")
            
            story_selectors = [
                "//div[@aria-label='Stories']//div[@role='button']",
                "//div[contains(@aria-label, 'Stories')]//a",
                "//div[@aria-label='Stories']//a",
                "//*[@aria-label='Stories']/following-sibling::*//div[@role='button']",
                "//div[@aria-label='Stories']//div[contains(@style, 'cursor')]",
            ]
            
            for selector in story_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    # Skip the first one if it's "Create story" - usually second element is first real story
                    for i, elem in enumerate(elements):
                        if elem.is_displayed():
                            # Check if it's not the "Create story" or "Add to story" button
                            text = elem.text.lower() if elem.text else ""
                            aria = (elem.get_attribute("aria-label") or "").lower()
                            
                            if "create" in text or "create" in aria or "add" in text:
                                continue
                            
                            logger.info(f"Method 1: Found story element at index {i}")
                            self._click_element_safe(elem)
                            self.random_delay(3, 5)
                            
                            if self._verify_story_opened():
                                return True
                except:
                    continue
            
            logger.warning("Method 1: No story elements found")
            return False
            
        except Exception as e:
            logger.warning(f"Method 1 failed: {e}")
            return False
    
    def _try_story_method_2(self):
        """Method 2: Find story cards/thumbnails"""
        try:
            logger.info("METHOD 2: Searching for story cards...")
            
            card_selectors = [
                "//div[@role='button'][.//img[contains(@alt, 'story') or contains(@alt, 'Story')]]",
                "//a[contains(@href, '/stories/')][.//img]",
                "//div[contains(@class, 'story')]//div[@role='button']",
                "//div[@role='button'][.//div[contains(@style, 'background-image')]]",
            ]
            
            for selector in card_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements[1:6]:  # Skip first (might be Create), try next 5
                        if elem.is_displayed():
                            logger.info("Method 2: Found story card")
                            self._click_element_safe(elem)
                            self.random_delay(3, 5)
                            
                            if self._verify_story_opened():
                                return True
                except:
                    continue
            
            logger.warning("Method 2: No story cards found")
            return False
            
        except Exception as e:
            logger.warning(f"Method 2 failed: {e}")
            return False
    
    def _try_story_method_3(self):
        """Method 3: Find story links by href"""
        try:
            logger.info("METHOD 3: Searching for story links...")
            
            link_selectors = [
                "//a[contains(@href, '/stories/')]",
                "//a[contains(@href, 'story_fbid')]",
                "//a[contains(@href, '/story.php')]",
            ]
            
            for selector in link_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            href = elem.get_attribute("href")
                            logger.info(f"Method 3: Found story link: {href}")
                            self._click_element_safe(elem)
                            self.random_delay(3, 5)
                            
                            if self._verify_story_opened():
                                return True
                except:
                    continue
            
            logger.warning("Method 3: No story links found")
            return False
            
        except Exception as e:
            logger.warning(f"Method 3 failed: {e}")
            return False
    
    def _try_story_method_4(self):
        """Method 4: Find story container and click child elements"""
        try:
            logger.info("METHOD 4: Searching story container...")
            
            # Find the stories section container
            container_selectors = [
                "//div[@aria-label='Stories']",
                "//div[contains(@aria-label, 'Stories')]",
                "//div[.//*[text()='Stories']]",
            ]
            
            for selector in container_selectors:
                try:
                    container = self.driver.find_element(By.XPATH, selector)
                    if container:
                        # Find clickable items within
                        clickables = container.find_elements(By.XPATH, ".//div[@role='button'] | .//a")
                        
                        for i, elem in enumerate(clickables[1:8]):  # Skip first, try next 7
                            if elem.is_displayed():
                                logger.info(f"Method 4: Clicking story container item {i}")
                                self._click_element_safe(elem)
                                self.random_delay(3, 5)
                                
                                if self._verify_story_opened():
                                    return True
                                else:
                                    # If didn't open, go back to home
                                    self.driver.get("https://www.facebook.com")
                                    self.random_delay(2, 3)
                except:
                    continue
            
            logger.warning("Method 4: Could not find story container")
            return False
            
        except Exception as e:
            logger.warning(f"Method 4 failed: {e}")
            return False
    
    def _try_story_method_5(self):
        """Method 5: Use JavaScript to find and click stories"""
        try:
            logger.info("METHOD 5: Using JavaScript to find stories...")
            
            js_code = """
            // Find the Stories section
            var storySection = document.querySelector('[aria-label="Stories"]') || 
                               document.querySelector('[aria-label*="Stories"]');
            
            if (storySection) {
                // Find all clickable items
                var items = storySection.querySelectorAll('div[role="button"], a');
                
                // Skip first item (usually "Create story"), return second or third
                for (var i = 1; i < Math.min(items.length, 5); i++) {
                    var item = items[i];
                    if (item.offsetParent !== null) {  // Check if visible
                        var text = item.innerText || '';
                        if (!text.toLowerCase().includes('create') && !text.toLowerCase().includes('add')) {
                            return item;
                        }
                    }
                }
            }
            
            // Alternative: find any story link
            var storyLinks = document.querySelectorAll('a[href*="/stories/"]');
            if (storyLinks.length > 0) {
                return storyLinks[0];
            }
            
            return null;
            """
            
            element = self.driver.execute_script(js_code)
            if element:
                logger.info("Method 5: JS found story element")
                self.driver.execute_script("arguments[0].click();", element)
                self.random_delay(3, 5)
                
                if self._verify_story_opened():
                    return True
            
            logger.warning("Method 5: JS found no stories")
            return False
            
        except Exception as e:
            logger.warning(f"Method 5 failed: {e}")
            return False
    
    def _try_story_method_6(self):
        """Method 6: Find story by circular avatar images"""
        try:
            logger.info("METHOD 6: Searching for story avatars...")
            
            avatar_selectors = [
                "//div[@aria-label='Stories']//img[contains(@class, 'avatar') or @alt]/..",
                "//div[@aria-label='Stories']//div[contains(@style, 'border-radius')]",
                "//div[@aria-label='Stories']//svg[@aria-label]/ancestor::div[@role='button']",
                "//div[@aria-label='Stories']//image/ancestor::a",
            ]
            
            for selector in avatar_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements[1:5]:  # Skip first, try next 4
                        if elem.is_displayed():
                            logger.info("Method 6: Found story avatar")
                            self._click_element_safe(elem)
                            self.random_delay(3, 5)
                            
                            if self._verify_story_opened():
                                return True
                except:
                    continue
            
            logger.warning("Method 6: No story avatars found")
            return False
            
        except Exception as e:
            logger.warning(f"Method 6 failed: {e}")
            return False
    
    def _verify_story_opened(self):
        """Verify that a story viewer has opened"""
        try:
            current_url = self.driver.current_url
            
            # Check URL
            if "/stories/" in current_url:
                logger.info("Story viewer opened (URL contains /stories/)")
                return True
            
            # Check for story dialog/viewer
            viewer_selectors = [
                "//div[@role='dialog'][.//video or .//img]",
                "//div[contains(@class, 'story')][@role='dialog']",
                "//div[@aria-label='Story viewer']",
                "//div[@role='dialog']//div[contains(@style, 'transform')]",
            ]
            
            for selector in viewer_selectors:
                try:
                    elem = self.driver.find_element(By.XPATH, selector)
                    if elem.is_displayed():
                        logger.info("Story viewer opened (dialog found)")
                        return True
                except:
                    continue
            
            # Check for video playing (stories are usually videos)
            try:
                video = self.driver.find_element(By.XPATH, "//video[@src or @currentSrc]")
                if video.is_displayed():
                    logger.info("Story viewer opened (video found)")
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            logger.warning(f"Story verification failed: {e}")
            return False
    
    def _watch_and_interact_story(self):
        """Watch the story and try to like it"""
        try:
            # Watch story for random duration
            watch_duration = random.uniform(5, 8)
            logger.info(f"Watching story for {watch_duration:.1f} seconds...")
            time.sleep(watch_duration)
            
            # Try to like the story
            like_selectors = [
                (By.XPATH, "//div[@role='button'][@aria-label='Like']"),
                (By.XPATH, "//div[@aria-label='Like']"),
                (By.CSS_SELECTOR, "[aria-label='Like']"),
                (By.XPATH, "//span[text()='Like']/ancestor::div[@role='button']"),
                (By.XPATH, "//*[@aria-label='Like' and @role='button']"),
            ]
            
            like_clicked = False
            for by, selector in like_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            aria = (elem.get_attribute("aria-label") or "").lower()
                            if "unlike" not in aria:
                                logger.info("Found like button, clicking...")
                                self._click_element_safe(elem)
                                like_clicked = True
                                self.random_delay(1, 2)
                                break
                    if like_clicked:
                        break
                except:
                    continue
            
            if like_clicked:
                logger.info("Story liked!")
            else:
                logger.info("Like button not found in story, but story was watched")
            
            # Close story
            self._close_story()
            
            logger.info("SUCCESS: STORY WATCHED!")
            self.take_screenshot("story_success.png")
            return True
            
        except Exception as e:
            logger.warning(f"Error watching story: {e}")
            self._close_story()
            return True  # Return True since we at least opened the story
    
    def _close_story(self):
        """Close the story viewer - Enhanced with multiple methods"""
        try:
            logger.info("Closing story viewer...")
            
            # Method 1: Escape key
            try:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                self.random_delay(1, 2)
                
                # Check if closed
                if "/stories/" not in self.driver.current_url:
                    logger.info("Story closed with Escape key")
                    return True
            except:
                pass
            
            # Method 2: Close button
            close_selectors = [
                "//div[@aria-label='Close']",
                "//div[@role='button'][@aria-label='Close']",
                "//*[@aria-label='Close']",
                "//div[contains(@class, 'close')][@role='button']",
                "//svg[@aria-label='Close']/ancestor::div[@role='button']",
            ]
            
            for selector in close_selectors:
                try:
                    elem = self.driver.find_element(By.XPATH, selector)
                    if elem.is_displayed():
                        self._click_element_safe(elem)
                        self.random_delay(1, 2)
                        logger.info("Story closed with close button")
                        return True
                except:
                    continue
            
            # Method 3: Click outside the story
            try:
                self.driver.execute_script("""
                    var backdrop = document.querySelector('[role="dialog"]');
                    if (backdrop) {
                        var event = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            clientX: 10,
                            clientY: 10
                        });
                        document.body.dispatchEvent(event);
                    }
                """)
                self.random_delay(1, 2)
            except:
                pass
            
            # Method 4: Navigate back to home
            try:
                if "/stories/" in self.driver.current_url:
                    self.driver.get("https://www.facebook.com")
                    self.random_delay(2, 3)
                    logger.info("Navigated back to home to close story")
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.warning(f"Error closing story: {e}")
            return True
    
    def generate_random_comment(self):
        """Generate a random comment WITHOUT emojis (Edge driver BMP issue)"""
        positive_words = [
            "Amazing", "Great", "Awesome", "Fantastic", "Wonderful", "Brilliant",
            "Perfect", "Excellent", "Beautiful", "Incredible", "Outstanding",
            "Lovely", "Superb", "Magnificent", "Impressive", "Remarkable"
        ]
        
        reactions = [
            "post", "content", "share", "photo", "update", "message",
            "story", "moment", "picture", "thought", "idea", "perspective"
        ]
        
        # FIXED: No emojis - Edge driver can't handle non-BMP characters
        endings = [
            "!", "!!", "!!!", ".", "..", "...", ":)", ":D", ";)", 
            " - love it!", " - so good!", " - thanks for sharing!"
        ]
        
        structures = [
            f"{random.choice(positive_words)} {random.choice(reactions)}{random.choice(endings)}",
            f"{random.choice(positive_words)}{random.choice(endings)}",
            f"Love this{random.choice(endings)}",
            f"Thanks for sharing{random.choice(endings)}",
            f"This is {random.choice(positive_words).lower()}{random.choice(endings)}",
            f"So {random.choice(positive_words).lower()}{random.choice(endings)}",
            f"{random.choice(positive_words)} stuff{random.choice(endings)}",
            f"Really {random.choice(positive_words).lower()}!",
            f"What a {random.choice(positive_words).lower()} {random.choice(reactions)}!",
        ]
        
        return random.choice(structures)
    
    def like_first_post(self):
        """Like the first post in the feed"""
        try:
            logger.info("LIKING FIRST POST IN FEED")
            
            # Scroll to load post
            self.scroll_page(300)
            self.random_delay(2, 3)
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.random_delay(2, 3)
            
            # Find like button
            like_selectors = [
                (By.XPATH, "//div[@aria-label='Like'][@role='button']"),
                (By.XPATH, "//span[text()='Like']/ancestor::div[@role='button']"),
                (By.CSS_SELECTOR, "[aria-label='Like'][role='button']"),
            ]
            
            like_button = None
            for by, selector in like_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            aria = elem.get_attribute("aria-label")
                            if aria and "unlike" not in aria.lower():
                                like_button = elem
                                break
                    if like_button:
                        break
                except:
                    continue
            
            if not like_button:
                logger.error("Like button not found")
                self.take_screenshot("like_button_not_found.png")
                return False
            
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", like_button)
            self.random_delay(1, 2)
            
            # Check if already liked
            try:
                aria_label = like_button.get_attribute("aria-label")
                if aria_label and "unlike" in aria_label.lower():
                    logger.info("Post is already liked")
                    return True
            except:
                pass
            
            # Click like
            try:
                self.driver.execute_script("arguments[0].click();", like_button)
                logger.info("Like button clicked")
            except:
                try:
                    like_button.click()
                except:
                    logger.error("Could not click like button")
                    return False
            
            self.random_delay(2, 3)
            
            logger.info("SUCCESS: POST LIKED!")
            self.take_screenshot("like_success.png")
            return True
            
        except Exception as e:
            logger.error(f"Error liking post: {str(e)}")
            self.take_screenshot("like_error.png")
            return False
    
    def comment_on_first_post(self, comment_text=None):
        """Comment on the first post in the feed"""
        try:
            logger.info("COMMENTING ON FIRST POST IN FEED")
            
            if not comment_text:
                comment_text = self.generate_random_comment()
            
            logger.info(f"Comment text: {comment_text}")
            
            # Find comment button
            comment_selectors = [
                (By.XPATH, "//span[contains(text(), 'Comment')]"),
                (By.XPATH, "//div[@role='button' and contains(., 'Comment')]"),
                (By.CSS_SELECTOR, "[aria-label*='Comment']"),
            ]
            
            comment_button = None
            for by, selector in comment_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            comment_button = elem
                            break
                    if comment_button:
                        break
                except:
                    continue
            
            if not comment_button:
                logger.error("Comment button not found")
                return False
            
            # Click comment button
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", comment_button)
            self.random_delay(1, 2)
            
            try:
                self.driver.execute_script("arguments[0].click();", comment_button)
            except:
                try:
                    comment_button.click()
                except:
                    logger.error("Could not click comment button")
                    return False
            
            self.random_delay(2, 3)
            
            # Find comment input
            input_selectors = [
                (By.XPATH, "//div[@role='textbox' and @contenteditable='true']"),
                (By.CSS_SELECTOR, "div[role='textbox'][contenteditable='true']"),
            ]
            
            comment_input = None
            for by, selector in input_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for elem in reversed(elements):
                        if elem.is_displayed() and elem.is_enabled():
                            comment_input = elem
                            break
                    if comment_input:
                        break
                except:
                    continue
            
            if not comment_input:
                logger.error("Comment input not found")
                return False
            
            # Click and type comment
            try:
                comment_input.click()
            except:
                self.driver.execute_script("arguments[0].click();", comment_input)
            
            self.random_delay(1, 2)
            
            # Type comment character by character
            for char in comment_text:
                try:
                    comment_input.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                except:
                    # Fallback to JS for problem characters
                    self.driver.execute_script(
                        "arguments[0].textContent += arguments[1];", 
                        comment_input, 
                        char
                    )
                    self.driver.execute_script("""
                        arguments[0].dispatchEvent(new InputEvent('input', {bubbles: true}));
                    """, comment_input)
            
            self.random_delay(2, 3)
            
            # Submit comment
            try:
                comment_input.send_keys(Keys.RETURN)
            except:
                self.driver.execute_script("""
                    arguments[0].dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', keyCode: 13, bubbles: true}));
                """, comment_input)
            
            self.random_delay(3, 5)
            
            # Close dialog if open
            try:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            except:
                pass
            
            logger.info("SUCCESS: COMMENT POSTED!")
            self.take_screenshot("comment_success.png")
            return True
            
        except Exception as e:
            logger.error(f"Error commenting: {str(e)}")
            self.take_screenshot("comment_error.png")
            return False
    
    def _type_text_with_js(self, element, text):
        """Type text into an element using JavaScript (handles all Unicode)"""
        try:
            self.driver.execute_script("arguments[0].focus();", element)
            time.sleep(0.3)
            
            self.driver.execute_script("""
                var element = arguments[0];
                var text = arguments[1];
                
                element.textContent = '';
                var textNode = document.createTextNode(text);
                element.appendChild(textNode);
                
                element.dispatchEvent(new InputEvent('input', {
                    bubbles: true,
                    cancelable: true,
                    inputType: 'insertText',
                    data: text
                }));
                
                element.dispatchEvent(new Event('change', {bubbles: true}));
            """, element, text)
            
            logger.info(f"Text set via JavaScript ({len(text)} chars)")
            return True
            
        except Exception as e:
            logger.error(f"JavaScript text input failed: {e}")
            return False
    
    def _click_post_button_all_methods(self, post_button):
        """Try ALL possible methods to click the Post button (20+ methods)"""
        logger.info("ATTEMPTING TO CLICK POST BUTTON - ALL METHODS")
        
        # METHOD 1: Simple JavaScript click
        try:
            logger.info("METHOD 1: Simple JavaScript click")
            self.driver.execute_script("arguments[0].click();", post_button)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 1 failed: {e}")
        
        # METHOD 2: Scroll into view + JavaScript click
        try:
            logger.info("METHOD 2: Scroll into view + JavaScript click")
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", 
                post_button
            )
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", post_button)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 2 failed: {e}")
        
        # METHOD 3: Regular Selenium click
        try:
            logger.info("METHOD 3: Regular Selenium click")
            post_button.click()
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 3 failed: {e}")
        
        # METHOD 4: ActionChains move and click
        try:
            logger.info("METHOD 4: ActionChains move_to_element + click")
            actions = ActionChains(self.driver)
            actions.move_to_element(post_button).click().perform()
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 4 failed: {e}")
        
        # METHOD 5: ActionChains with pause
        try:
            logger.info("METHOD 5: ActionChains with pause before click")
            actions = ActionChains(self.driver)
            actions.move_to_element(post_button).pause(0.5).click().perform()
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 5 failed: {e}")
        
        # METHOD 6: MouseEvent dispatch
        try:
            logger.info("METHOD 6: Dispatch MouseEvent (click)")
            self.driver.execute_script("""
                var event = new MouseEvent('click', {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: arguments[0].getBoundingClientRect().x + 10,
                    clientY: arguments[0].getBoundingClientRect().y + 10
                });
                arguments[0].dispatchEvent(event);
            """, post_button)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 6 failed: {e}")
        
        # METHOD 7: PointerEvent dispatch
        try:
            logger.info("METHOD 7: Dispatch PointerEvent")
            self.driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                var centerX = rect.left + rect.width / 2;
                var centerY = rect.top + rect.height / 2;
                
                ['pointerdown', 'pointerup', 'click'].forEach(function(eventType) {
                    var event = new PointerEvent(eventType, {
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        clientX: centerX,
                        clientY: centerY,
                        pointerType: 'mouse'
                    });
                    arguments[0].dispatchEvent(event);
                });
            """, post_button)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 7 failed: {e}")
        
        # METHOD 8: Focus + Enter key
        try:
            logger.info("METHOD 8: Focus element + Enter key")
            self.driver.execute_script("arguments[0].focus();", post_button)
            time.sleep(0.5)
            post_button.send_keys(Keys.ENTER)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 8 failed: {e}")
        
        # METHOD 9: Focus + Space key
        try:
            logger.info("METHOD 9: Focus element + Space key")
            self.driver.execute_script("arguments[0].focus();", post_button)
            time.sleep(0.5)
            post_button.send_keys(Keys.SPACE)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 9 failed: {e}")
        
        # METHOD 10: Remove disabled + click
        try:
            logger.info("METHOD 10: Remove disabled attributes + click")
            self.driver.execute_script("""
                arguments[0].removeAttribute('aria-disabled');
                arguments[0].removeAttribute('disabled');
                arguments[0].style.pointerEvents = 'auto';
                arguments[0].click();
            """, post_button)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 10 failed: {e}")
        
        # METHOD 11: Find and click inner span
        try:
            logger.info("METHOD 11: Click inner span element")
            inner_span = post_button.find_element(By.XPATH, ".//span[text()='Post']")
            self.driver.execute_script("arguments[0].click();", inner_span)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 11 failed: {e}")
        
        # METHOD 12: Click parent element
        try:
            logger.info("METHOD 12: Click parent element")
            parent = post_button.find_element(By.XPATH, "..")
            self.driver.execute_script("arguments[0].click();", parent)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 12 failed: {e}")
        
        # METHOD 13: Double click
        try:
            logger.info("METHOD 13: Double click")
            actions = ActionChains(self.driver)
            actions.double_click(post_button).perform()
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 13 failed: {e}")
        
        # METHOD 14: Click at coordinates
        try:
            logger.info("METHOD 14: Click at element coordinates")
            location = post_button.location
            size = post_button.size
            x = location['x'] + size['width'] / 2
            y = location['y'] + size['height'] / 2
            
            self.driver.execute_script(f"""
                document.elementFromPoint({x}, {y}).click();
            """)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 14 failed: {e}")
        
        # METHOD 15: Full mouse event sequence
        try:
            logger.info("METHOD 15: Full mouse event sequence")
            self.driver.execute_script("""
                var element = arguments[0];
                var rect = element.getBoundingClientRect();
                var centerX = rect.left + rect.width / 2;
                var centerY = rect.top + rect.height / 2;
                
                var events = ['mouseenter', 'mouseover', 'mousemove', 'mousedown', 'mouseup', 'click'];
                
                events.forEach(function(eventType) {
                    var event = new MouseEvent(eventType, {
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        clientX: centerX,
                        clientY: centerY
                    });
                    element.dispatchEvent(event);
                });
            """, post_button)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 15 failed: {e}")
        
        # METHOD 16: Click and hold then release
        try:
            logger.info("METHOD 16: Click and hold then release")
            actions = ActionChains(self.driver)
            actions.click_and_hold(post_button).pause(0.2).release().perform()
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 16 failed: {e}")
        
        # METHOD 17: Move by offset and click
        try:
            logger.info("METHOD 17: Move by offset and click")
            actions = ActionChains(self.driver)
            actions.move_to_element_with_offset(post_button, 5, 5).click().perform()
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 17 failed: {e}")
        
        # METHOD 18: Re-find button and click
        try:
            logger.info("METHOD 18: Re-find button and click")
            fresh_button = self.driver.find_element(By.XPATH, "//div[@aria-label='Post'][@role='button']")
            self.driver.execute_script("arguments[0].click();", fresh_button)
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 18 failed: {e}")
        
        # METHOD 19: Keyboard shortcut (Ctrl+Enter)
        try:
            logger.info("METHOD 19: Send Ctrl+Enter to page")
            dialog = self.driver.find_element(By.XPATH, "//div[@role='dialog']")
            actions = ActionChains(self.driver)
            actions.move_to_element(dialog)
            actions.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()
            time.sleep(3)
            if self._check_post_submitted():
                return True
        except Exception as e:
            logger.debug(f"Method 19 failed: {e}")
        
        # METHOD 20: Try all Post button selectors
        try:
            logger.info("METHOD 20: Try alternative Post button selectors")
            alt_selectors = [
                "//div[@role='button'][.//span[text()='Post']]",
                "//span[text()='Post']/ancestor::div[@role='button']",
                "//*[@role='button']//span[text()='Post']/..",
            ]
            
            for selector in alt_selectors:
                try:
                    btn = self.driver.find_element(By.XPATH, selector)
                    if btn and btn.is_displayed():
                        self.driver.execute_script("arguments[0].click();", btn)
                        time.sleep(3)
                        if self._check_post_submitted():
                            return True
                except:
                    continue
        except Exception as e:
            logger.debug(f"Method 20 failed: {e}")
        
        logger.error("ALL 20 METHODS FAILED!")
        return False
    
    def _check_post_submitted(self):
        """Check if post was submitted successfully"""
        try:
            # Check if dialog is gone
            try:
                dialog = self.driver.find_element(By.XPATH, "//div[@role='dialog']")
                if not dialog.is_displayed():
                    logger.info("Dialog not visible - post likely submitted")
                    return True
            except NoSuchElementException:
                logger.info("Dialog not found - post likely submitted")
                return True
            
            # Check if Post button is gone
            try:
                post_btn = self.driver.find_element(By.XPATH, "//div[@aria-label='Post'][@role='button']")
                if not post_btn.is_displayed():
                    logger.info("Post button not visible - likely submitted")
                    return True
            except NoSuchElementException:
                logger.info("Post button not found - likely submitted")
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Check post submitted error: {e}")
            return False
    
    def _wait_for_post_button_enabled(self, timeout=30):
        """Wait for Post button to be enabled"""
        logger.info(f"Waiting up to {timeout}s for Post button to be enabled...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                post_button_selectors = [
                    "//div[@aria-label='Post'][@role='button']",
                    "//div[@role='button'][.//span[text()='Post']]",
                    "//span[text()='Post']/ancestor::div[@role='button']",
                ]
                
                for selector in post_button_selectors:
                    try:
                        btn = self.driver.find_element(By.XPATH, selector)
                        if btn and btn.is_displayed():
                            aria_disabled = btn.get_attribute("aria-disabled")
                            
                            if aria_disabled != "true":
                                logger.info("Post button is ENABLED!")
                                return btn
                    except:
                        continue
                
            except Exception as e:
                logger.debug(f"Error checking button state: {e}")
            
            time.sleep(1)
        
        logger.warning(f"Post button did not become enabled within {timeout}s")
        return None
    
    def create_image_post(self):
        """Create a new post with a stock image from API"""
        try:
            logger.info("CREATING NEW IMAGE POST WITH STOCK PHOTO")
            
            # Fetch image from API
            logger.info("Fetching stock image from API...")
            image_path, caption = self.image_fetcher.get_random_image()
            
            if not image_path:
                logger.error("Could not fetch image from API")
                return False
            
            logger.info(f"Image downloaded to {image_path}")
            logger.info(f"Caption: {caption}")
            
            # Scroll to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.random_delay(2, 3)
            
            # Find post creation box
            post_box_selectors = [
                (By.XPATH, "//span[contains(text(), \"What's on your mind\")]"),
                (By.XPATH, "//span[contains(text(), 'What')]"),
                (By.CSS_SELECTOR, "[aria-label*='Create a post']"),
            ]
            
            post_box = None
            for by, selector in post_box_selectors:
                try:
                    wait = WebDriverWait(self.driver, 5)
                    post_box = wait.until(EC.element_to_be_clickable((by, selector)))
                    if post_box:
                        logger.info("Found post box")
                        break
                except:
                    continue
            
            if not post_box:
                logger.error("Could not find post creation box")
                self.take_screenshot("post_creation_failed.png")
                return False
            
            # Open dialog
            self.driver.execute_script("arguments[0].scrollIntoView(true);", post_box)
            self.random_delay(1, 2)
            
            try:
                post_box.click()
            except:
                self.driver.execute_script("arguments[0].click();", post_box)
            
            logger.info("Dialog opened")
            self.random_delay(2, 4)
            
            # Find Photo/Video button
            photo_button_selectors = [
                (By.XPATH, "//span[contains(text(), 'Photo/video')]"),
                (By.XPATH, "//div[@aria-label='Photo/video']"),
                (By.XPATH, "//span[contains(text(), 'Photo')]"),
            ]
            
            photo_button = None
            for by, selector in photo_button_selectors:
                try:
                    wait = WebDriverWait(self.driver, 5)
                    photo_button = wait.until(EC.element_to_be_clickable((by, selector)))
                    if photo_button:
                        logger.info("Found Photo/Video button")
                        break
                except:
                    continue
            
            if not photo_button:
                logger.error("Could not find Photo/Video button")
                return False
            
            # Click Photo/Video button
            try:
                photo_button.click()
            except:
                self.driver.execute_script("arguments[0].click();", photo_button)
            
            self.random_delay(2, 3)
            
            # Find file input
            file_input = None
            try:
                file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                if file_inputs:
                    file_input = file_inputs[-1]
                    logger.info("Found file input")
            except:
                pass
            
            if not file_input:
                logger.error("Could not find file input")
                return False
            
            # Upload image
            absolute_path = os.path.abspath(image_path)
            logger.info(f"Uploading image: {absolute_path}")
            
            if not os.path.exists(absolute_path):
                logger.error(f"Image file does not exist: {absolute_path}")
                return False
            
            file_input.send_keys(absolute_path)
            logger.info("Image path sent to file input")
            
            # Wait for upload
            logger.info("Waiting for image to upload...")
            self.random_delay(5, 8)
            
            # Add caption
            if caption:
                logger.info("Adding caption...")
                
                text_input_selectors = [
                    (By.XPATH, "//div[@role='textbox' and @contenteditable='true']"),
                    (By.CSS_SELECTOR, "div[role='textbox'][contenteditable='true']"),
                ]
                
                text_input = None
                for by, selector in text_input_selectors:
                    try:
                        elements = self.driver.find_elements(by, selector)
                        for elem in reversed(elements):
                            if elem.is_displayed() and elem.is_enabled():
                                text_input = elem
                                break
                        if text_input:
                            break
                    except:
                        continue
                
                if text_input:
                    try:
                        text_input.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", text_input)
                    
                    self.random_delay(1, 2)
                    
                    # Use JavaScript to set text
                    self._type_text_with_js(text_input, caption)
                    logger.info("Caption added")
                    self.random_delay(2, 3)
            
            # Wait for Post button to be enabled
            post_button = self._wait_for_post_button_enabled(timeout=30)
            
            if not post_button:
                # Try to find it anyway
                post_button_selectors = [
                    "//div[@aria-label='Post'][@role='button']",
                    "//div[@role='button'][.//span[text()='Post']]",
                ]
                
                for selector in post_button_selectors:
                    try:
                        post_button = self.driver.find_element(By.XPATH, selector)
                        if post_button and post_button.is_displayed():
                            break
                    except:
                        continue
            
            if not post_button:
                logger.error("Could not find Post button")
                self.take_screenshot("post_button_not_found.png")
                return False
            
            # Take screenshot before clicking
            self.take_screenshot("before_post_click.png")
            
            # Try all click methods
            click_success = self._click_post_button_all_methods(post_button)
            
            if not click_success:
                logger.error("ALL CLICK METHODS FAILED!")
                self.take_screenshot("all_click_methods_failed.png")
                return False
            
            # Wait for post to publish
            self.random_delay(5, 7)
            
            # Final verification
            if self._check_post_submitted():
                logger.info("SUCCESS: IMAGE POST CREATED AND PUBLISHED!")
                self.take_screenshot("image_post_success.png")
                return True
            else:
                logger.error("Post may not have been published")
                self.take_screenshot("post_verification_failed.png")
                return False
            
        except Exception as e:
            logger.error(f"Error creating image post: {str(e)}")
            self.take_screenshot("image_post_error.png")
            return False
    
    def take_screenshot(self, filename="screenshot.png"):
        """Save a screenshot to the screenshots folder"""
        try:
            screenshot_path = self.screenshots_folder / filename
            self.driver.save_screenshot(str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
    
    def close_browser(self):
        """Close the browser and clean up"""
        try:
            if self.driver:
                logger.info("Closing browser...")
                self.driver.quit()
                logger.info("Browser closed successfully")
            
            self.image_fetcher.cleanup()
            
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")