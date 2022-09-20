#!/usr/bin/python3
import requests
import re
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("domain", help="Domain to scan for subdomains eg: hackthebox.com")
parser.add_argument("-a", "--apikey", help="Api key for SecurityTrails")
parser.add_argument("-c", "--clean", action="store_true",
                    help="Display clean output, handy for automation")
args = parser.parse_args()

def securitytrails(target, apikey):

    # Build request
    url = "https://api.securitytrails.com/v1/domain/" + target + "/subdomains"
    headers = {
        "Accept": "application/json",
        "APIKEY": apikey
    }

    #Send request
    response = requests.get(url, headers=headers)

    # Process response from api call
    data = response.json()
    subs = data['subdomains']

    #Append target to include tld
    for index in range(len(subs)):
        subs[index] = subs[index] + "." + target

    return subs

def crtsh(target):
    # Get html of page
    response = requests.get('https://crt.sh' + '?q=' + target)
    html = response.text

    # Regex for Subdomains
    pattern = re.compile(r">([\w\-_\.]*." + target + ")<")  # New Regex with cleaner output
    subs = re.findall(pattern, html)

    return subs # Return results

def dnsdumpster(target):
    # Request the webpage, return html of target
    homepagereq = requests.get('https://dnsdumpster.com/')

    # Extract csrfmiddlewaretoken hidden field
    pattern = re.compile(r"csrfmiddlewaretoken\"[\s\S]value=\"(\w*)\"")
    csrfmiddlewaretoken = re.findall(pattern, homepagereq.text)


    # Send post request
    data = "csrfmiddlewaretoken=" + csrfmiddlewaretoken[0] + "&targetip=" + target + "&user=free"
    headers = {
        'Origin': 'https://dnsdumpster.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.54 Safari/537.36',
        'Referer': 'https://dnsdumpster.com/',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    searchreq = requests.post('https://dnsdumpster.com/', data=data, cookies=homepagereq.cookies, headers=headers)

    # Extract Subdomains
    pattern = re.compile(r">([\w\-_\.]*." + target + ")<")
    subs = re.findall(pattern, searchreq.text)

    return subs

# Allows clean output incase user wants to automate with bash etc.
def loginfo(string):
    if args.clean:
        return
    
    print(string)

    
# Display banner
loginfo("")
loginfo("            ┌───┐")
loginfo("           ┌┘░░░│                           º     º")
loginfo("  ┌────────┴────┴────────────┐      º  O    o  º    º")
loginfo(" ┌┘░░░░░░░░░░░░░░░░░░░░░░░░░░├┐│  o      O º    º")
loginfo(" │░░░Subf Subdomain Finder░░░│├┤   º O    o  º")
loginfo(" └┐░░░░░░░░░░░░░░░░░░░░░░░░░░├┘│  O  º  o")
loginfo("  └──────────────────────────┘")
loginfo("")
loginfo("Subf v1.0 | Made by Pyrochiliarch")
loginfo("Searches online sites for subdomains")
loginfo("")



# Get results form each and remove duplicates
# Removing duplicates is done before merging since we want to let the
# user know how many results there were

# Skip on errors
try:
    results_dnsdumpster = dnsdumpster(args.domain)
    results_dnsdumpster = list(dict.fromkeys(results_dnsdumpster))
except:
    loginfo("Error getting DNS Dumpster results")
    results_dnsdumpster = []

# Skip on errors
try:
    results_crtsh = crtsh(args.domain)
    results_crtsh = list(dict.fromkeys(results_crtsh))
except:
    loginfo("Error getting Crt.sh results")
    results_crtsh = []


    
# Only do securitytrails if an apikey was provided
# Skip on errors
if args.apikey:
    try:
        results_securitytrails = securitytrails(args.domain, args.apikey)
        results_securitytrails = list(dict.fromkeys(results_securitytrails))
    except:
        loginfo("Error getting SecurityTrails results")
        results_securitytrails = []
else:
    loginfo("SecurityTrails Api key not provided, skipping..")
    results_securitytrails = []


    
# Join together, remove duplictes, sort
results = results_dnsdumpster + results_crtsh + results_securitytrails
results = list(dict.fromkeys(results))
results.sort()



# print num results from each method
loginfo("# DNS Dumpster: " + str(len(results_dnsdumpster)))
loginfo("# Crt.sh: " + str(len(results_crtsh)))
loginfo("# SecurityTrails: " + str(len(results_securitytrails)))
loginfo("")



# print Results
print("\n".join(results))
