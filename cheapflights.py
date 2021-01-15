import requests
import re
import optparse
import random
import argparse
import datetime
from termcolor import colored
from proxies.proxies import Scrapper, Proxy, ScrapperException
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

def dev_testing():
    """
    Function for tesing against downloadded html response
    """
    with open('second.html', 'r') as data:
        m = data.read()
    return m

def check_connection():
    """
    Function to check if i'm conntected to the internet
    """
    r = requests.get('https://www.google.com')
    if r.status_code == 200:
        print (colored("Connected.", 'green'))
    else:
        print (colored("Not Connected.", 'red'))

def check_proxy_status(proxy_ip):
    """
    Function to check if a proxy is live
    Parameter:  proxy ip
    """
    try:
        status = subprocess.check_output(["ping", "-c","1", proxy_ip]).decode('utf-8')
        if status.find("1 received") > -1:
            return True
    except subprocess.CalledProcessError as e:
        return False

    return False
    
def get_data(data):
    """
    Get specific types of data to display on the flight cubes.
    Parameter: data, the data to be queried
    """
    depart = data[0].lstrip(" ")
    aiport_time = data[1].lstrip(" ")
    duration = data[3].rstrip("<").lstrip(" ")
    return f"[b][yellow]{depart}[/b]\n[green]{aiport_time}\n{duration}"


def get_flights(request_data):
    """
    Getting all the flights from the returned html data
    """
    flight_data = []
    flights = re.findall('Provided\s\w+.+<', request_data)

    [flight_data.append(i.split(",")) for i in flights]

    console = Console()
    user_render = [Panel(get_data(user), expand=False, title=f"FLIGHT",box=box.HEAVY_HEAD, border_style="pale_turquoise1") for user in flight_data]
    console.print(Columns(user_render))


def get_arguments():
    """
    Get program arguments
    """
    parse = argparse.ArgumentParser(description="Let's test")
    # parse.add_argument("-y", "--year", dest="year", help="Year")
    parse.add_argument("-m", "--month", dest="month", help="Month")
    parse.add_argument("-d", "--day", dest="day", help="Day")
    parse.add_argument("-f", "--from", dest="cfrom", help="From")
    parse.add_argument("-t", "--to", dest="to", help="To")

    return parse.parse_args()

arguments = get_arguments()

def ssl_proxies():
    """
    Using the proxy library to get http proxies.

    """
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
    It will use a random proxy and user-agent to avoid being cought as a bot.

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

    if check_proxy_status:
        proxies = proxy_list[random_proxy]
        print("Using http proxy.")
    else:
        print("Proxy Down, using original ip.")
        proxies = {}


    now = datetime.datetime.now()

    request_session = requests.Session()
    flight_request_uri = f"https://www.cheapflights.co.za/flight-search/{arguments.cfrom}-{arguments.to}/{now.year}-{arguments.month}-{arguments.day}?sort=price_a"

    # print(colored(flight_request_uri, 'white')) the url.
    # print(len(request.text))
    request = request_session.get(flight_request_uri, headers=headers, proxies=proxies)

    length = len(request.text)
    if request.text.find("""If you are seeing this page, it means that Cheapflights thinks you are a "bot," and the 
                            page you were trying to get to is only useful for humans.""") > -1 :
        print(colored('Ithi Uyi\'Robot Leshandis', 'red', attrs=['bold', 'blink']))
    
    cheapest = re.search("""Cheapest\n</\w+>\n</\w+>\n</\w+>\n</\w+>\n<\w+\s\w+="\w+\s\w+">\n<\w+\s\w+='\w+-\w+\s\w+-\
                            w+\s\w+\s\w+\s\w+\s\w+\s\w+'\n>\nR\d\s\d{3}\n|R\d{3}\n""", request.text)

    try:
        get_flights(request.text)
        return(cheapest.group(0).rstrip())
    except AttributeError:
        return (colored("Something went wrong, Try again.", 'red'))

print(get_cheapest_flight())

# print(check_proxy_status("14.63.228.217"))
# proxies = proxies[r]
# r = requests.get('https://httpbin.org/ip', proxies=proxy, timeout=20)
# print(r.text)
