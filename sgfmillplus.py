from sgfmill import sgf

_ALPHA = 'ABCDEFGHJKLMNOPQRST' #excludes 'i'

def sgf_to_gtp(sgf_vertex):
    if sgf_vertex:
        return _ALPHA[sgf_vertex[1]] + str(sgf_vertex[0] + 1)
    else:
        return "pass"

def gtp_to_sgf(gtp_vertex):
    if gtp_vertex == "pass":
        return None
    else:
        return (int(gtp_vertex[1:])-1, _ALPHA.index(gtp_vertex[0]))

# Given a file name, create an Sgf_game object and return the root
def get_root(filename):
    with open(filename, "rb") as f:
        game = sgf.Sgf_game.from_bytes(f.read())
        return game.get_root()

# Given the root, return the string name of the game
def which_game(root):
    games_dict = {
        1: "Go",
        2: "Othello",
        3: "chess",
        4: "Gomoku+Renju",
        5: "Nine Men's Morris",
        6: "Backgammon",
        7: "Chinese chess",
        8: "Shogi",
        9: "Lines of Action",
        10: "Ataxx",
        11: "Hex",
        12: "Jungle",
        13: "Neutron",
        14: "Philosopher's Football",
        15: "Quadrature",
        16: "Trax",
        17: "Tantrix",
        18: "Amazons",
        19: "Octi",
        20: "Gess",
        21: "Twixt",
        22: "Zertz",
        23: "Plateau",
        24: "Yinsh",
        25: "Punct",
        26: "Gobblet",
        27: "hive",
        28: "Exxit",
        29: "Hnefatal",
        30: "Kuba",
        31: "Tripples",
        32: "Chase",
        33: "Tumbling Down",
        34: "Sahara",
        35: "Byte",
        36: "Focus",
        37: "Dvonn",
        38: "Tamsk",
        39: "Gipf",
        40: "Kropki"
    }
    try:
        game_key = root.get("GM")
    except:
        raise Exception("Root has no GM key.")
    return games_dict[game_key]

# Given the root, return True if the game is Go
def is_go(root):
    try:
        game_key = root.get("GM")
    except:
        raise Exception("Root has no GM key.")
    return game_key == 1

# Given the root, return True if there is more than one move
def has_multiple_moves(root):
    return len(root) != 0 and len(root[0]) != 0

def main():
    # Testing
    filename = "./test_sgf/byoyomi-HA4PO.sgf"
    root = get_root(filename)
    print(which_game(root))
    print(is_go(root))
    print(has_multiple_moves(root))

if __name__ == "__main__":
    main()