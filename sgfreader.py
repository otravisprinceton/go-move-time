import os
import sys
from sgfmill import sgf

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
                try:
                    ot = root_node.get("OT")
                except:
                    pass
                timing_system = str(timing) + " + " + str(ot)
                if timing_system in timing_systems:
                    timing_systems[timing_system] += 1
                else:
                    timing_systems[timing_system] = 1
        printDict(timing_systems)

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

def main():
    #removeGames()
    #countTimingTypes()
    findType()

if __name__ == "__main__":
    main()
            