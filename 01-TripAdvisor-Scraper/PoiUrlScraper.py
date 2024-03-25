import os
from bs4 import BeautifulSoup

# self-defined package
import MySpider


# get all the urls of poi detail page in a region, from the listing pages of the region
class PoiUrlScraper(object):
    def __init__(self):

        # listing page for all poi in Singapore
        self.listing_url = 'https://www.tripadvisor.com/Attractions-g294265-Activities-Singapore.html'

        # save result in this file
        self.filename = "output/poi_urls.txt"

        # Total number of POI and pages
        # as of 2024.02.17, 3532 POI, 118 pages in total
        self.num_page=118

        # empty list of POI urls from each listing page url
        self.poi_url_list = []


    # FUNCTION: Get POI's urls from listing page
    def get_poi_urls(self):
        

        # if the .txt file storing all POI urls exists, import urls from file
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                self.poi_url_list = [line.strip() for line in file]

            # return urls loaded from external file
            print(f"\nLoaded {len(self.poi_url_list)} URLs from {self.filename}")
            return self.poi_url_list

        # else, get urls of listing pages in Singapore, based on num_page
        listing_urls = []
        listing_url_parts = self.listing_url.split('-Activities-')
        for page in range(0, self.num_page):
            new_listing_url = listing_url_parts[0]+'-Activities-oa{}-'.format(30 * page)+listing_url_parts[1]
            listing_urls.append(new_listing_url)

        counter = 0
        for listing_url in listing_urls:
            counter += 1
            print(f"\nprogress: {counter}/{self.num_page}")

            # try opening each listing url in the listing url list
            try:

                # initialize spider
                listing_spider = MySpider.Spider()
                listing_spider.url = listing_url

                # get the html content, save in html folder
                html = listing_spider.get_html()
                listing_spider.write_html()

                # get the html content
                soup = BeautifulSoup(html, 'html.parser')

            except:
                print("Cannot get html content from url: ", listing_url)
                continue

            # url in poi title
            # <div class="alPVI eNNhq PgLKC tnGGX"> <a href="/Attraction_Review-g294265-d2149128-Reviews-Gardens_by_the_Bay-Singapore.html" target="_blank">

            # get each poi element on the current listing page
            div_elements = soup.find_all('div', class_='alPVI eNNhq PgLKC tnGGX')

            # for each poi element, scrap poi url 
            for div_element in div_elements:
                # find the url's postfix in <a> element, combine the url with url prefix and postfix
                poi_url = 'https://www.tripadvisor.com' + div_element.find('a')['href']
                # append the full poi url to the poi url list
                self.poi_url_list.append(poi_url)


        # save the poi url list to .txt file
        with open(self.filename, 'w') as file:
            for url in self.poi_url_list:
                file.write(url + '\n')


        # return list of poi urls
        print(f"\nScrapped {len(self.poi_url_list)} POI URLs.")
        return self.poi_url_list
    

    #FUNCTION: print out url list
    def print_poi_urls(self):
        for poi_url in self.poi_url_list:
            print(poi_url)



# MAIN
if __name__ == '__main__':

    # scrap all POI's url from the listing page of Singapore
    scraper = PoiUrlScraper()
    poi_urls = scraper.get_poi_urls()

    # print all urls
    #scraper.print_poi_urls()

