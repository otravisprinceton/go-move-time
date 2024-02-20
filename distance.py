###---------------------------------------------------------------------
# First analysis
# Calculate the average distance between moves
###---------------------------------------------------------------------
from sgfmillplus import get_root, is_go, has_multiple_moves, get_player_names, get_player_ranks
import numpy as np
import os
import random
import pandas as pd


BOT_PARTIALS = {"kata", "zen", "petgo", "gnugo", "gomancer", "nexus",
"neural", "sgmdb", "alphacent1", "dcnn", "golois", "bot", "tw001", "pachipachi", "alphago"}

def get_bot_status(root):
    bot_status = {"b":False, "w":False}

    if root.has_property("PB"):
        pb = root.get("PB").lower()
        for partial in BOT_PARTIALS:
            if partial in pb:
                bot_status["b"] = True
                break
    else:
        bot_status["b"] = None
    
    if root.has_property("PW"):
        pw = root.get("PW").lower()
        for partial in BOT_PARTIALS:
            if partial in pw:
                bot_status["w"] = True
                break
    else:
        bot_status["w"] = None

    return bot_status

# Advance past the handicap moves
def skipHandicap(root):
    curr = root[0]
    # If there is a handicap and the first two moves were played by the
    # same color...
    if root.has_property("HA") and curr.get_move()[0] == curr[0].get_move()[0]:
        handicap = root.get("HA")
        try:
            for _ in range(handicap):
                curr = curr[0]
        except:
            return None
    return curr

# For a single game, given the root, get the average distance between
# moves
def process_game(root):
    ranks = get_player_ranks(root)
    names = get_player_names(root)
    bot_status = get_bot_status(root)

    rows = []

    moveNumber = 1
    prev_coord = None

    # Skip past the handicap moves, if they are played out
    curr = skipHandicap(root)
    if not curr:
        return pd.DataFrame(rows, columns=["MoveNum", "Clr", "Name", "Rank", "isBot", "Row", "Col", "Dist"])

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
               names[color],
               ranks[color],
               bot_status[color],
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
        # if moveNumber > 400:
        #     raise Exception()

    return pd.DataFrame(rows, columns=["MoveNum", "Clr", "Name", "Rank", "isBot", "Row", "Col", "Dist"])



def process_all_games(data_folder, filenames, isAlphaGoSelfPlay=False):
    dfs = []
    count = 0
    random.shuffle(filenames)
    for filename in filenames:
        print(count)
        filepath = os.path.join(data_folder, filename.strip())
        print(filepath)

        # Get the root of the file
        try:
            root = get_root(filepath)
        except:
            print("Quitting. Not a valid sgf file.")
            continue

        # Check that the game is valid
        if not (isAlphaGoSelfPlay or is_go(root)):
            print("Quitting. Game not identified as Go.")
            continue
        if not (isAlphaGoSelfPlay or has_multiple_moves(root)):
            print("Quitting. Game has fewer than two moves.")
            continue
        print("Root is valid.")

        game_df = process_game(root)
        game_df["Game"] = filename.strip()
        dfs.append(game_df)
        count += 1


    return pd.concat(dfs, ignore_index=True, axis=0)

def main():
    # Testing
    # filepath = "./test_sgf/byoyomi-HA4PO.sgf"
    # root = from_filepath_get_root(filepath)
    # skipHandicap(root)

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
    res.to_csv("distance_output_handicap_handled.csv", index=False)

if __name__=="__main__":
    main()