from tranco import Tranco
from BackNForthIterator import BackNForthIterator
import datetime
from bs4 import BeautifulSoup
import requests
import pymongo
from dotenv import load_dotenv   
load_dotenv()                    
import os 
import sys

def setup_mongo(list_position):
    username = os.environ.get("MONGODB_ATLAS_USER")
    password = os.environ.get("MONGODB_ATLAS_PASSWORD")
    client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.mznnc.mongodb.net/ScrapeDatabase?retryWrites=true&w=majority")
    db = client.mydb

    collection = db[f"real_requests_scraper_{list_position}1000"]
    return collection

def get_request(url):
    user_agent = {'User-agent': "Mozilla/5.0 (Linux; Android 8.0.0; Nexus 5X Build/OPR4.170623.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Mobile Safari/537.36"}
    return requests.get(url, headers=user_agent, timeout=10)

def setup_tranco():
    t = Tranco(cache=True, cache_dir='.tranco')
    list_ = t.list(date='2021-06-12')
    top1m = list_.top(1000000)
    print(len(top1m))
    return top1m

def get_number_of_preloads(html):
    preloads = html.find_all("link", {"rel" : "preload"})
    return len(preloads)

def get_preloads(html):
    preloads = html.find_all("link", {"rel" : "preload"})
    return list(map(str, preloads))

def get_number_of_preconnects(html):
    preconnect_hints = html.find_all("link", {"rel" : "preconnect"})
    return len(preconnect_hints)

def get_preconnects(html):
    preconnects = html.find_all("link", {"rel" : "preconnect"})
    return list(map(str, preconnects))

def get_number_of_dns_prefetches(html):
    dns_prefetch_hints = html.find_all("link", {"rel" : "dns-prefetch"})
    return len(dns_prefetch_hints)

def get_dns_prefetches(html):
    dns_prefetches = html.find_all("link", {"rel" : "dns-prefetch"})
    return list(map(str, dns_prefetches))

def meets_our_requirements(html):
    has_at_least_1_preload = get_number_of_preloads(html) > 0 
    has_at_least_1_resource_hint = (get_number_of_dns_prefetches(html) > 0 or get_number_of_preconnects(html) > 0)
    
    return (has_at_least_1_preload and has_at_least_1_resource_hint)

def headers_contain_preloads_or_resource_hints(request):
    # use short circuiting so we do not get an error...
    return ("Link" in request.headers) and ("preload" in request.headers["Link"] or "dns-prefetch" in request.headers["Link"] or "preconnect" in request.headers["Link"])
        
def main():

    if len(sys.argv) != 2:
        print("Use scraper.py top|middle|bottom")
        quit()
    
    if sys.argv[1] not in ["top","middle", "bottom"]:
        print("Please provide top|middle|bottom")
        quit()

    list_position = sys.argv[1]

    tranco_list_full = setup_tranco()
    if list_position == "top":
        tranco_list = tranco_list_full
    elif list_position == "middle":
        tranco_list = list(BackNForthIterator(tranco_list_full))
    elif list_position == "bottom":
        tranco_list = tranco_list_full[::-1]


    print(tranco_list[:10])
    db = setup_mongo(list_position)

    nr_of_websites_visited = 0
    nr_of_websites_meeting_criteria = 0

    start_time = datetime.datetime.now()
    print("Start time: ", start_time)
    for website in tranco_list:
        print("======================================================================")

        if nr_of_websites_meeting_criteria == 1000:
            print("Finished!")
            break

        browser_url = f"http://{website}"
        print("Loading ", browser_url)

        try:
            request = get_request(browser_url)

            page_source = request.text
            soup = BeautifulSoup(page_source, "lxml")

            meets_requirements = meets_our_requirements(soup)
            headers_contain_preloads_or_hints = headers_contain_preloads_or_resource_hints(request)

            if meets_requirements:
                print("Meets criteria: TRUE")
                print("Nr of preloads: ", get_number_of_preloads(soup) )
                print("Nr of resource hints: ", get_number_of_dns_prefetches(soup) + get_number_of_preconnects(soup))

                if not headers_contain_preloads_or_hints:
                    nr_of_websites_meeting_criteria += 1

            if headers_contain_preloads_or_hints:
                print("Contains Link headers: TRUE")
                print(request.headers["Link"])

            data = {
            "tranco_url" : website,
            "browser_url" : browser_url,
            "meets_criteria" : meets_requirements,
            "nr_preloads" : get_number_of_preloads(soup),
            "preloads" : get_preloads(soup),
            "nr_dns_prefetches" : get_number_of_dns_prefetches(soup),
            "dns_prefetches" : get_dns_prefetches(soup),
            "nr_preconnects" : get_number_of_preconnects(soup),
            "preconnects" : get_preconnects(soup),
            "headers_contain_preloads_or_hints" : headers_contain_preloads_or_hints,
            "link_headers" : request.headers["Link"] if headers_contain_preloads_or_hints else None
            }

        except Exception as e:
            print("Error")
            print(e)
            data = {
                "tranco_url" : website,
                "browser_url" : browser_url,
                "error" : str(e)
            }
        finally:
            nr_of_websites_visited += 1
            print("Total # of Loaded Websites: ", nr_of_websites_visited)
            print(f"Total # of Websites Meeting Our Criteria: {nr_of_websites_meeting_criteria} ({nr_of_websites_meeting_criteria/nr_of_websites_visited}%)")
            print("Time since start: ", str(datetime.datetime.now()-start_time))

            db.insert_one(data)

    end_time = datetime.datetime.now()
    print("End time: ", end_time)
    print("Total time taken: ", str(end_time-start_time))

if __name__ == "__main__":
    main()