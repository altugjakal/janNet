import urllib.robotparser as urobot
from utils.config import Config

# Test with a real Wikipedia URL
url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
r_url = "https://en.wikipedia.org/robots.txt"

rp = urobot.RobotFileParser()
rp.set_url(r_url)
rp.read()

print(f"User-Agent being used: '{Config.USER_AGENT}'")
print(f"Can fetch {url}? {rp.can_fetch(Config.USER_AGENT, url)}")

# Test with wildcard
print(f"Can fetch with '*'? {rp.can_fetch('*', url)}")

# Test if your user agent is in the blocked list
blocked_uas = ['wget', 'HTTrack', 'libwww', 'grub-client', 'WebReaper']
if Config.USER_AGENT in blocked_uas:
    print(f"WARNING: Your user agent '{Config.USER_AGENT}' is explicitly blocked by Wikipedia!")