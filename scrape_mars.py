#import dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

def scrape_all():

    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_headline = mars_news(browser)

    #Run all scraping functions and store them
    data = {
        "news_title": news_title,
        "news_paragraph": news_headline,
        "featured_image": featured_image(browser),
        "hemispheres": mars_hemispheres(browser),
        "weather": twitter_mars_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    #Stop webdriver and return the info
    browser.quit()
    return data


#MARS FUNCTION
def mars_news(browser):
    #visit the nasa mars site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    #can create delay for loading web page if wanted
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    #convert the browser.html to a soup object
    html = browser.html
    mars_news_soup = BeautifulSoup(html, 'html.parser')

    try:
        slide_elem = mars_news_soup.select_one('ul.item_list li.slide')

        #Using parent element to find the first a tag and it to the variable "news_title"
        news_title = slide_elem.find("div", class_="content_title").get_text()

        #Use the parent element to find the text in the paragraph tag
        news_headline = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_headline


#MARS FUNCTION
def featured_image(browser):
    #visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    #Find and click on the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    #Finding the more info button (the first one doesn't work, but by running both one of them can find the 'more info' button)
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    #parsing the new html site we passed onto by clicking the more info button
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    #find the images source url
    img_src_url = img_soup.select_one('figure.lede a img')

    try:
        img_url = img_src_url.get('src')

    except AttributeError:
        return None

    #image web link
    image_url_link = f'https://www.jpl.nasa.gov{img_src_url}'

    return image_url_link


#TWITTER WEATHER FUNCTION
def twitter_mars_weather(browser):
    #Going to the twitter url
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)

    #parsing the html with BeautifulSoup
    html = browser.html
    weather_soup = BeautifulSoup(html, 'html.parser')

    # finding a tweet with the data-name 'Mars Weather'
    mars_weather_tweet = weather_soup.find('div', attrs={"class": "tweet", "data-name": "Mars Weather"})

    #getting the weather report text from the tweet
    mars_weather = mars_weather_tweet.find('p', 'tweet-text').get_text()

    return mars_weather



def mars_hemispheres(browser):

    #Going to the astreology url
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    hemi_img_urls = []

    #getting the list of all the links for hemisphere images
    links = browser.find_by_css("a.product-item h3")

    #looping through the links, clic on it and find the sample anchor and then return back
    for i in range(len(links)):
        hemisphere = {}

        #have to find each link to avoid it being stale element exemption
        browser.find_by_css("a.product-item h3")[i].click()

        #finding the sample image anchor tag and take the href url
        sample_elem = browser.find_link_by_text('Sample').first
        hemisphere['img_url'] = sample_elem['href']

        #Get hemisphere title
        hemisphere['title'] = browser.find_by_css("h2.title").text

        #Appending the title and image links as an object to the hemi_img_urls list
        hemi_img_urls.append(hemisphere)

        #navigate back to the startingg url
        browser.back()

    return hemi_img_urls

def scrape_hemisphere(html_text):
    #Soupify the html site's text
    hemi_soup = BeautifulSoup(html_text, 'html.parser')

    #trying to get href unless there is an error
    try:
        title_elem = hemi_soup.find('h2', class_="title").get_text()
        sample_elem = hemi_soup.find('a', text='Sample').get('href')

    except AttributeError:

        # Image error returns none for better handling on the front end
        title_elem = None
        sample_elem = None

    hemishpere = {
        'title': title_elem,
        'image_url': sample_elem
    }

    return hemisphere

def mars_facts():
    try:
        mars_facts_df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    mars_facts_df.columns = ['description', 'value']
    mars_facts_df.set_index('description', inplace=True)

    return mars_facts_df.to_html(classes='table table-striped')

if __name__ == "__main__":

    #if running as script to see if it is working use this to see scraped Data
    print(scrape_all())
