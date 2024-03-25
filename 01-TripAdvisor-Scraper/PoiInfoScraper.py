import re
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
import random
import csv

# self-defined package
import MySpider
import PoiUrlScraper


# get all the info of one poi from the detail page
class PoiInfolScraper(object):

    def __init__(self):

        poi_url_scraper = PoiUrlScraper.PoiUrlScraper()
        self.urls = poi_url_scraper.get_poi_urls()

        self.filename = "output/poi_info.csv"

        self.poi_info_df = pd.DataFrame()
        

    def get_poi_info(self):

        # if the file exist, import from file
        if os.path.exists(self.filename):
            # Read the CSV file containing the URLs into a pandas DataFrame
            self.poi_info_df = pd.read_csv(self.filename)

            print(f"\nLoaded {len(self.poi_info_df)} POIs from {self.filename}")
            return self.poi_info_df
        

        # list to store info for poi
        poi_info_list = []

        failed_urls = []

        total_num = len(self.urls)
        counter = 0

        for url in self.urls:

            counter += 1
            print(f"\nprogress: {counter}/{total_num}")


            try:
                # Initialize spider
                poi_spider = MySpider.Spider()
                poi_spider.url = url

                # Get the html content
                html = poi_spider.get_html()

                # check if successfully get the html content, if not skip this loop
                if "<!DOCTYPE html>" not in html:
                    failed_urls.append(url)
                    print("Appended URL to failed_urls list.")
                    continue

                # Parse the html content
                soup = BeautifulSoup(html, 'html.parser')

                # dictionary to store info for single poi
                poi_info = {}

                # Extract the ID with regular expression search and conditional expression
                poi_info['id'] = re.search(r'd(\d+)-', url).group(1) if re.search(r'd(\d+)-', url) else None
                print("id:", poi_info['id']) if poi_info['id'] else print("poi ID not found in the URL")

                poi_info['url'] = url
                print("url:", poi_info['url'])

                # Scrap poi info data with print out
                poi_info['name'] = soup.find('h1', class_='biGQs _P fiohW eIegw').text.strip() if soup.find('h1', class_='biGQs _P fiohW eIegw') else ''
                print("name:", poi_info['name'])

                poi_info['type'] = ', '.join(span.text.strip() for span in soup.find_all('span', class_='eojVo')) if soup.find('span', class_='eojVo') else ''
                print("type:", poi_info['type'])

                poi_info['openingHours'] = soup.find('span', class_='EFKKt').text.strip() if soup.find('span', class_='EFKKt') else ''
                print("openingHours:", poi_info['openingHours'])

                poi_info['description'] = soup.find('div', class_='afQPz SyjMH ttWhi WRRwX Gg A').find('span', class_='JguWG').text.strip() if soup.find('div', class_='afQPz SyjMH ttWhi WRRwX Gg A').find('span', class_='JguWG') else ''
                print("description:", poi_info['description'])

                poi_info['duration'] = soup.find('div', class_='nvXSy f _Y Q2').find('div', class_='biGQs _P pZUbB KxBGd').text.strip().replace('Duration: ', '') if soup.find('div', class_='nvXSy f _Y Q2') else ''
                print("duration:", poi_info['duration'])

                poi_info['price'] = soup.find('div', class_='MQPqk').find('div', class_='biGQs _P fiohW uuBRH').text.strip().split()[1].strip('$') if soup.find('div', class_='MQPqk').find('div', class_='biGQs _P fiohW uuBRH') else ''
                print("price:", poi_info['price'])

                poi_info['address'] = soup.find('div', class_='wgNTK').find('div', class_='MJ').find('span', class_='biGQs _P XWJSj Wb').text.strip() if soup.find('div', class_='wgNTK').find('div', class_='MJ') else ''
                print("address:", poi_info['address'])

                poi_info['region'] = soup.find('div', class_='wgNTK').find('div', class_='MK').find('div', class_='biGQs _P fiohW fOtGX').text.split(": ")[1].strip() if soup.find('div', class_='wgNTK').find('div', class_='MK') else ''
                print("region:", poi_info['region'])

                poi_info['avgRating'] = soup.find('div', class_='biGQs _P fiohW hzzSG uuBRH').text.strip() if soup.find('div', class_='biGQs _P fiohW hzzSG uuBRH') else ''
                print("avgRating:", poi_info['avgRating'])

                poi_info['numReviews'] = soup.find('div', class_='jVDab o W f u w GOdjs').find('span', class_='biGQs _P pZUbB KxBGd').text.strip().split()[0].replace(',', '') if soup.find('div', class_='jVDab o W f u w GOdjs') else 0
                print("numReviews:", poi_info['numReviews'])

                num_reviews_breakdown = soup.find('div', class_='yFKLG').find('div', class_='_S wSSLS').find_all('div', class_='biGQs _P pZUbB osNWb') if soup.find('div', class_='yFKLG') else []
                poi_info['numReviews_5'] = num_reviews_breakdown[0].text.strip().replace(',', '') if num_reviews_breakdown else 0
                print("numReviews_5:", poi_info['numReviews_5'])

                poi_info['numReviews_4'] = num_reviews_breakdown[1].text.strip().replace(',', '') if len(num_reviews_breakdown) > 1 else 0
                print("numReviews_4:", poi_info['numReviews_4'])

                poi_info['numReviews_3'] = num_reviews_breakdown[2].text.strip().replace(',', '') if len(num_reviews_breakdown) > 2 else 0
                print("numReviews_3:", poi_info['numReviews_3'])

                poi_info['numReviews_2'] = num_reviews_breakdown[3].text.strip().replace(',', '') if len(num_reviews_breakdown) > 3 else 0
                print("numReviews_2:", poi_info['numReviews_2'])

                poi_info['numReviews_1'] = num_reviews_breakdown[4].text.strip().replace(',', '') if len(num_reviews_breakdown) > 4 else 0
                print("numReviews_1:", poi_info['numReviews_1'])

                # append to list
                poi_info_list.append(poi_info)

                # print result
                print("Scraped POI info successfully!")

            except Exception as e:
                print("Error scraping POI info from URL:", url)

                failed_urls.append(url)
                print("Appended URL to failed_urls list.")

                print(e)

        print(f"\n{len(failed_urls)} urls failed: {failed_urls}")

        # save the failed poi url list to .txt file for subsequent processing
        file_failed_urls = "output/poi_urls_failed.txt"
        with open(file_failed_urls, 'w') as file:
            for url in failed_urls:
                file.write(url + '\n')

        # Convert poi info dictionary to DataFrame
        self.poi_info_df = pd.DataFrame(poi_info_list)

        # Save to .csv
        self.poi_info_df.to_csv(self.filename, index=False)

        return self.poi_info_df

        

# MAIN
if __name__ == '__main__':

    # scrap information in POI's url
    start=time.time()

    scraper = PoiInfolScraper()
    poi_info_df = scraper.get_poi_info()

    end=time.time()

    # display execution time
    print('\nTotal Duration: %.2f s'%(end-start))