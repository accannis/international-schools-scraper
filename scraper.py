from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import logging
import sys
import subprocess
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Known Italian cities and their URLs, along with known school names
ITALIAN_CITIES = {
    'Bergamo': {
        'url': 'https://www.international-schools-database.com/in/bergamo',
        'known_schools': ['International School of Bergamo']
    },
    'Bologna': {
        'url': 'https://www.international-schools-database.com/in/bologna',
        'known_schools': ['International School of Bologna', 'Kinder International School Bologna']
    },
    'Brescia': {
        'url': 'https://www.international-schools-database.com/in/brescia',
        'known_schools': []
    },
    'Brindisi': {
        'url': 'https://www.international-schools-database.com/in/brindisi',
        'known_schools': []
    },
    'Como': {
        'url': 'https://www.international-schools-database.com/in/como',
        'known_schools': []
    },
    'Ferrara': {
        'url': 'https://www.international-schools-database.com/in/ferrara',
        'known_schools': []
    },
    'Florence': {
        'url': 'https://www.international-schools-database.com/in/florence',
        'known_schools': []
    },
    'Genoa': {
        'url': 'https://www.international-schools-database.com/in/genoa',
        'known_schools': []
    },
    'Lanciano': {
        'url': 'https://www.international-schools-database.com/in/lanciano',
        'known_schools': []
    },
    'Lucca': {
        'url': 'https://www.international-schools-database.com/in/lucca',
        'known_schools': []
    },
    'Milan': {
        'url': 'https://www.international-schools-database.com/in/milan',
        'known_schools': []
    },
    'Modena': {
        'url': 'https://www.international-schools-database.com/in/modena',
        'known_schools': []
    },
    'Naples': {
        'url': 'https://www.international-schools-database.com/in/naples',
        'known_schools': []
    },
    'Padua': {
        'url': 'https://www.international-schools-database.com/in/padua',
        'known_schools': []
    },
    'Palermo': {
        'url': 'https://www.international-schools-database.com/in/palermo',
        'known_schools': []
    },
    'Rimini': {
        'url': 'https://www.international-schools-database.com/in/rimini',
        'known_schools': []
    },
    'Rome': {
        'url': 'https://www.international-schools-database.com/in/rome',
        'known_schools': []
    },
    'Siena': {
        'url': 'https://www.international-schools-database.com/in/siena',
        'known_schools': []
    },
    'Trieste': {
        'url': 'https://www.international-schools-database.com/in/trieste',
        'known_schools': []
    },
    'Turin': {
        'url': 'https://www.international-schools-database.com/in/turin',
        'known_schools': []
    },
    'Udine': {
        'url': 'https://www.international-schools-database.com/in/udine',
        'known_schools': []
    },
    'Varese': {
        'url': 'https://www.international-schools-database.com/in/varese',
        'known_schools': []
    },
    'Venice': {
        'url': 'https://www.international-schools-database.com/in/venice',
        'known_schools': []
    },
    'Verona': {
        'url': 'https://www.international-schools-database.com/in/verona',
        'known_schools': []
    },
    'Vicenza': {
        'url': 'https://www.international-schools-database.com/in/vicenza',
        'known_schools': []
    },
    'Viterbo': {
        'url': 'https://www.international-schools-database.com/in/viterbo',
        'known_schools': []
    }
}

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    try:
        # Check if Chrome is installed
        chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        if not os.path.exists(chrome_path):
            logging.error("Google Chrome is not installed in the default location")
            sys.exit(1)

        # Get Chrome version
        chrome_version = subprocess.check_output([chrome_path, '--version']).decode().strip().split()[-1]
        logging.info(f"Chrome version: {chrome_version}")

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        logging.error(f"Failed to set up Chrome driver: {e}")
        sys.exit(1)

