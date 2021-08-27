jjfrom mitmproxy import http
from mitmproxy import ctx
from bs4 import BeautifulSoup, Comment
import datetime

class Change:
    def __init__(self):
        self.REMOVE_PRELOADS = False

        self.POST_SERVER = "192.168.2.7"
        self.POST_SERVER_PORT = 8000

        self.js_snippet = 'function xml_http_post_experiment(url, data, callback) { var req = new XMLHttpRequest(); req.open("POST", url, true); req.send(data); } function calcaulate_performance() { var plt = window.performance.timing.loadEventStart - window.performance.timing.navigationStart; console.log("Calculated PLT: " + plt);  xml_http_post_experiment("https://example.com/ourserver",  plt , null)} window.addEventListener ? window.addEventListener("load", calcaulate_performance, true) : window.attachEvent && window.attachEvent("onload", calcaulate_performance);'

        self.urls = ["bensonbingham.com", "acientistaagricola.pt", "squareinternet.co", "unilad.co.uk", "cruisetricks.de", "africafreak.com", "traineracademy.org", 
        "nsctotal.com.br", "lisakristine.com", "home.pl", "insydo.com", "parse.ly", "elbotola.com", "zksync.io", "screenrant.com", "alternativeto.net", "nbc.com", "grantthornton.se", "agriwebb.com", "haaretz.com", "musicgreatness.com", "cbc.ca",
        "nzz.ch", "fastcompany.com", "kijk.nl", "espncricinfo.com", "sedanmed.ir", "trustpilot.com", "theweathernetwork.com", "theodysseyonline.com", "dji.com", "animoto.com", "el-fenn.com", "newsbreak.com", "blistex.com", "fitchratings.com", "mercan.com", "coindesk.com", "berlinomagazine.com", "coursera.org",
        "elastic.co", "changeinseconds.com", "beegru.com", "scmp.com", "insertlive.com", "jisr.net", "g-talent.net", "noshift.com", "ict.moscow", "bmj.com", "sangoma.com",
        "affirm.com", "ladbible.com", "infobunny.com", "intercom.com",
        "ingenieriareal.com", "sportbible.com", "unclesamsmisguidedchildren.com"]


    def requestheaders(self, flow):
        if flow.request.path == "/removepreload":
            self.REMOVE_PRELOADS = True
            flow.request.path = "/"
            ctx.log.error("removeit")
        elif flow.request.path == "/noremovepreload":
            flow.request.path = "/"
            self.REMOVE_PRELOADS = False

    def request(self, flow):
        if flow.request.pretty_host == "example.com" and flow.request.path=="/ourserver":
            flow.request.host = self.POST_SERVER
            flow.request.port = self.POST_SERVER_PORT
            flow.request.scheme = "http"

    def check_content_type(self, flow):
        if not "Content-Type" in flow.response.headers:
            return False
        
        return "text/html" in flow.response.headers["Content-Type"]

    def response(self, flow):
        # If the website is one of our subjects.
        if any(x in flow.request.host for x in self.urls) and flow.response.status_code == 200 and self.check_content_type(flow) and "Referer" not in flow.request.headers: 
            html = flow.response.get_text()
            soup = BeautifulSoup(html, "lxml")
          
            # Add JS snippet to each website regardless of whether we want to remove the preloads or not.
            js_snippet = soup.new_tag("script")
            js_snippet.string = self.js_snippet 
            soup.body.insert(0, js_snippet)

            # Remove this header so we can send a xmlhttprequest to our local webserver.
            if "Content-Security-Policy" in flow.response.headers:
                del flow.response.headers["Content-Security-Policy"]

            # Remove preloads
            if self.REMOVE_PRELOADS:
                preloads = soup.find_all("link", rel="preload") 
                for preload in preloads:
                    if preload["as"] == "style":
                        preload["rel"] = "stylesheet"
                    else:
                        preload.extract()

            flow.response.set_text(str(soup))

addons = [Change()]
