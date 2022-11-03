from sgfmill import sgf
import subprocess
import re

#------------------------------
# GLOBALS
#------------------------------
MAXMOVES = 3
LOW_CFG_FILE = "./gtp_low.cfg"
HIGH_CFG_FILE = "./gtp_high.cfg"

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

def get_cset_input(root, filepath, csets):
    kata_list = []
    curr = root[0]

    # set rules and load game past handicap stones
    if root.has_property("HA"):
        handicap = root.get("HA")
    else:
        handicap = 0
    print("Handicap is " + str(handicap) + " stones for Black.")
    kata_list.append(" ".join(["loadsgf", filepath, str(handicap + 1)]))
    for i in range(handicap):
        curr = curr[0]

    kata_list.append("kata-time_settings none")

    # analyze after every
    alpha = 'abcdefghjklmnopqrst' #excludes 'i'
    count = 0
    while True:
        color, sgf_vertex = curr.get_move()
        if curr.has_property("O" + color.upper()):
            #in byo-yomi
            break
        kata_list.append("clear_cache")
        kata_list.append("kata-genmove_analyze maxmoves " + str(MAXMOVES))
        kata_list.append("undo")
        print(curr.get(color.upper() + "L"))
        gtp_vertex = alpha[sgf_vertex[1]] + str(sgf_vertex[0] + 1)
        kata_list.append(" ".join(["play", color, gtp_vertex]))
        csets[(color, gtp_vertex)] = set()

        # advance to next move
        if len(curr) == 0:
            break
        if count == 2:
            break
        curr = curr[0]
        count += 1

    # return
    cset_input = "\n".join(kata_list) + "\n"
    return cset_input

def get_analysis_input(root, filepath, csets):
    kata_list = []
    curr = root[0]

    # set rules and load game past handicap stones
    if root.has_property("HA"):
        handicap = root.get("HA")
    else:
        handicap = 0
    print("Handicap is " + str(handicap) + " stones for Black.")
    kata_list.append(" ".join(["loadsgf", filepath, str(handicap + 1)]))
    for i in range(handicap):
        curr = curr[0]

    kata_list.append("kata-time_settings none")

    # analyze after every
    for actual_move in csets:
        color, actual_gtp_vertex = actual_move
        for cmove in csets[actual_move]:
            kata_list.append("play " + color + " " + cmove)
            kata_list.append("clear_cache")
            kata_list.append("kata-genmove_analyze maxmoves 1")
            kata_list.append("undo") #undo the genmove
            kata_list.append("undo") #undo the play
        kata_list.append("play " + color + " " + actual_gtp_vertex)

    # return
    analysis_input = "\n".join(kata_list) + "\n"
    return analysis_input

def runkata(kata_input, cfg_file, output_file):
    cmd = []
    cmd.append("katago")
    cmd.append("gtp")
    cmd.append("-model")
    cmd.append("/usr/local/Cellar/katago/1.11.0/share/katago/g170-b30c320x2-s4824661760-d1229536699.bin.gz")
    cmd.append("-config")
    cmd.append(cfg_file)
    with subprocess.Popen(cmd, text=True,
    stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=output_file) as proc:
        # wait for setup
        while True:
            errLine = proc.stderr.readline()
            if "GTP ready" in errLine:
                break
        # play out the game
        proc.communicate(kata_input)

def update_csets(csets, file):
    for move in csets:
        line = file.readline()
        while "info" not in line:
            line = file.readline()
        csets[move].update(line[m.end()+1:v.start()-1] for m, v in zip(re.finditer('move', line), re.finditer('visits', line)))
        print(csets[move])

def main():
    csets = {}
    #filepath = "./GoGames/201803/201831petgo3-luancaius.sgf"
    filepath = "./GoGames/201803/201831petgo3-Maxime-2.sgf"
    print("Loading file " + filepath)

    root_node = from_filepath_get_root(filepath)
    if not valid_root(root_node):
        print("Quitting. Not a valid root.")
        return
    print("Root is valid.")

    # input for generating cset
    cset_input = get_cset_input(root_node, filepath, csets)
    print("\n" + "INPUT TO KATAGO (CSETS):\n" + cset_input + "\n")

    # low config
    print("Generating consideration set at low config\n")
    low_output_filepath = filepath[:-4] + "-lowset.txt"
    with open(low_output_filepath, "w+") as low_output:
        runkata(cset_input, LOW_CFG_FILE, low_output)
    print("Saved output to " + low_output_filepath)
    with open(low_output_filepath, "r") as low_output:
        update_csets(csets, low_output)
    
    # high config
    print("Generating consideration set at high config\n")
    high_output_filepath = filepath[:-4] + "-highset.txt"
    with open(high_output_filepath, "w+") as high_output:
        runkata(cset_input, HIGH_CFG_FILE, high_output)
    print("Saved output to " + high_output_filepath)
    with open(high_output_filepath, "r") as high_output:
        update_csets(csets, high_output)

    # input for analyzing each move in cset
    analysis_input = get_analysis_input(root_node, filepath, csets)
    print("\n" + "INPUT TO KATAGO (ANALYSIS):\n" + analysis_input + "\n")
    
    voc_output_filepath = filepath[:-4] + "-voc.txt"
    with open(voc_output_filepath, "w+") as voc_output:
        runkata(analysis_input, HIGH_CFG_FILE, voc_output)
    print("Saved output to " + voc_output_filepath)


if __name__ == "__main__":
    main()