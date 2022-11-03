# katago gtp -model /usr/local/Cellar/katago/1.11.0/share/katago/g170-b30c320x2-s4824661760-d1229536699.bin.gz 
# -config /usr/local/Cellar/katago/1.11.0/share/katago/configs/gtp_example.cfg


from sgfmill import sgf
import subprocess

def from_filepath_get_root(filepath):
    with open(filepath, "rb") as f:
        game = sgf.Sgf_game.from_bytes(f.read())
    root_node = game.get_root()
    return root_node

def valid_root(root_node):
    # check that the game is Go
    if root_node.get("GM") != 1:
        print("not go")
        return False
    # other checks here?
    # FF --> version of sgf (e.g. 4)
    # CA --> character set (e.g. UTF-8)
    # AP --> app that was used to create sgf
    # ST --> defines variations and markup
    return True

def from_root_get_input(root, filepath):
    kata_list = []
    curr = root[0]

    # set rules and load game past handicap stones
    if root.has_property("HA"):
        handicap = root.get("HA")
    else:
        handicap = 0
    kata_list.append(" ".join(["loadsgf", filepath, str(handicap + 1)]))
    for i in range(handicap):
        curr = curr[0]

    # play all moves
    alpha = 'abcdefghjklmnopqrst' #excludes 'i'
    while True:
        print(curr.get_move())
        color, sgf_vertex = curr.get_move()
        if curr.has_property("O" + color.upper()):
            break
        print(curr.get(color.upper() + "L"))
        gtp_vertex = alpha[sgf_vertex[0]] + str(sgf_vertex[1] + 1)
        kata_list.append(" ".join(["play", color, gtp_vertex]))


        # advance to next move
        if len(curr) == 0:
            break
        curr = curr[0]
    
    # show the board at the end of the game
    kata_list.append("showboard")

    # return
    kata_input = "\n".join(kata_list) + "\n"
    return kata_input

def runkata(kata_input):
    cmd = []
    cmd.append("katago")
    cmd.append("gtp")
    cmd.append("-model")
    cmd.append("/usr/local/Cellar/katago/1.11.0/share/katago/g170-b30c320x2-s4824661760-d1229536699.bin.gz")
    cmd.append("-config")
    cmd.append("/usr/local/Cellar/katago/1.11.0/share/katago/configs/gtp_example.cfg")
    with subprocess.Popen(cmd, text=True,
    stderr=subprocess.PIPE, stdin=subprocess.PIPE) as proc:
        # wait for setup
        while True:
            errLine = proc.stderr.readline()
            print(errLine)
            if "GTP ready" in errLine:
                break
        # play out the game
        outs, errs = proc.communicate(kata_input)

def main():
    filepath = "./GoGames/201803/201831petgo3-luancaius.sgf"
    #filepath = "./GoGames/201803/201831petgo3-Maxime-2.sgf"
    root_node = from_filepath_get_root(filepath)
    if not valid_root(root_node):
        return
    kata_input = from_root_get_input(root_node, filepath)
    print(kata_input)
    runkata(kata_input)

if __name__ == "__main__":
    main()