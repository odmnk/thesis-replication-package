from mitmproxy import http
from mitmproxy import ctx
from bs4 import BeautifulSoup, Comment
import datetime
class Change:
    def __init__(self):
        self.REMOVE_HINTS = False
        self.sites = []

        self.POST_SERVER = "192.168.2.7"
        self.POST_SERVER_PORT = 8000

        self.js_snippet = 'function xml_http_post_experiment(url, data, callback) { var req = new XMLHttpRequest(); req.open("POST", url, true); req.send(data); } function calcaulate_performance() { var plt = window.performance.timing.loadEventStart - window.performance.timing.navigationStart; console.log("Calculated PLT :" + plt);  xml_http_post_experiment("https://example.com/ourserver",  plt, null)} window.addEventListener ? window.addEventListener("load", calcaulate_performance, true) : window.attachEvent && window.attachEvent("onload", calcaulate_performance);'

        self.urls = ["braunshop.co.uk", "mommysnippets.com", "berlinomagazine.com", "thefreelancemovement.com", "accesspressthemes.com", "westernunion.com", "home.pl", "palagrit.com", "teleseryeonline.su", "tebasnan.com", "manchestereveningnews.co.uk",
        "iamvenezuela.com", "tuha.vn",
         "opumo.com", #redircts to opumo.com
         "gardeninglovy.com",
         "mirror.co.uk", "ecomputertips.com", "axomjobs.in", "jezebel.com", "dell.com", "multimetertools.com", "foundationfairy.com", "writeawriting.com", 
         "olympics.com", "dailymail.co.uk", "nationalreview.com", 
         "kentlive.news", "creativebloq.com", "rockcontent.com", "therecipespk.com", "dictionary.com", "ncaa.com", "caribbean-beat.com", "dallasnews.com", "oeco.com.br", "lululemon.com", "beautydea.it", "simplylakita.com", "express.co.uk", "searchenginejournal.com",
         "vivahr.com", "arbdk.info", "stern.de", "skynewsarabia.com", "timesofmalta.com", "gettersiida.net", "best-microcontroller-projects.com", "nwsource.com", "seattletimes.com", "marketwatch.com", "gamestop.com", "themoneyninja.com", "globaltechgadgets.com", "pro-vigil.com", "india.com", "estadao.com.br", "variety.com", "tnscolaire.com", "freeagent.com"] #redirect to https://www.kentlive.news/news/sussex-news/ #redirects to olympics.com from olympic.org

    def requestheaders(self, flow):
        if flow.request.path == "/removehints":
            self.REMOVE_HINTS = True
            flow.request.path = "/"
            ctx.log.error("removeit")
        elif flow.request.path == "/noremovehints":
            flow.request.path = "/"
            self.REMOVE_HINTS = False

    def request(self, flow):
        if flow.request.pretty_host == "example.com" and flow.request.path=="/ourserver":
            print("Set to http")
            flow.request.host = self.POST_SERVER
            flow.request.port = self.POST_SERVER_PORT
            flow.request.scheme = "http"

    def check_content_type(self, flow):
        if not "Content-Type" in flow.response.headers:
            return False
        
        return "text/html" in flow.response.headers["Content-Type"]

    def remove_resource_hints(self, soup):
        # Find all dns-prefetches on the page.
        dns_prefetches = soup.find_all("link", rel="dns-prefetch")
        for dns_prefetch in dns_prefetches:
            dns_prefetch.extract()

        preconnects = soup.find_all("link", rel="preconnect")
        for preconnect in preconnects:
            preconnect.extract()

        return soup

    def get_nr_resource_hints(self, soup):
        nr_dns_prefetches = len(soup.find_all("link", rel="dns-prefetch"))
        nr_preconnects = len(soup.find_all("link", rel="preconnect"))

        ctx.log.error(f"prefetches: {nr_dns_prefetches}, preconncects: {nr_preconnects}")
        return nr_dns_prefetches, nr_preconnects


    def response(self, flow):
        in_urls = any(x in flow.request.host for x in self.urls)
        response_200 = flow.response.status_code == 200 
        content_html = self.check_content_type(flow)
        referer_not_in_header = "Referer" not in flow.request.headers

        if in_urls and response_200 and content_html and referer_not_in_header: 
            ctx.log.error("Yes a website we need")
            html = flow.response.get_text()
            soup = BeautifulSoup(html, "lxml")

            # Add JS snippet to each website regardless of whether we want to remove the resource hints or not.
            js_snippet = soup.new_tag("script")
            js_snippet.string = self.js_snippet 
            soup.body.insert(0, js_snippet)

            # Remove this header so we can send a xmlhttprequest to our local webserver.
            if "Content-Security-Policy" in flow.response.headers:
                del flow.response.headers["Content-Security-Policy"]

            # Disable preloads
            if self.REMOVE_HINTS:
                ctx.log.error("Remove hints")
                soup = self.remove_resource_hints(soup)

  
            flow.response.set_text(str(soup))



   

addons = [Change()]
