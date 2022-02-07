import random
import requests
from bs4 import BeautifulSoup

def scrape_clubs(URL="https://ocwp.pennlabs.org/"):
    page = requests.get(url=URL)
    soup = BeautifulSoup(page.content, "html.parser")
    section = soup.find("section", class_="section")
    container = section.find("div", class_="container")
    boxes = container.find_all("div", class_="box")
    all_clubs = list(map(convert_to_json, boxes))
    return all_clubs

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
