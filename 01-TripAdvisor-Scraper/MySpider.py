import random
import requests
import time

from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# get the html content of a url

class Spider(object):
    def __init__(self):
        '''
        # initialize a user agent
        user_agent = UserAgent()
    
        # set up dictionary headers to store the random user agent 
        headers = {
            'UserAgent':user_agent.chrome
        }

        # Set up Chrome options with the custom User-Agent
        chrome_options = Options()
        chrome_options.add_argument(f'user-agent={headers["UserAgent"]}')

        # Initialize the browser with the custom User-Agent
        self.browser = webdriver.Chrome(options=chrome_options)

        # Check the actual User-Agent from Chrome options
        actual_user_agent = self.browser.execute_script("return navigator.userAgent;")
        print("User-Agent:", actual_user_agent, '\n')

        '''

        # initialize a random user agent in the headers
        user_agent = UserAgent()

        #self.headers = {'User-Agent': user_agent.chrome}
        self.headers = {
            'authority': 'tripadvisor.com',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'user-agent': user_agent.chrome,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
        }
        #print(f'headers:', self.headers)

        self.url = 'https://www.tripadvisor.com/Attractions-g294265-Activities-oa0-Singapore.html'         # url for testing
        
        self.flag = 1

    def get_proxies(self):
        with open('proxies.txt', 'r') as f:
            result = f.readlines()                  # read all proxies in the list
        proxy_ip = random.choice(result)[:-1]       # choose a random proxy
        L = proxy_ip.split(':')
        proxy_ip = {
            'http': 'http://{}:{}'.format(L[0], L[1]),
            'https': 'https://{}:{}'.format(L[0], L[1])
        }
        return proxy_ip

    def get_html(self):

        #proxies = self.get_proxies()
        #print(proxies)

        if self.flag <= 3:
            try:
                '''
                self.browser.get(self.url)

                # get the html content
                self.html = self.browser.page_source

                '''
                self.html = requests.get(url=self.url, headers=self.headers, timeout=5).text #proxies=proxies,
                #print(self.html)

                 # check if successfully get the html content
                if "<!DOCTYPE html>" in self.html:
                    print(f"Spider got the html content!")
        
                else:
                    print(f"Spider failed to get the html content.")
                
                # after every request, randomly rest for seconds
                #print("Randomly rest for seconds.")
                time.sleep(random.randint(1,3))

                return self.html

            except Exception as e:
                print('Retry')
                self.flag += 1
                self.get_html()
    
    # FUNCTION: write the html content to file, for debug purpose
    def write_html(self):
        # reserve strings after the domain as html file name
        truncated_url = self.url[len("https://www.tripadvisor.com/"):]
        
        # Write the HTML content to a file in the folder html
        with open(f"html/{truncated_url}", "w", encoding="utf-8") as file:
            file.write(self.html)

        # Print a message indicating the file write operation is completed
        print("HTML content has been written to file.")


if __name__ == '__main__':
    spider = Spider()
    spider.get_html()
    spider.write_html()