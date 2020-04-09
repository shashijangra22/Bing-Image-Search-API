from requests import exceptions
import argparse
import requests
import cv2
import os

def getResults(URL,headers,params):
    search = requests.get(URL,headers=headers,params=params)
    search.raise_for_status()
    return search.json()

ap = argparse.ArgumentParser()
ap.add_argument("-k","--key",required=True,help="your API key")
ap.add_argument("-q","--query",required=True,help="search query")
ap.add_argument("-o","--output",required=True,help="path to output directory")
args = vars(ap.parse_args())

API_KEY = args["key"]
MAX_RESULTS = 250
GROUP_SIZE = 50

URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

EXCEPTIONS = set([IOError, FileNotFoundError,
	exceptions.RequestException, exceptions.HTTPError,
	exceptions.ConnectionError, exceptions.Timeout])
    
term = args["query"]
headers = {"Ocp-Apim-Subscription-Key" : API_KEY}
params = {"q": term, "offset": 0, "count": GROUP_SIZE, "aspect":"Square"}

print("[INFO] Searching Bing API for '{}'".format(term))

results = getResults(URL,headers,params)
estNumResults = min(results["totalEstimatedMatches"],MAX_RESULTS)
print("[INFO] {} total results for '{}'".format(estNumResults,
    term))

try:
    os.mkdir(args["output"]+args["query"])
except:
    pass

total = 0

for offset in range(0,estNumResults,GROUP_SIZE):
    
    print("[INFO] making request for group {}-{} of {}...".format(offset, offset + GROUP_SIZE, estNumResults))
    params["offset"] = offset
    results = getResults(URL,headers,params)
    
    print("[INFO] saving images for group {}-{} of {}...".format(offset, offset + GROUP_SIZE, estNumResults))
    for v in results["value"]:
        try:
            print("[INFO] fetching image : {}".format(total))
            r = requests.get(v["contentUrl"], timeout = 30)
            ext = v["contentUrl"][v["contentUrl"].rfind("."):]
            p = os.path.sep.join([args["output"]+args["query"], "{}{}".format(str(total).zfill(8),ext)])
            
            f = open(p,"wb")
            f.write(r.content)
            f.close()
        except Exception as e:
            if type(e) in EXCEPTIONS:
                print("[INFO] skipping image : {}".format(total))
                continue
        
        image = cv2.imread(p)
        if image is None:
            print("[INFO] deleting image : {}".format(total))
            os.remove(p)
            continue
        total+=1