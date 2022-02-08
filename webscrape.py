import random
import requests
from bs4 import BeautifulSoup

'''
This function takes in a URL and deconstructs the HTML page it points to using BeautifulSoup
Uses helper functions convert_to_json and club_code_maker to format clubs from site into JSON
'''
def scrape_clubs(URL="https://ocwp.pennlabs.org/"):
    page = requests.get(url=URL)
    soup = BeautifulSoup(page.content, "html.parser")
    section = soup.find("section", class_="section")
    container = section.find("div", class_="container")
    boxes = container.find_all("div", class_="box")
    all_clubs = list(map(convert_to_json, boxes))
    return all_clubs

'''
This function takes a particular "box" and takes the required text elements of club name, tags, and description
The, using helper function club_code_maker() generates a code based off of the club name and pseudo-random integers
'''
def convert_to_json(box):
    club_name = box.find("strong", class_="club-name").text.strip()
    club_tags = [i.text.strip() for i in box.find_all("span", class_="tag")]
    club_description = box.find("em").text.strip()
    return {
        "code": club_code_maker(club_name),
        "name": club_name,
        "description": club_description,
        "tags": club_tags,
    }

'''
Using the club name, takes the first letter of each word then lower-cases the combined string
Combines this string with random integers to ensure no overlap in codes for the clubs being added
'''
def club_code_maker(name):
    result = ""
    take_next = True
    for i in name:
        if(i == ' '):
            take_next = True
        elif(i != ' ' and take_next):
            result += i
            take_next = False
    return (result.lower() + str(random.randint(0,1000)))


if __name__ == '__main__':
    scrape_clubs()
