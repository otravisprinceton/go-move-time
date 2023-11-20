from sgfmill import sgf
import numpy as np
import os
import random
import pandas as pd


BOT_PARTIALS = {"kata", "zen", "petgo", "gnugo", "gomancer", "nexus",
"neural", "sgmdb", "alphacent1", "dcnn", "golois", "bot", "tw001", "pachipachi", "alphago"}

# Given an sgf filepath, return the root node
def from_filepath_get_root(filepath):
    with open(filepath, "rb") as f:
        try:
            game = sgf.Sgf_game.from_bytes(f.read())
        except:
            print("Not a valid sgf file.")
            return None
    root_node = game.get_root()
    return root_node

# Given a root node, check that it's valid
def valid_root(root_node):
    # check that the game is Go
    if (not root_node.has_property("GM")) or root_node.get("GM") != 1:
        print("not go")
        return False
    if len(root_node) == 0:
        print("no moves were made")
        return False
    if len(root_node[0]) == 0:
        print("only one move was made")
        return False

    # other checks here?
    # FF --> version of sgf (e.g. 4)
    # CA --> character set (e.g. UTF-8)
    # AP --> app that was used to create sgf
    # ST --> defines variations and markup
    return True

def get_ranks(root):
    ranks = {"b":None, "w":None}
    if root.has_property("BR"):
        ranks["b"]=root.get("BR")
    if root.has_property("WR"):
        ranks["w"]=root.get("WR")
    return ranks
    
def get_names(root):
    names = {"b":None, "w":None}
    if root.has_property("PB"):
        names["b"]=root.get("PB")
    if root.has_property("PW"):
        names["w"]=root.get("PW")
    return names

def get_bot_status(root):
    bot_status = {"b":False, "w":False}

    if root.has_property("PB"):
        pb = root.get("PB").lower()
        for partial in BOT_PARTIALS:
            if partial in pb:
                bot_status["b"] = True
                print("Black is a bot")
                break
    else:
        bot_status["b"] = None
    
    if root.has_property("PW"):
        pw = root.get("PW").lower()
        for partial in BOT_PARTIALS:
            if partial in pw:
                bot_status["w"] = True
                print("White is a bot")
                break
    else:
        bot_status["w"] = None

# For a single game, given the root, get the average distance between
# moves
def process_game(root):
    ranks = get_ranks(root)
    names = get_names(root)

    rows = []

    moveNumber = 1
    prev_coord = None
    curr = root[0]
    while True:
        color, coord = curr.get_move()
        if coord:
            coord_toPrint = coord
            if prev_coord:
                dist = abs(coord[0]-prev_coord[0]) + abs(coord[1]-prev_coord[1])
            else:
                dist = None
        else:
            coord_toPrint = (None, None)
            dist = None
        row = [moveNumber,
               color,
               ranks[color],
               coord_toPrint[0],
               coord_toPrint[1],
               dist]
        rows.append(row)

        # Exit or advance the loop
        if len(curr) == 0:
            break
        prev_coord = coord
        curr = curr[0]
        moveNumber += 1

    return pd.DataFrame(rows, columns=["MoveNum", "Clr", "Rank", "Row", "Col", "Dist"])



def process_all_games(data_folder, filenames, isAlphaGoSelfPlay=False):
    dfs = []
    count = 0
    random.shuffle(filenames)
    for filename in filenames:
        print(count)
        filepath = os.path.join(data_folder, filename.strip())
        print(filepath)
        root = from_filepath_get_root(filepath)
        if not root:
            print("Quitting.")
            continue
        if not (isAlphaGoSelfPlay or valid_root(root)):
            print("Quitting. Not a valid root.")
            continue

        game_df = process_game(root)
        game_df["Game"] = filename.strip()
        dfs.append(game_df)
        count += 1

        if count > 10:
            break

    return pd.concat(dfs, ignore_index=True, axis=0)

def main():
    human_data_folder = '/Users/owentravis/Documents/IW/GoGames'
    with open(os.path.join(human_data_folder, "gamesList.txt"), "r") as gamesList:
        human_filenames = gamesList.readlines()
    human_df = process_all_games(human_data_folder, human_filenames)
        
    alphago_data_folder = '/Users/owentravis/Downloads/AlphaGoSelfPlay'
    with open(os.path.join(alphago_data_folder, "agGamesList.txt"), "r") as agGamesList:
        alphago_filenames = agGamesList.readlines()
    ag_df = process_all_games(alphago_data_folder, alphago_filenames, True)

    ag_df["isAlphaGo"] = 1
    human_df["isAlphaGo"] = 0

    res = pd.concat([ag_df, human_df], ignore_index=True, axis=0)
    res.to_csv("distance_output.csv", index=False)

if __name__=="__main__":
    main()