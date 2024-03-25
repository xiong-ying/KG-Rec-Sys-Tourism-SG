
# 01 TripAdvisor Scraper
This module contains the code for scraping tourist information from TripAdvisor. 

## Introduction

It consists of several Python scripts:

### 1.MySpider.py

This script defines a Spider class that is responsible for fetching HTML content from URLs using both standard HTTP requests and Selenium WebDriver. It utilizes a random User-Agent for each request to mimic different browsers. Additionally, it provides functionality to write the HTML content to files for debugging purposes.

### 2.PoiUrlScraper.py

This script contains the PoiUrlScraper class, which is used to extract URLs of points of interest (POIs) from TripAdvisor's listing pages. It retrieves the listing pages for all attractions in Singapore and parses the HTML content to extract the URLs of individual POI detail pages. These URLs are then stored in a text file for subsequent processing.

### 3.PoiInfoScraper.py

The PoiInfoScraper class defined in this script is responsible for scraping detailed information about each POI from its respective detail page. It utilizes the Spider class to fetch the HTML content of each page and parses it to extract information such as the POI's name, type, opening hours, description, duration, price, address, region, average rating, and number of reviews. The extracted data is then stored in a CSV file.

This script relies on the output text file generated by PoiUrlScraper.py.

### 4.ReviewScraper.py

This script implements the ReviewScraper class, which is used to scrape reviews for each POI from TripAdvisor. It first retrieves the URLs of reviews for each POI and then extracts relevant information such as the reviewer's username, location, review title, date, rating, user group, and review content. The scraped data is saved in a CSV file for further analysis.

Each script contains detailed comments explaining the purpose of the code and how it operates.

This script relies on the output csv file generated by PoiInfoScraper.py.

## Usage

To use the TripAdvisor scraper module, follow these steps:

1. Ensure that Python and the required dependencies (such as Selenium and BeautifulSoup) are installed.
2. Run the desired script (MySpider.py, PoiUrlScraper.py, PoiInfoScraper.py, ReviewScraper.py).
3. Follow the instructions provided in each script's comments to customize the scraping process or handle any errors.

## Dependencies

- Python 3.x
- Selenium
- BeautifulSoup
- Requests
- Pandas
- Fake User-Agent

## Contributors

Xiong Ying

## License

This project is licensed under the [MIT License](LICENSE).