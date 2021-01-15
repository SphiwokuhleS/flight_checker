import requests
import re
import optparse
import random
import argparse
import datetime
from termcolor import colored
from proxies import Scrapper, Proxy, ScrapperException
from torrequest import TorRequest
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich import box
import json
import os
import subprocess

#TODO add 9 more user-gents to randomly pick from

#flight = "<div class="bottom " >" for regex
#20779
with open('second.html', 'r') as data:
    m = data.read()

def check_connection():
    r = requests.get('https://www.google.com')
    if r.status_code == 200:
        print (colored("Connected.", 'green'))
    else:
        print (colored("Not Connected.", 'red'))

def check_proxy_status(proxy_ip):
    try:
        status = subprocess.check_output(["ping", "-c","1", proxy_ip]).decode('utf-8')
        if status.find("1 received") > -1:
            return True
    except subprocess.CalledProcessError as e:
        return False
    # status = os.system(f"ping -c 1 {proxy_ip}")

    return False
    
def get_data(data):
    depart = data[0].lstrip(" ")
    aiport_time = data[1].lstrip(" ")
    # lands = data[2].lstrip(" ")
    duration = data[3].rstrip("<").lstrip(" ")
    return f"[b][yellow]{depart}[/b]\n[green]{aiport_time}\n{duration}"


def get_flights(request_data):
    flight_data = []
    flights = re.findall('Provided\s\w+.+<', request_data)

    [flight_data.append(i.split(",")) for i in flights]

    console = Console()

    # console.print(data, overflow='ignore', crop=False)
    user_render = [Panel(get_data(user), expand=False, title=f"FLIGHT",box=box.HEAVY_HEAD, border_style="pale_turquoise1") for user in flight_data]
    console.print(Columns(user_render))
    
    # for i in range(1, len(flight_data)):
    #     print( "Flight :" + str(i))
    #     for x in flight_data[i]:
    #         print(x.strip(" ").rstrip("<"))
    #     print("\n")

# get_flights(m)
def get_arguments():

    parse = argparse.ArgumentParser(description="Let's test")
    # parse.add_argument("-y", "--year", dest="year", help="Year")
    parse.add_argument("-m", "--month", dest="month", help="Month")
    parse.add_argument("-d", "--day", dest="day", help="Day")
    parse.add_argument("-f", "--from", dest="cfrom", help="From")
    parse.add_argument("-t", "--to", dest="to", help="To")

    return parse.parse_args()

arguments = get_arguments()

def ssl_proxies():
    # Category = 'PROXYLIST_DOWNLOAD_HTTPS'
    Category = 'PROXYLIST_DOWNLOAD_HTTP'

    # Initialize the Scrapper
    scrapper = Scrapper(category=Category, print_err_trace=False)

    # Get ALL Proxies According to your Choice
    data = scrapper.getProxies()

    proxies_list = []
    https = "http"
    for item in data.proxies:
        proxies_list.append({https : '{}:{}'.format(item.ip, item.port)})
    return proxies_list

def get_cheapest_flight():

    """
    This function will look for the cheapest flight from cheapflights.co.za,
    Function can still be upgraded to provide more information.

    Parameter:  month, day, from, to. 
    The one : <p\sid="\w+.+</p> 
    """

    user_agent = [

    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (X11; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
    'Opera/9.80 (Linux armv7l) Presto/2.12.407 Version/12.51 , D50u-D1-UHD/V1.5.16-UHD (Vizio, D50u-D1, Wireless)',

    ]

    proxy_list = ssl_proxies()
    # print(len(proxy_list))
    random_agent = random.randint(0, len(user_agent)-1)
    random_proxy = random.randint(0, len(proxy_list)-1)
    print(random_proxy)
    headers = { 'User-agent' : user_agent[random_agent],
                'Connection' : 'close',
                'Upgrade-Insecure-Requests': '1',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Sec-Fetch-Site' : 'same-origin',
                'Sec-Fetch-Mode' : 'navigate',
                'Sec-Fetch-User' : '?1',
                'Sec-Fetch-Dest' : 'document',
                'Referer'        : 'https://www.cheapflights.co.za/',
                'Accept-Encoding': 'gzip, deflate' ,
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    proxies = {'https' : '139.162.41.219:8889'}
    # proxies = { 'http' : '192.109.165.221:80' }

    # print(proxies)
    now = datetime.datetime.now()

    request_session = requests.Session()
    # print(request_session)
    flight_request_uri = f"https://www.cheapflights.co.za/flight-search/{arguments.cfrom}-{arguments.to}/{now.year}-{arguments.month}-{arguments.day}?sort=price_a"

    print(colored(flight_request_uri, 'white'))

    # print(len(request.text))

    # request = request_session.get(flight_request_uri, headers=headers)
    request = request_session.get(flight_request_uri, headers=headers, proxies=proxies)
    

    length = len(request.text)
    if request.text.find("""If you are seeing this page, it means that Cheapflights thinks you are a "bot," and the 
                            page you were trying to get to is only useful for humans.""") > -1 :
        print(colored('Ithi Uyi\'Robot Leshandis', 'red', attrs=['bold', 'blink']))

    print(len(request.text))
    # print(len(user_agent[random_agent]))
    
    cheapest = re.search("""Cheapest\n</\w+>\n</\w+>\n</\w+>\n</\w+>\n<\w+\s\w+="\w+\s\w+">\n<\w+\s\w+='\w+-\w+\s\w+-\
                            w+\s\w+\s\w+\s\w+\s\w+\s\w+'\n>\nR\d\s\d{3}\n|R\d{3}\n""", request.text)

    try:
        get_flights(request.text)
        return(cheapest.group(0).rstrip())
    except AttributeError:
        return (colored("Something went wrong, Try again.", 'red'))


# check_connection()
# print(ssl_proxies())
print(get_cheapest_flight())

# proxies = ssl_proxies()
# r = random.randint(0, len(proxies))
# proxy = proxies[r]
# print(proxy)
# print(ssl_proxies())
# proxy = {'https' : '79.104.25.218:8080'}
# proxy = {'https' : '63.249.67.70:53281'}
# proxy = {'https' : '139.162.41.219:8889'}
# proxy = {'http' : '175.141.69.203:80'}


# print(check_proxy_status("14.63.228.217"))
print(check_proxy_status("175.141.69.203"))
# proxies = proxies[r]
# r = requests.get('https://httpbin.org/ip', proxies=proxy, timeout=20)
# print(r.text)
