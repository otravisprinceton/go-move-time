import os
from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import sys

def check_validity(my_url):
    try:
        urlopen(my_url)
        print("Valid URL")
    except IOError:
        print ("Invalid URL")
        sys.exit()


def get_sgfs(my_url):
    links = []
    archive_html = urlopen(my_url).read()
    archive_html_page = BeautifulSoup(archive_html, features="lxml")
    for month_link in archive_html_page.find_all('a'):
        current_month_link = month_link.get('href')
        if current_month_link.endswith('html'):
            links.append("http://orb.at/top100/" + current_month_link)

    print("Done getting links")
    print(links[0])

    total_game_count = 0
    for link in links:
        game_links = []
        print("LINK is : " + link)
        month_html = urlopen(link).read()
        month_html_page = BeautifulSoup(month_html, features="lxml")
        month = link[-11:-5]
        path = os.path.join("/Users/owentravis/Documents/IW/GoGames/", month)
        print("Path is: " + path)
        os.mkdir(path)
        print("Now on month: " + month)
        count = 0
        for game_link in month_html_page.find_all('a'):
            current_game_link = game_link.get("href")
            print(current_game_link)
            if current_game_link.endswith('sgf'):
                count += 1
                game_links.append(current_game_link)

        print("Found " + str(count) + " games")
        total_game_count += count
        downloaded_count = 0
        failed_count = 0
        games = len(game_links)
        for i in range(games):
            #print(game_link)
            split_link = game_links[i].split("/")
            fullfilename = path + "/" + split_link[-4] + split_link[-3] + split_link[-2] + split_link[-1]
            print(fullfilename)
            try: 
                urlretrieve(game_links[i], fullfilename)
                downloaded_count += 1
            except:
                failed_count += 1
        
        print("Downloaded: " + str(downloaded_count))
        print("Failed: " + str(failed_count))
def main():
    args = sys.argv
    check_validity(args[1])
    get_sgfs(args[1])


if __name__ == '__main__':
    main()