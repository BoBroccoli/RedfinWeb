from bs4 import BeautifulSoup
import requests
import pandas as pd
from geopy.geocoders import Nominatim
import geopy.distance as geoDis
import sys
import re 
import copy

url = 'https://www.redfin.com/city/16500/NY/Rye-Brook/filter/mr=6:16495'
current_city = 'Stamford'
current_country = 'USA'

class House(object):
    def __init__(self, open_time, address, price, size, beds, baths, year, house_link, lat, long):
        self.open_time = open_time
        self.address = address
        self.price = price
        self.size = size
        self.beds = beds
        self.baths = baths
        self.year = year
        self.size = size
        self.house_link = house_link
        self.lat = lat
        self.long = long


def process_houses(single_house_req):
    open_time_tag = single_house_soup.find('div', {'class': 'Pill Pill--open-house padding-vert-smallest padding-horiz-smaller font-size-smaller font-weight-bold font-color-white HomeSash margin-right-smaller margin-top-smallest'})
    if open_time_tag is not None:
        open_time = open_time_tag.contents[0]
        address = single_house_soup.find('title').contents[0].split('|')[0]
        price = single_house_soup.find('div', {'class': 'statsValue'}).contents[0]
        size = single_house_soup.find('div', {'class': 'stat-block sqft-section'}).span.contents[0]
        beds = single_house_soup.find_all('div', {'class': 'stat-block beds-section'})[1::2][0].div.contents[0]
        baths = single_house_soup.find('div', {'class': 'stat-block baths-section'}).div.contents[0]
        year = single_house_soup.find(text='Year Built').parent.nextSibling.contents[0]
        house_link = single_house_req
        geo_position = single_house_soup.find('meta', {'name': 'geo.position'})['content']
        geo = geo_position.split(';')
        house = House(open_time, address, price, size, beds, baths, year, house_link, float(geo[0]), float(geo[1]))
        same_time_houses = time_houses_dict.get(open_time.split(',')[0], [])
        same_time_houses.append(house)
        time_houses_dict[open_time.split(',')[0]] = same_time_houses
    
def find_shortest_trip(distanceMap: dict, visited, start: int, total: float, level: int, result: list):
    global min_distance
    global route
    if(level == len(visited)):
        if total < min_distance:
            min_distance = total
            route = copy.deepcopy(result)
            #print(str(min_distance))
    for i in range(1, len(visited)):
        if(visited[i] == False) :
            if total+distanceMap.get(str(start)+'->'+str(i)) >= min_distance:
                continue
            visited[i] = True
            result.append(i)
            find_shortest_trip(distanceMap, visited, i, total+distanceMap.get(str(start)+'->'+str(i)), level+1, result)
            result.pop()
            visited[i] = False

def sort_houses(route: list, houses: list):
    res = []
    for i in range(1, len(route)):
        res.append(houses[route[i]-1])
    return res

def create_df(houses):
    raw_data={'open_time': houses_open_time,
        'address': houses_address,
        'prices': prices,
        'size': sizes,
        'beds': beds,
        'baths': baths,
        'year': year,
        'house_link': house_links
    }
    for house in houses:
        houses_open_time.append(house.open_time)
        houses_address.append(house.address)
        prices.append(house.price)
        sizes.append(house.size)
        beds.append(house.beds)
        baths.append(house.baths)
        year.append(house.year)
        house_links.append(house.house_link)
    houses_open_time.append('')
    houses_address.append('')
    prices.append('')
    sizes.append('')
    beds.append('')
    baths.append('')
    year.append('')
    house_links.append('')
    return raw_data

loc = Nominatim(user_agent="GetLoc")
locRes = loc.geocode(current_city+','+ current_country)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
resp = requests.get(url, headers = headers)

soup = BeautifulSoup(resp.content, 'html.parser')
house_lists = soup.find_all('div', {'class': 'HomeCardsContainer flex flex-wrap'})
time_houses_dict = {}
for i in range(0,2):
    for house in house_lists[i].find_all('div', {'class': 'HomeCardContainer'}, id=re.compile('MapHomeCard')):
        #print(house)
        house_link = house.find('a')
        single_house_req = 'https://www.redfin.com'+house_link['href']
        single_house_soup = BeautifulSoup(requests.get(single_house_req, headers = headers).content, 'html.parser')
        process_houses(single_house_req)
        
houses_open_time = []
houses_address = []
prices = []
sizes = []
beds = []
baths = []
year = []
house_links = []
for houses in time_houses_dict.values():
    distance = [[locRes.latitude, locRes.longitude]]
    for house in houses:
        distance.append([house.lat, house.long])

    distanceMap = {}
    for i in range(len(distance)):
        for j in range(i+1, len(distance)):
            distanceMap[str(i)+'->'+str(j)] = geoDis.geodesic(distance[i], distance[j]).miles
            distanceMap[str(j)+'->'+str(i)] = geoDis.geodesic(distance[i], distance[j]).miles

    visited = [bool(False)] * (len(houses)+1)
    visited[0] = True
    min_distance = sys.float_info.max
    route = {}
    find_shortest_trip(distanceMap, visited, 0, 0.0, 1, [0])
    houses = sort_houses(route, houses)
    create_df(houses)
data={'open_time': houses_open_time, 'address': houses_address, 'prices': prices, 'size': sizes, 'beds': beds, 'baths': baths, 'built year': year, 'house link': house_links}
df=pd.DataFrame(data)
df.to_csv('redlin_open_house.csv')
    




