import os
import sys
from sgfmill import sgf
from collections import defaultdict

# def exploreChildren(node):
#     if node:
#         for child in node:
#             return exploreChildren(child)
#     else:
#         if node.has_property("BL") or node.has_property("WL"):
#             print("Found move times")
#             return True
#         else:
#             print("--")

def find_handicap():
    count_not_ha = 0
    count_ha = 0
    pathname = '/Users/owentravis/Documents/IW/GoGames'
    for directory in os.listdir(pathname):
        directorypath = os.path.join(pathname, directory)
        if directorypath.endswith(".txt"):
            continue
        for filename in os.listdir(directorypath):
            print(f"{count_not_ha}/{count_not_ha + count_ha}")
            print(filename)
            filepath = os.path.join(directorypath, filename)
            if filepath.endswith(".txt"):
                continue
            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    game = sgf.Sgf_game.from_bytes(f.read())
                root_node = game.get_root()
                ha = ""
                try:
                    ha = root_node.get("HA")
                    if not ha:
                        count_not_ha += 1
                    else:
                        count_ha += 1
                except:
                    count_not_ha += 1
    print(count_not_ha)
    print(count_ha)


def removeGames():
    removed_count = 0
    error_count = 0
    directory = sys.argv[1]
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, "rb") as f:
                game = sgf.Sgf_game.from_bytes(f.read())
            root_node = game.get_root()
            #result = exploreChildren(root_node)
            #if result is None:
                #os.remove(filepath)
            try: 
                if root_node.get('TM') == 0:
                    print(filepath)
                    os.remove(filepath)
                    removed_count += 1            
            except KeyError:
                print("ERROR ON " + filepath)
                os.remove(filepath)
                error_count += 1

    print(removed_count)
    print(error_count)

def printDict(dictionary):
    for item in dictionary:
        if dictionary[item] > 800 :
            print(str(item) + " : " + str(dictionary[item]))

def countTimingTypes():
    timing_systems = {}
    pathname = './GoGames'
    for directory in os.listdir(pathname):
        directorypath = os.path.join(pathname, directory)
        for filename in os.listdir(directorypath):
            filepath = os.path.join(directorypath, filename)
            if os.path.isfile(filepath):
                print(filepath)
                with open(filepath, "rb") as f:
                    game = sgf.Sgf_game.from_bytes(f.read())
                root_node = game.get_root()
                try:
                    timing = root_node.get("TM")
                except:
                    timing = "NONE"
                ot = ""
                ot = root_node.get("OT")
                timing_system = str(timing) + " + " + str(ot)
                if timing_system in timing_systems:
                    timing_systems[timing_system] += 1
                else:
                    timing_systems[timing_system] = 1
        printDict(timing_systems)



def countOTTypes():
    ot_types = set()
    count = 0
    pathname = '../GoGames'
    for directory in os.listdir(pathname):
        directorypath = os.path.join(pathname, directory)
        for filename in os.listdir(directorypath):
            filepath = os.path.join(directorypath, filename)
            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    game = sgf.Sgf_game.from_bytes(f.read())
                root_node = game.get_root()
                ot = ""
                try:
                    ot = root_node.get("OT")
                    if ot not in ot_types:
                        print(ot)
                        ot_types.add(ot)
                except:
                    pass
        print(count)
        count += 1

def findType():
    pathname = '../GoGames'
    for directory in os.listdir(pathname):
        directorypath = os.path.join(pathname, directory)
        for filename in os.listdir(directorypath):
            filepath = os.path.join(directorypath, filename)
            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    try:
                        game = sgf.Sgf_game.from_bytes(f.read())
                    except:
                        print(filepath)
                root_node = game.get_root()
                try:
                    handicap = root_node.get("HA")
                except:
                    handicap = "NONE"
                if handicap==2:
                    print(filepath)

def countPlayers():
    pathname = '../GoGames'
    players = defaultdict(int)
    count = 0
    for directory in os.listdir(pathname):
        directorypath = os.path.join(pathname, directory)
        for filename in os.listdir(directorypath):
            filepath = os.path.join(directorypath, filename)
            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    try:
                        game = sgf.Sgf_game.from_bytes(f.read())
                    except:
                        print(filepath)
                    root_node = game.get_root()
                    playerW = root_node.get('PW')
                    playerB = root_node.get('PB')
                    players[playerW] += 1
                    players[playerB] += 1
        count += 1
        print(count)
    for k, v in sorted(players.items(), key=lambda item: item[1], reverse=True):
        if v > 300:
            print(k + ": " + str(v))

def makeGameList():
    pathname = '/Users/owentravis/Downloads/AlphaGoSelfPlay'
    with open("/Users/owentravis/Downloads/agGamesList.txt", "x") as outputFile:
        for directory in os.listdir(pathname):
            directorypath = os.path.join(pathname, directory)
            for filename in os.listdir(directorypath):
                filepath = os.path.join(directorypath, filename)
                if os.path.isfile(filepath):
                    with open(filepath, "rb") as f:
                        try:
                            game = sgf.Sgf_game.from_bytes(f.read())
                            outputFile.write(os.path.join(directory, filename) + "\n")
                        except:
                            print(filepath)

def makeGameListAlphaGoTygem():
    pathname = '/Users/owentravis/Downloads/AlphaGoSelfPlay/tygemfox'
    with open("/Users/owentravis/Downloads/AlphaGoSelfPlay/agGamesList-tygem.txt", "x") as outputFile:
        for filename in os.listdir(pathname):
            filepath = os.path.join(pathname, filename)
            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    try:
                        game = sgf.Sgf_game.from_bytes(f.read())
                        outputFile.write(filename + "\n")
                    except:
                        print(filepath)


def main():
    makeGameListAlphaGoTygem()

if __name__ == "__main__":
    main()
            