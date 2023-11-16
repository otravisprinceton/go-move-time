from sgfmill import sgf
import numpy as np
import os
import random
import pandas as pd

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

# Given a root node, check for validity
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


def get_mean_distance(root):
    distances = []
    curr = root[0]
    _, prev_coord = curr.get_move()
    if not prev_coord:
        print("Game starts with a pass")
        return None
    curr = curr[0]
    while True:
        _, coord = curr.get_move()
        if not coord:
            break
        dist = abs(coord[1] - prev_coord[1]) + abs(coord[0]-prev_coord[0])
        distances.append(dist)
        prev_coord = coord
        if len(curr) == 0:
            break
        curr = curr[0]
    if distances:
        return np.mean(distances)
    return None

def get_all_mean_distances(data_folder, filenames):
    mean_dists = []
    count = 0
    for filename in filenames:
        print(count)
        filepath = os.path.join(data_folder, filename.strip())
        root_node = from_filepath_get_root(filepath)
        if not root_node:
            print("Quitting.")
            continue
        if not valid_root(root_node):
            print("Quitting. Not a valid root.")
            continue
        print("Root is valid")

        mean_dist = get_mean_distance(root_node)
        if mean_dist:
            mean_dists.append(mean_dist)
        count += 1
        if count > 3000:
            break

    return mean_dists

def main():
    human_data_folder = '/Users/owentravis/Documents/IW/GoGames'
    with open(os.path.join(human_data_folder, "gamesList.txt"), "r") as gamesList:
        human_filenames = gamesList.readlines()
    human_mean_dists = get_all_mean_distances(human_data_folder, human_filenames)
        
    alphago_data_folder = '/Users/owentravis/Downloads/AlphaGoSelfPlay'
    with open(os.path.join(alphago_data_folder, "agGamesList.txt"), "r") as agGamesList:
        alphago_filenames = agGamesList.readlines()
    alphago_mean_dists = get_all_mean_distances(alphago_data_folder, alphago_filenames)

    print(len(human_mean_dists))
    print(np.mean(human_mean_dists))
    print(len(alphago_mean_dists))
    print(np.mean(alphago_mean_dists))




if __name__=="__main__":
    main()