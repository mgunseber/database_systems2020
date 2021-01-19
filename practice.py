import ssl
import certifi
import requests
from bs4 import BeautifulSoup

r = requests.get(
    "https://www.zorlupsm.com/tr/takvim?searchQuery=&types=18&places=&fromDate=&toDate=")
source = BeautifulSoup(r.content, "lxml")


#cinema = source.find_all("div", attrs={"class": "eventContents"})

# event = (teather[0].contents)[len(teather[0].contents)-1]

online = source.find_all(
    "div", attrs={"class": "events-carousel__item__info"})
for e_property in online:
    event_title = e_property.find(
        "a", attrs={"class": "events-carousel__item__info__title"})
    event_loc = e_property.find(
        "a", attrs={"class": "events-carousel__item__info__subtitle"})
    event_date = e_property.find(
        "a", attrs={"class": "events-carousel__item__info__footer__right"})
    # event_price = teather.find("div", attrs={"class": "flex fluid title"})
    print((event_loc).text)
    print((event_date).text)
    print((event_title).text)