def wait_and_find_element(driver, by, value, timeout=10):
    """Wait for an element to be present and return it."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return driver.find_element(by, value)
    except TimeoutException:
        logging.warning(f"Timeout waiting for element: {value}")
        return None
    except Exception as e:
        logging.warning(f"Error finding element {value}: {e}")
        return None

def wait_and_find_elements(driver, by, value, timeout=10):
    """Wait for elements to be present and return them."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return driver.find_elements(by, value)
    except TimeoutException:
        logging.warning(f"Timeout waiting for elements: {value}")
        return []
    except Exception as e:
        logging.warning(f"Error finding elements {value}: {e}")
        return []

def get_schools_in_city(driver, city, city_info, coordinates=None):
    """Get all schools in a given city."""
    try:
        url = city_info['url']
        known_schools = city_info['known_schools']
        
        logging.info(f"Fetching URL for {city}: {url}")
        driver.get(url)
        time.sleep(8)  # Wait for page load
        
        schools = []
        found_school_names = set()  # Keep track of schools we've already found
        
        def add_school(school_data):
            """Helper to add a school if it's not a duplicate"""
            if 'name' in school_data and school_data['name'] not in found_school_names:
                # Add coordinates if we have them
                if coordinates and school_data['name'] in coordinates:
                    logging.info(f"Found coordinates for {school_data['name']}: {coordinates[school_data['name']]}")
                    school_data.update(coordinates[school_data['name']])
                else:
                    logging.warning(f"No coordinates found for {school_data['name']}")
                    if coordinates:
                        logging.info(f"Available coordinates: {coordinates}")
                
                found_school_names.add(school_data['name'])
                schools.append(school_data)
                logging.info(f"Added school '{school_data['name']}' from {city} with fields: {school_data}")
            else:
                logging.debug(f"Skipping duplicate school: {school_data.get('name', 'Unknown')}")
        
        # Try to find schools by class first
        logging.info(f"Looking for schools with school-row class in {city}")
        
        # Find the main schools section (before "Other international schools nearby")
        try:
            # First try to find the "Other schools" heading
            other_schools_heading = None
            try:
                other_schools_heading = driver.find_element(By.XPATH, "//h2[contains(text(), 'Other international schools nearby')]")
                logging.info("Found 'Other international schools nearby' section")
            except NoSuchElementException:
                logging.info("No 'Other international schools nearby' section found")
            
            # Get all school rows
            school_rows = driver.find_elements(By.CLASS_NAME, 'school-row')
            
            for row in school_rows:
                # If we found the "Other schools" heading and this row comes after it, skip it
                if other_schools_heading and row.location['y'] > other_schools_heading.location['y']:
                    logging.info("Skipping school in 'Other schools nearby' section")
                    continue
                
                try:
                    school_data = {'city': city}
                    
                    # Get URL directly from the school-row div
                    school_data['url'] = row.get_attribute('href')
                    
                    # Try to find school name in h2, h3, or .school-name
                    for selector in ['h2', 'h3', '.school-name']:
                        try:
                            name_elem = row.find_element(By.CSS_SELECTOR, selector)
                            school_data['name'] = name_elem.text.strip()
                            break
                        except NoSuchElementException:
                            continue
                    
                    if 'name' in school_data:
                        add_school(school_data)
                    
                except Exception as e:
                    logging.warning(f"Error processing school row: {e}")
                    continue
            
            logging.info(f"Found {len(schools)} schools in {city}")
            return schools
            
        except Exception as e:
            logging.error(f"Error finding schools by class: {e}")
            import traceback
            logging.error(traceback.format_exc())
        
        # First, try to get coordinates from the map
        logging.info("Looking for school coordinates in map")
        try:
            # Wait for map to be present
            time.sleep(2)  # Give map a moment to load
            map_element = wait_and_find_element(driver, By.CLASS_NAME, "centered-map")
            logging.info("Found map element")
            
            # Try multiple selectors for map pins
            pin_selectors = [
                ".leaflet-marker-icon",  # Leaflet map markers
                "[data-lat][data-lng]",  # Elements with direct lat/lng data
                ".map-marker",  # Common marker class
                ".pin"  # Another common marker class
            ]
            
            map_pins = []
            for selector in pin_selectors:
                pins = map_element.find_elements(By.CSS_SELECTOR, selector)
                if pins:
                    logging.info(f"Found {len(pins)} pins using selector: {selector}")
                    map_pins.extend(pins)
                    break
            
            if not map_pins:
                # Try to get the map's HTML content for debugging
                map_html = map_element.get_attribute('innerHTML')
                logging.info(f"Map HTML content: {map_html[:500]}...")  # Log first 500 chars
            
            for pin in map_pins:
                try:
                    # Try different ways to get school name
                    school_name = None
                    for attr in ['data-name', 'title', 'alt', 'aria-label']:
                        school_name = pin.get_attribute(attr)
                        if school_name:
                            break
                    
                    # Try different ways to get coordinates
                    lat = pin.get_attribute('data-lat')
                    lng = pin.get_attribute('data-lng')
                    
                    # If no direct lat/lng, try parsing from other attributes
                    if not (lat and lng):
                        data_props = pin.get_attribute('data-props')
                        if data_props:
                            try:
                                import json
                                props = json.loads(data_props)
                                lat = props.get('lat') or props.get('latitude')
                                lng = props.get('lng') or props.get('longitude')
                            except:
                                pass
                    
                    if school_name and lat and lng:
                        school_coordinates[school_name.strip()] = {
                            'latitude': lat,
                            'longitude': lng
                        }
                        logging.info(f"Found coordinates for '{school_name}': {lat}, {lng}")
                    else:
                        logging.debug(f"Pin data - Name: {school_name}, Lat: {lat}, Lng: {lng}")
                        # Log all attributes for debugging
                        for attr in pin.get_property('attributes'):
                            logging.debug(f"Pin attribute {attr.name}: {attr.value}")
                            
                except Exception as e:
                    logging.warning(f"Error extracting coordinates from pin: {e}")
                    
        except Exception as e:
            logging.warning(f"Error finding map or pins: {e}")
            import traceback
            logging.debug(f"Map extraction error traceback: {traceback.format_exc()}")
        
        # Try to find schools by class first
        logging.info(f"Looking for schools with school-row class in {city}")
        
        # Find the main schools section (before "Other international schools nearby")
        try:
            # First try to find the "Other schools" heading
            other_schools_heading = None
            try:
                other_schools_heading = driver.find_element(By.XPATH, "//h2[contains(text(), 'Other international schools nearby')]")
                logging.info("Found 'Other international schools nearby' section")
            except NoSuchElementException:
                logging.info("No 'Other international schools nearby' section found")
            
            # Get all school rows
            school_rows = driver.find_elements(By.CLASS_NAME, 'school-row')
            
            for row in school_rows:
                # If we found the "Other schools" heading and this row comes after it, skip it
                if other_schools_heading and row.location['y'] > other_schools_heading.location['y']:
                    logging.info("Skipping school in 'Other schools nearby' section")
                    continue
                
                try:
                    school_data = {'city': city}
                    
                    # Try to find school name in h2, h3, or .school-name
                    for selector in ['h2', 'h3', '.school-name']:
                        try:
                            name_elem = row.find_element(By.CSS_SELECTOR, selector)
                            school_data['name'] = name_elem.text.strip()
                            
                            # Try to get URL from the name element or its parent
                            try:
                                url_elem = name_elem
                                if not url_elem.tag_name == 'a':
                                    url_elem = name_elem.find_element(By.XPATH, './ancestor::a[1]')
                                school_data['url'] = url_elem.get_attribute('href')
                            except NoSuchElementException:
                                pass
                            break
                        except NoSuchElementException:
                            continue
                    
                    if 'name' in school_data:
                        add_school(school_data)
                    
                except Exception as e:
                    logging.warning(f"Error processing school row: {e}")
                    continue
            
            logging.info(f"Found {len(schools)} schools in {city}")
            return schools
            
        except Exception as e:
            logging.error(f"Error finding schools by class: {e}")
            import traceback
            logging.error(traceback.format_exc())
        
        # If we didn't find all known schools, look for them specifically
        if known_schools:
            for school_name in known_schools:
                if school_name not in found_school_names:  # Only look for schools we haven't found yet
                    logging.info(f"Looking for known school in {city}: {school_name}")
                    try:
                        # Try to find exact school name
                        xpath = f"//*[contains(text(), '{school_name}')]"
                        elements = driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            try:
                                # Get the parent element that might contain more info
                                parent = element
                                for _ in range(3):  # Look up to 3 levels up
                                    if parent.get_attribute('class') and any(x in parent.get_attribute('class').lower() for x in ['school', 'listing', 'item']):
                                        break
                                    parent = parent.find_element(By.XPATH, '..')
                                
                                school_data = {
                                    'city': city,
                                    'name': school_name
                                }
                                
                                # Try to get URL
                                try:
                                    url_elem = parent.find_element(By.XPATH, './/a[contains(@href, "school")]')
                                    school_data['url'] = url_elem.get_attribute('href')
                                except NoSuchElementException:
                                    pass
                                
                                # Try to get additional information
                                try:
                                    info_elements = parent.find_elements(By.CSS_SELECTOR, '.school-info-item, .info-item, .details, [itemprop="description"]')
                                    for info_elem in info_elements:
                                        text = info_elem.text.strip()
                                        if ':' in text:
                                            label, value = text.split(':', 1)
                                            label = label.strip().lower()
                                            value = value.strip()
                                            if label and value:
                                                school_data[label] = value
                                except Exception as e:
                                    logging.debug(f"Error getting additional info: {e}")
                                
                                add_school(school_data)
                                break  # Found the school, no need to process more elements
                                
                            except Exception as e:
                                logging.warning(f"Error processing known school '{school_name}' in {city}: {e}")
                                continue
                    except Exception as e:
                        logging.warning(f"Error searching for known school '{school_name}' in {city}: {e}")
        
        # If we still haven't found all known schools, try other selectors
        if len(schools) < len(known_schools):
            logging.info(f"Still missing some known schools in {city}, trying other selectors")
            selectors = [
                '.school-row',  # Primary selector - exact match for school rows
                'div[class*="school-row"]',  # Backup for school row with additional classes
                '.school-list-item, .school-card',  # Secondary selectors
                'div[itemtype="http://schema.org/School"]',  # Schema.org school type
                'div[class*="school-listing"]',  # Common pattern for school listings
                'div.listing-item:has(a[href*="school"])',  # Listings with school links
                'a[href*="/in/"][href*="school"]:not([href*="top-schools"])'  # Direct school links, excluding "top schools" pages
            ]
            
            school_elements = []
            for selector in selectors:
                logging.info(f"Trying selector '{selector}' in {city}")
                elements = wait_and_find_elements(driver, By.CSS_SELECTOR, selector)
                if elements:
                    # Filter out elements that are likely not actual schools
                    filtered_elements = [
                        e for e in elements 
                        if e.text.strip() and  # Must have text
                        not any(x in e.text.lower() for x in ['contact us', 'advertisement', 'top schools'])  # Exclude non-school elements
                    ]
                    if filtered_elements:
                        school_elements = filtered_elements
                        logging.info(f"Found {len(filtered_elements)} school elements with selector '{selector}' in {city}")
                        break
                logging.warning(f"No valid elements found with selector '{selector}' in {city}")
            
            if not school_elements:
                logging.warning(f"Could not find any school elements in {city} with any selector")
                return []
            
            for element in school_elements:
                try:
                    school_data = {'city': city}
                    
                    # Try multiple approaches to get school name and URL
                    name_found = False
                    
                    # Try common name patterns
                    for name_selector in ['h2', 'h3', '.school-name', '.title', '[itemprop="name"]']:
                        try:
                            name_elem = element.find_element(By.CSS_SELECTOR, name_selector)
                            name = name_elem.text.strip()
                            if name and len(name) > 3 and not any(x in name.lower() for x in ['contact', 'advertisement']):
                                school_data['name'] = name
                                name_found = True
                                # Try to get URL from this element or its parent
                                try:
                                    url_elem = name_elem.find_element(By.XPATH, './ancestor::a[1]') if name_elem.tag_name != 'a' else name_elem
                                    school_data['url'] = url_elem.get_attribute('href')
                                except NoSuchElementException:
                                    pass
                            break
                        except NoSuchElementException:
                            continue
                    
                    # If no name found yet, try the element itself if it's a link
                    if not name_found and element.tag_name == 'a':
                        name = element.text.strip()
                        if name and len(name) > 3 and not any(x in name.lower() for x in ['contact', 'advertisement']):
                            school_data['name'] = name
                            school_data['url'] = element.get_attribute('href')
                            name_found = True
                    
                    # Only proceed if we found a valid name
                    if name_found:
                        # Try to get additional information
                        info_selectors = [
                            '.school-info-item, .info-item, .details',
                            '[itemprop="description"]',
                            '.school-details'
                        ]
                        
                        for info_selector in info_selectors:
                            try:
                                info_elements = element.find_elements(By.CSS_SELECTOR, info_selector)
                                for info_elem in info_elements:
                                    try:
                                        # Try structured data first
                                        label = info_elem.find_element(By.CSS_SELECTOR, '.label, .key').text.strip().lower()
                                        value = info_elem.find_element(By.CSS_SELECTOR, '.value, .data').text.strip()
                                        school_data[label] = value
                                    except NoSuchElementException:
                                        # If no structured data, try to parse the text
                                        text = info_elem.text.strip()
                                        if ':' in text:
                                            label, value = text.split(':', 1)
                                            label = label.strip().lower()
                                            value = value.strip()
                                            if label and value:
                                                school_data[label] = value
                            except Exception as e:
                                logging.debug(f"Error getting additional info: {e}")
                                continue
                        
                        add_school(school_data)
            
                except Exception as e:
                    logging.warning(f"Error processing school in {city}: {e}")
                    continue
        
        logging.info(f"Found {len(schools)} schools in {city}")
        return schools
    except Exception as e:
        logging.error(f"Error getting schools in {city}: {e}")
        return []

