from bs4 import BeautifulSoup
import requests
import pandas as pd
from geopy.geocoders import Nominatim
import geopy.distance as geoDis
import sys
import re 
import copy

url = 'https://www.redfin.com/city/26700/CT/Westport'
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

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            'referer': 'https://www.redfin.com/city/26700/CT/Westport/filter/min-price=50k,max-price=1M',
            'cookie': '''RF_UNBLOCK_ID=dMBAHWHp; AKA_A2=A; RF_CORVAIR_LAST_VERSION=433.4.0; RF_BROWSER_ID=ro6dvnmsR-eNAILXjewcNQ; RF_BROWSER_ID_GREAT_FIRST_VISIT_TIMESTAMP=2022-08-30T19%3A05%3A48.878; RF_BID_UPDATED=1; searchMode=1; sortOrder=1; sortOption=special_blend; collapsedMapView=1; bm_mi=8EC5A635E4A0FD64111B76A4ED0F05D4~YAAQkRnfF5l2ScmCAQAAFcal8RDAYipH945D9YAyT/50YyvZE/mcq4mLAu/LKffSAR9+qrQ+aGyJWJmWfUKQwvRpnz2Z665FKnuNAVBAgADxJhS30d9SihGVm8gT5zrzozZaE8LXyAl99g1HrRS8gIAxdafKQkYbzMRutikOeEK02apsMd3o5tXVSUrCWQTMEA5WtB8ih/hmg7yY+28u72Vtm+AlIUKVaIGAENGg1rNoLaWd0WGP91rUoQ4Ke7vfWceuxaFNrDgqLpVXsJidIgB2PQOr+dzZyBrhZZspnNH9qFMYOZg=~1; _gcl_au=1.1.1098551747.1661911544; run_fs_for_user=500; _rdt_uuid=1661911544133.4a8d67ec-37ce-47a2-8179-daa337b4e38b; __pdst=e8b3520305a14e13b4c4b1cb3a4dc2fc; _fbp=fb.1.1661911544587.1735231379; AMP_TOKEN=%24NOT_FOUND; _gid=GA1.2.910858316.1661911545; _tt_enable_cookie=1; _ttp=7440b717-0198-495f-a419-e5bd6c2e8ddc; _clck=naekde|1|f4h|0; RF_BROWSER_CAPABILITIES=%7B%22screen-size%22%3A4%2C%22events-touch%22%3Afalse%2C%22ios-app-store%22%3Afalse%2C%22google-play-store%22%3Afalse%2C%22ios-web-view%22%3Afalse%2C%22android-web-view%22%3Afalse%7D; RF_LAST_NAV=0; ak_bmsc=5B55840C368879C63B09F8B20E9C4AB6~000000000000000000000000000000~YAAQkRnfF9l2ScmCAQAABc2l8RDext0xAwUsW91wbxWV8v01+w1ou8ji37xk02EbqZFZcfsNqga3X+qcsUQ73/cVtf5Hm+f5Qxm01fd7ko5Qh9aVzzafVMSFlyHv3bI07lOkclY9frIy7rdvClKaAYTXhyUoaq/gyUp/e7o8LFfVSFcgzSYTHekrxB9oUbE63zKcUVnrNFxrBo8M2p2gNdYwYaBA0yp8pBrYvaXwaKaGvSVIss8zQPp2Asiha5FweWpE9xauEvjOok11R14PmUkTuCaMVuKH3F0hdTRyc8yM0HqLjhUUUBqqzl2L0vAUpwospUFK8gfRxL66J8ws/VK/JaqB18HvqeGRwbgwgIjnuxxB2lOGy9qYCWhP//Xq97V1hbXhHiskYkvxtT5nhzHphn1rGOM=; G_ENABLED_IDPS=google; FEED_COUNT=%5B%22%22%2C%22f%22%5D; __gads=ID=a1bea72443dbda6b:T=1661911553:S=ALNI_MZKW5TdJ2w5XN6h5jKT0cMQsFzSMQ; __gpi=UID=000007cc5c71e297:T=1661911553:RT=1661911553:S=ALNI_MZbV3lSHcZX0I6v33xgFh020inarA; g_state={"i_p":1661918749328,"i_l":1}; RF_VISITED=true; unifiedLastSearch=name%3DWestport%26subName%3DWestport%252C%2520CT%252C%2520USA%26url%3D%252Fcity%252F26700%252FCT%252FWestport%26id%3D2_26700%26type%3D2%26unifiedSearchType%3D2%26isSavedSearch%3D%26countryCode%3DUS; RF_MARKET=connecticut; RF_LAST_SEARCHED_CITY=Westport; FCNEC=[["AKsRol_o6yL8ILDXry_pnaHfX6oceGXsF9XgzPsRLBjXE34-XnIyfPn9GZJ4bkrtNAKKZnWByT_Uh0EJmyg1cXbgkQqNyPbsFD1ckEzPhChclQ2x1iIBoKoob44n1d2qbZMpWBa7nyLYX-qpaQCqtlG0h-yLtDrluQ=="],null,[]]; _clsk=w4pobv|1661912365382|9|0|m.clarity.ms/collect; userPreferences=parcels%3Dtrue%26schools%3Dfalse%26mapStyle%3Ds%26statistics%3Dtrue%26agcTooltip%3Dfalse%26agentReset%3Dfalse%26ldpRegister%3Dfalse%26afCard%3D2%26schoolType%3D0%26viewedSwipeableHomeCardsDate%3D1661912380477; bm_sv=7FA1BCE0797663A78B33FED538696FBE~YAAQihnfF8cMZsqCAQAA0nSy8RAHktDpaJ8rRh7hNuizwCp27hKB5hCAcya1pB1CdXCzHtuTjh8K6w6PxetIP4mGs8kO3NTXJCYstn7lBL9+DL0TjnbDmTNBZ2rq7eSrSpjfGBNnC61E/ucCHJaxAzeIZ1U32j9UFp8cjsNhA7aXKl7DBQzHvsSeBeMRNc9Rk+nJ0nMghYkXvPjGQmSZvgXOS/TKW6pjiIcEJA9xf1K4gWGJQyNA4IJfG0QoONrjgw==~1; _ga_928P0PZ00X=GS1.1.1661911544.1.1.1661912375.59.0.0; _ga=GA1.2.1139433679.1661911544; _dc_gtm_UA-294985-1=1; _uetsid=6c471f5028d111edb9c6cdc59e5282ae; _uetvid=6c473d0028d111ed87d6d56871ba8b20'''}
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
    




