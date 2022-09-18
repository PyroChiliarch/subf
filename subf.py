#!/usr/bin/python3
# Usage: subf.py domain.com securitytrailsapi

import requests
import re
import sys

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

print("")
print("            ┌───┐")
print("           ┌┘░░░│                           º     º")
print("  ┌────────┴────┴────────────┐      º  O    o  º    º")
print(" ┌┘░░░░░░░░░░░░░░░░░░░░░░░░░░├┐│  o      O º    º")
print(" │░░░subf░subdomain finder░░░│├┤   º O    o  º")
print(" └┐░░░░░░░░░░░░░░░░░░░░░░░░░░├┘│  O  º  o")
print("  └──────────────────────────┘")
print("")


print("Subf v1.0 | Made by Pyrochiliarch")
print("Searches online sites for subdomains")
print("")

if len(sys.argv) != 3:
    print("Invalid number of args")
    print("Usage: subf.py domain.com securitytrailsapikey")
    print("Example: subf.py tesla.com uaGOJYS25GhYV7WPAl91nNPpCT1tzmt8")
    exit()

# Get results form each and remove duplicates
# Removing duplicates is done before merging since we want to let the
# user know how many results there were
results_dnsdumpster = dnsdumpster(sys.argv[1])
results_dnsdumpster = list(dict.fromkeys(results_dnsdumpster))

results_crtsh = crtsh(sys.argv[1])
results_crtsh = list(dict.fromkeys(results_crtsh))

results_securitytrails = securitytrails(sys.argv[1], sys.argv[2])
results_securitytrails = list(dict.fromkeys(results_securitytrails))

# Join together, remove duplictes, sort
results = results_dnsdumpster + results_crtsh + results_securitytrails
results = list(dict.fromkeys(results))
results.sort()



# Print num results from each method
print("# DNS Dumpster: " + str(len(results_dnsdumpster)))
print("# Crt.sh: " + str(len(results_crtsh)))
print("# SecurityTrails: " + str(len(results_securitytrails)))
print("")

# Print Results
print("\n".join(results))