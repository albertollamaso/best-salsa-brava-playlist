import os
import time
import requests
import csv
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
driver = Chrome(options=options)


def scrape(findClass):
    list = []

    content = soup.find_all(class_=findClass)
    for element in content:
        list.append(element.string)
    
    return list

def checkDuplicate(title, artist):
    df = pd.read_csv('playlist.csv', delimiter=',')
    tuples = [tuple(x) for x in df.values]
    for t in tuples:
        if (title == t[0] and artist == t[1]):
            print("*** this song already exists in list ***")
            print("song: {}".format(t[0]))
            print("artist: {}".format(t[1]))
            return False
    
    return True


def spotifyToken(AUTH_URL, CLIENT_ID, CLIENT_SECRET):
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    auth_response_data = auth_response.json()

    return auth_response_data['access_token']

def get_spotify_uri(spotifyToken, track, artist):
    query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track".format(track,artist)
    
    response = requests.get(query,headers={"Content-Type": "application/json","Authorization": "Bearer {}".format(spotifyToken)})

    response = response.json()
    
    songs = response["tracks"]["items"]
    if len(songs) > 0 :
        url = songs[0]["external_urls"]["spotify"]
        uri = songs[0]["uri"]
        return url
    else:
        return "not found"

titleBlacklist = ["Advert", "Advert:"]
artistBlacklist = ["Publicidad", "Colombia Salsa Dura"]


SOURCE_URL = os.getenv('SOURCE_URL')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/api/token'

# Opening the CSV File Handle
csv_file = open('playlist.csv', 'a')

# Create the csv writer
writer = csv.writer(csv_file)

driver.get(SOURCE_URL)

# Delay to load the contents of the HTML FIle
time.sleep(2)

# Parse processed webpage with BeautifulSoup
soup = BeautifulSoup(driver.page_source, features="html.parser")

# get spotify access token
spotifyAuthToken = spotifyToken(SPOTIFY_AUTH_URL, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)


# scrape content
titles = scrape("song-name")
artists = scrape("artist-name")


for (title, artist) in zip(titles, artists):
    if (title not in titleBlacklist) and (artist not in artistBlacklist):
        if checkDuplicate(title, artist):
            spotifyTrackUrl = get_spotify_uri(spotifyAuthToken, title, artist)
            print("Adding song:")
            print("title:  {}".format(title))
            print("artist: {}".format(artist))
            print("spotify url: {}".format(spotifyTrackUrl))
            writer.writerow([title, artist, spotifyTrackUrl])
            print("--------------------------------------------------------")