def save_schools_to_csv(schools, mode='w'):
    """Save schools to CSV file. Mode can be 'w' for write (overwrite) or 'a' for append."""
    if schools:
        df = pd.DataFrame(schools)
        # Ensure consistent column order with required columns first
        columns = ['name', 'city', 'url', 'latitude', 'longitude']
        # Add any additional columns found in the data
        extra_cols = sorted(col for col in df.columns if col not in columns)
        columns.extend(extra_cols)
        
        # Reindex and ensure all required columns exist
        for col in ['latitude', 'longitude']:
            if col not in df.columns:
                df[col] = None
        df = df.reindex(columns=columns)
        
        if mode == 'w':
            df.to_csv('italian_schools.csv', index=False)
        else:
            df.to_csv('italian_schools.csv', mode='a', header=False, index=False)
        logging.info(f"Saved {len(schools)} schools to italian_schools.csv ({mode}) with columns: {', '.join(df.columns)}")

def main():
    logging.info("Starting the scraper...")
    driver = None
    all_schools = []
    first_city = True  # Track if this is the first city
    max_retries = 3
    
    try:
        driver = setup_driver()
        
        # Process all cities
        logging.info(f"Processing {len(ITALIAN_CITIES)} cities")
        for city, city_info in ITALIAN_CITIES.items():
            retry_count = 0
            while retry_count < max_retries:
                try:
                    logging.info(f"\nProcessing {city} (attempt {retry_count + 1})")
                    
                    # Load the page
                    url = city_info['url']
                    logging.info(f"Loading {url}")
                    driver.get(url)
                    time.sleep(5)  # Initial wait for page load
                    
                    # First get all school rows to know what schools we're looking for
                    school_rows = driver.find_elements(By.CLASS_NAME, 'school-row')
                    if not school_rows:
                        logging.warning("No school rows found, retrying...")
                        retry_count += 1
                        time.sleep(5)  # Wait before retry
                        continue
                        
                    school_names = set()
                    
                    # Find the "Other schools" heading
                    other_schools_heading = None
                    try:
                        other_schools_heading = driver.find_element(By.XPATH, "//h2[contains(text(), 'Other international schools nearby')]")
                        logging.info("Found 'Other international schools nearby' section")
                    except NoSuchElementException:
                        logging.info("No 'Other international schools nearby' section found")
                    
                    # Get names of schools in the main section
                    for row in school_rows:
                        # Skip schools in "Other schools nearby" section
                        if other_schools_heading and row.location['y'] > other_schools_heading.location['y']:
                            continue
                            
                        for selector in ['h2', 'h3', '.school-name']:
                            try:
                                name_elem = row.find_element(By.CSS_SELECTOR, selector)
                                school_names.add(name_elem.text.strip())
                                break
                            except NoSuchElementException:
                                continue
                    
                    logging.info(f"Found {len(school_names)} schools in main section: {school_names}")
                    
                    # Get coordinates from map markers, but only for schools we found
                    school_coordinates = {}
                    try:
                        logging.info("Looking for map markers...")
                        markers = driver.find_elements(By.CSS_SELECTOR, "[data-marker-latitude][data-marker-longitude]")
                        for marker in markers:
                            try:
                                lat = marker.get_attribute('data-marker-latitude')
                                lng = marker.get_attribute('data-marker-longitude')
                                name = marker.get_attribute('data-marker-name')
                                if lat and lng and name:
                                    # Remove city name if present
                                    name = name.split(',')[0].strip()
                                    # Only add coordinates if this is a school we found in the main section
                                    if name in school_names:
                                        school_coordinates[name] = {
                                            'latitude': lat,
                                            'longitude': lng
                                        }
                                        logging.info(f"Found coordinates for {name}: {lat}, {lng}")
                                    else:
                                        logging.debug(f"Skipping coordinates for {name} - not in main section")
                            except Exception as e:
                                logging.warning(f"Error extracting marker data: {e}")
                        
                    except Exception as e:
                        logging.error(f"Error getting coordinates: {e}")
                        import traceback
                        logging.error(traceback.format_exc())
                    
                    # Now process the school rows again to create the final data
                    schools = []
                    found_school_names = set()
                    
                    for row in school_rows:
                        # Skip schools in "Other schools nearby" section
                        if other_schools_heading and row.location['y'] > other_schools_heading.location['y']:
                            continue
                            
                        try:
                            school_data = {'city': city}
                            
                            # Get URL directly from the school-row div
                            school_data['url'] = row.get_attribute('href')
                            
                            # Get school name
                            for selector in ['h2', 'h3', '.school-name']:
                                try:
                                    name_elem = row.find_element(By.CSS_SELECTOR, selector)
                                    school_data['name'] = name_elem.text.strip()
                                    break
                                except NoSuchElementException:
                                    continue
                            
                            if 'name' in school_data and school_data['name'] not in found_school_names:
                                # Add coordinates if we have them
                                if school_data['name'] in school_coordinates:
                                    school_data.update(school_coordinates[school_data['name']])
                                    logging.info(f"Added coordinates for {school_data['name']}")
                                
                                found_school_names.add(school_data['name'])
                                schools.append(school_data)
                                logging.info(f"Added school '{school_data['name']}' from {city} with fields: {school_data}")
                            
                        except Exception as e:
                            logging.warning(f"Error processing school row: {e}")
                            continue
                    
                    if schools:
                        # Save schools from this city
                        mode = 'w' if first_city else 'a'  # Write mode for first city, append for others
                        save_schools_to_csv(schools, mode)
                        first_city = False
                        
                        all_schools.extend(schools)
                        logging.info(f"Found and saved {len(schools)} schools in {city}")
                    
                    # If we got here without errors, break the retry loop
                    break
                    
                except Exception as e:
                    logging.error(f"Error processing city {city} (attempt {retry_count + 1}): {e}")
                    import traceback
                    logging.error(traceback.format_exc())
                    retry_count += 1
                    if retry_count < max_retries:
                        logging.info(f"Retrying {city} in 5 seconds...")
                        time.sleep(5)
                    else:
                        logging.error(f"Failed to process {city} after {max_retries} attempts")
                    continue
        
        logging.info(f"\nFinished processing all cities. Total schools found: {len(all_schools)}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        import traceback
        logging.error(traceback.format_exc())
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
