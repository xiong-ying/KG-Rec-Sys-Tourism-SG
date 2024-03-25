import re
from bs4 import BeautifulSoup
import time
import pandas as pd
import os

# self-defined package
import MySpider
import PoiInfoScraper

class ReviewScraper(object):
    
    def __init__(self):

        poi_info_scraper = PoiInfoScraper.PoiInfolScraper()
        self.poi_info_df = poi_info_scraper.get_poi_info()

        self.filename = "output/reviews.csv"

        self.review_df = pd.DataFrame()
        

    def get_review(self):

        # if the file exist, import from file
        if os.path.exists(self.filename):
            # Read the CSV file into a pandas DataFrame
            self.review_df = pd.read_csv(self.filename)

            print(f"\nLoaded {len(self.review_df)} reviews from {self.filename}")
            return self.review_df
        
        review_list = []

        poi_counter = 0

        num_poi = self.poi_info_df.shape[0]
        #num_poi = min(5, self.poi_info_df.shape[0])  # test with 5 poi

        # for each poi
        for index, row in self.poi_info_df.iterrows():
        #for index, row in self.poi_info_df.head(num_poi).iterrows():

            poi_counter += 1

            poi_id = row["id"]
            poi_url = row["url"]
            num_reviews = row["numReviews"]
            num_page = int(num_reviews / 10) + 1

            # get all urls of review for this poi
            review_urls = []
            review_urls_parts = poi_url.split('-Reviews-')
            for page in range(0, num_page):
                new_review_url = review_urls_parts[0]+'-Reviews-or{}-'.format(10 * page)+review_urls_parts[1]
                review_urls.append(new_review_url)

            total_num = len(review_urls)
            counter = 0

            #for url in review_urls:
            for url in review_urls:

                counter += 1
                print(f"\nprogress: poi - {poi_counter}/{num_poi}; review - {counter}/{total_num}")

                try:
                    
                    # Initialize spider
                    review_spider = MySpider.Spider()
                    review_spider.url = url

                    # Get the html content
                    html = review_spider.get_html()

                    # check if successfully get the html content, if not skip this loop
                    if "<!DOCTYPE html>" not in html:
                        continue

                    soup = BeautifulSoup(html, 'html.parser')

                    # scrap review
                    reviews = soup.find_all('div', class_='_c', attrs={'data-automation': 'reviewCard'})

                    for review in reviews:

                        # dictionary to store info for single poi
                        review_info = {}

                        review_info['poiID'] = poi_id
                        print("\npoiID:", review_info['poiID'])

                        # display name
                        #review_info['username'] = review.find('div', class_='mwPje f M k').find('span', class_='biGQs _P fiohW fOtGX').a.text.strip() if review.find('div', class_='mwPje f M k') else ''

                        review_info['username'] = review.find('div', class_='tknvo ccudK Rb I o').a['href'].strip().replace('/Profile/', '') if review.find('div', class_='tknvo ccudK Rb I o') else ''
                        print("username:", review_info['username'])

                        review_info['location'] = review.find('div', class_='biGQs _P pZUbB osNWb').span.text.strip() if "contribution" not in review.find('div', class_='biGQs _P pZUbB osNWb').span.text.strip() else ''
                        print("location:", review_info['location'])

                        review_info['review_id'] = re.search(r'r(\d+)', review.find('div', class_='biGQs _P fiohW qWPrE ncFvv fOtGX').a['href']).group(1) if review.find('div', class_='biGQs _P fiohW qWPrE ncFvv fOtGX') else ''
                        print("review_id:", review_info['review_id'])

                        review_info['title'] = review.find('div', class_='biGQs _P fiohW qWPrE ncFvv fOtGX').find('span', class_='yCeTE').text.strip() if review.find('div', class_='biGQs _P fiohW qWPrE ncFvv fOtGX') else ''
                        print("title:", review_info['title'])

                        review_info['date'] = review.find('div', class_='biGQs _P pZUbB ncFvv osNWb').text.strip().replace('Written ', '') if review.find('div', class_='biGQs _P pZUbB ncFvv osNWb') else ''
                        print("date:", review_info['date'])

                        review_info['rating'] = soup.find('svg', class_='UctUV d H0')['aria-label'].replace(' of 5 bubbles', '') if soup.find('svg', class_='UctUV d H0') else ''
                        print("rating:", review_info['rating'])

                        review_info['user_group'] = review.find('div', class_='RpeCd').text.split('•')[-1].strip() if '•' in review.find('div', class_='RpeCd').text.strip() else ''
                        print("user_group:", review_info['user_group'])

                        review_info['content'] = review.find('div', class_='biGQs _P pZUbB KxBGd').find('span', class_='yCeTE').text.strip() if review.find('div', class_='biGQs _P pZUbB KxBGd') else ''
                        print("content:", review_info['content'])

                        review_info['review_url'] = "https://www.tripadvisor.com" + review.find('div', class_='biGQs _P fiohW qWPrE ncFvv fOtGX').a['href'] if review.find('div', class_='biGQs _P fiohW qWPrE ncFvv fOtGX') else ''
                        print("review_url:", review_info['review_url'])

                        review_list.append(review_info)

                        # print result
                        print("Scraped review successfully!")
                
                except Exception as e:
                    print("Error scraping review from URL:", url)
                    print(e)

        # Convert poi info dictionary to DataFrame
        self.review_df = pd.DataFrame(review_list)

        # Save to .csv
        self.review_df.to_csv(self.filename, index=False)

        return self.review_df
    


# MAIN
if __name__ == '__main__':

    # scrap review for each url
    start=time.time()

    scraper = ReviewScraper()
    review_df = scraper.get_review()

    end=time.time()

    # display execution time
    print('\nTotal Duration: %.2f s'%(end-start))


    # TODO: scrap review for each poi

    # TODO: IP proxy

