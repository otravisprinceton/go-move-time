from sgfmill import sgf
import subprocess
import re
import os

#------------------------------
# GLOBALS
#------------------------------
NUMJOBS = 300

#------------------------------
# Local
# KATAGO = "katago"
# MODEL = "/usr/local/Cellar/katago/1.11.0/share/katago/g170-b30c320x2-s4824661760-d1229536699.bin.gz"
# LOW_CFG_FILE = "./gtp_low.cfg"
# HIGH_CFG_FILE = "./gtp_high.cfg"

# Della
KATAGO = "/home/otravis/software/KataGoOpenCL/katago"
#MODEL = "/home/otravis/software/g170e-b20c256x2-s5303129600-d1228401921.bin.gz" #20
MODEL = "/home/otravis/software/g170-b30c320x2-s4824661760-d1229536699.bin.gz" #30
#MODEL = "/home/otravis/software/g170-b40c256x2-s5095420928-d1229425124.bin.gz" #40
LOW_CFG_FILE = "/home/otravis/go-move-time/gtp_low.cfg"
HIGH_CFG_FILE = "/home/otravis/go-move-time/gtp_high.cfg"
#------------------------------


MAXMOVES = 3
ALPHA = 'abcdefghjklmnopqrst' #excludes 'i'

BOT_PARTIALS = {"kata", "zen", "petgo", "gnugo", "gomancer", "nexus",
"neural", "sgmdb", "alphacent1", "dcnn", "golois", "bot", "tw001", "pachipachi"}

class MoveInfo:
    def __init__(self, num, color, gtp_vertex, in_overtime):
        self.num = num
        self.color = color
        self.gtp_vertex = gtp_vertex
        self.time_used = None
        self.time_left = None
        self.PUtility = None
        self.PWinrate = None
        self.PScoreLd = None
        self.in_overtime = in_overtime
        self.analyzed = None
        self.cset = {}

    def __str__(self):
        res = f"{self.num:<3} {self.color:<1}"
        res = res +  f" {self.gtp_vertex:<4} {self.time_used:8.3f} {self.time_left:13.3f} {self.in_overtime:<2} {self.analyzed:<2}"
        if self.analyzed:
            res = res + f" {self.PUtility:<10} {float(self.PWinrate):9f} {self.PScoreLd:<9}"
            for cmove in self.cset:
                res = res + f" {cmove:<4}"
                res = res + f" {self.cset[cmove][0]:10}" #utility
                res = res + f" {float(self.cset[cmove][1]):9f}" #winRate
                res = res + f" {self.cset[cmove][2]:9}" #scoreLead
        return res

def from_filepath_get_root(filepath):
    with open(filepath, "rb") as f:
        try:
            game = sgf.Sgf_game.from_bytes(f.read())
        except:
            print("Not a valid sgf file.")
            return False
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

def get_cset_input(root, filepath, csets, whiteIsBot, blackIsBot, startTM, ot):
    kata_list = []
    curr = root[0]

    handicap, curr = handle_handicap(root, curr)

    kata_list.append(" ".join(["loadsgf", filepath, str(handicap + 1)]))
    kata_list.append("kata-time_settings none")

    # track move count
    count = 1

    # track which colors can be analyzed
    if ot.endswith("byo-yomi"):
        print("isByoYomi = True")
        isByoYomi = True
    else:
        print("isByoYomi = False")
        isByoYomi = False
        canadianNum = int(ot[0:ot.index("/")])

    unusable = set()
    canadian = set()
    if whiteIsBot:
        unusable.add('w')
    if blackIsBot:
        unusable.add('b')

    # track time elapsed
    prevTimes = {"w":startTM, "b":startTM}

    while True:
        color, sgf_vertex = curr.get_move()
        if sgf_vertex:
            gtp_vertex = ALPHA[sgf_vertex[1]] + str(sgf_vertex[0] + 1)
        else:
            gtp_vertex = "pass"
        
        newmove = MoveInfo(count, color, gtp_vertex, in_overtime=curr.has_property("O" + color.upper()))
        newTM = curr.get(color.upper() + "L")
        newmove.time_left = newTM
        newmove.time_used = prevTimes[color] - newTM
        prevTimes[color] = newTM
        if color in unusable:
            newmove.analyzed = False
        elif curr.has_property("O" + color.upper()):
            if isByoYomi:
                newmove.analyzed = False
                unusable.add(color)
            elif color in canadian:
                if curr.get("O" + color.upper()) == canadianNum:
                    newmove.analyzed = False
                else:
                    newmove.analyzed = True
                    kata_list.append("clear_cache")
                    kata_list.append("kata-genmove_analyze " + color + " maxmoves " + str(MAXMOVES))
                    kata_list.append("undo")
            else:
                canadian.add(color)
                if curr.get("O" + color.upper()) == canadianNum - 1:
                    newmove.analyzed = False
                else:
                    newmove.analyzed = True
                    kata_list.append("clear_cache")
                    kata_list.append("kata-genmove_analyze " + color + " maxmoves " + str(MAXMOVES))
                    kata_list.append("undo")
        else:
            newmove.analyzed = True
            kata_list.append("clear_cache")
            kata_list.append("kata-genmove_analyze " + color + " maxmoves " + str(MAXMOVES))
            kata_list.append("undo")
        csets.append(newmove)
        kata_list.append(" ".join(["play", color, gtp_vertex]))

        # advance to next move
        if len(curr) == 0 or len(unusable) == 2:
            break
        # if count == 3:
        #     break
        curr = curr[0]
        count += 1

    # return
    cset_input = "\n".join(kata_list) + "\n"
    return cset_input

def handle_handicap(root, curr):
    if root.has_property("HA") and curr.get_move()[0] == curr[0].get_move()[0]:
        # Handicap exists and is played out
        print("Handicap is played out")
        handicap = root.get("HA")
        for _ in range(handicap):
            curr = curr[0]
    else:
        # Handicap is not played out in sgf, or there is no handicap
        print("Handicap is not played out")
        handicap = 0
    return handicap, curr

def get_analysis_input(root, filepath, csets):
    kata_list = []
    curr = root[0]

    handicap, curr = handle_handicap(root, curr)

    kata_list.append(" ".join(["loadsgf", filepath, str(handicap + 1)]))
    kata_list.append("kata-time_settings none")

    # analyze after every
    for move in csets:
        if move.analyzed:
            for cmove in move.cset:
                kata_list.append("play " + move.color + " " + cmove)
                kata_list.append("clear_cache")
                kata_list.append("kata-genmove_analyze maxmoves 1")
                kata_list.append("undo") #undo the genmove
                kata_list.append("undo") #undo the play
        kata_list.append("play " + move.color + " " + move.gtp_vertex)

    # return
    analysis_input = "\n".join(kata_list) + "\n"
    return analysis_input

def runkata(kata_input, cfg_file, output_file):
    cmd = []
    cmd.append(KATAGO)
    cmd.append("gtp")
    cmd.append("-model")
    cmd.append(MODEL)
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

def update_csets_low(csets, file):
    index = 0
    prevLine = ""
    for line in file:
        if line.startswith("play"):
            while not csets[index].analyzed:
                index += 1
            for m, v in zip(re.finditer('move', prevLine), re.finditer('visits', prevLine)):
                csets[index].cset[prevLine[m.end()+1:v.start()-1]] = None
            index += 1
        prevLine = line

def update_csets_high(csets, file):
    index = 0
    prevLine = ""
    for line in file:
        if line.startswith("play"):
            while not csets[index].analyzed:
                index += 1
            for m, v in zip(re.finditer('move', prevLine), re.finditer('visits', prevLine)):
                csets[index].cset[prevLine[m.end()+1:v.start()-1]] = None
            u = re.search('utility', prevLine)
            w = re.search('winrate', prevLine)
            s = re.search('scoreMean', prevLine)
            d = re.search('scoreStdev', prevLine)
            csets[index].PUtility = prevLine[u.end()+1:w.start()-1]
            csets[index].PWinrate = prevLine[w.end()+1:s.start()-1]
            csets[index].PScoreLd = prevLine[s.end()+1:d.start()-1]
            index += 1
        prevLine = line

def update_vocs(csets, file):
    count = 0
    for move in csets:
        if move.analyzed:
            for cmove in move.cset:
                count += 1
                print(count)
                loopCount = 0
                while True and loopCount < 20:
                    loopCount += 1
                    line = file.readline()
                    if "info" in line:
                        u = re.search('utility', line)
                        w = re.search('winrate', line)
                        s = re.search('scoreMean', line)
                        d = re.search('scoreStdev', line)
                        move.cset[cmove] = [line[u.end()+1:w.start()-1]]
                        move.cset[cmove].append(line[w.end()+1:s.start()-1])
                        move.cset[cmove].append(line[s.end()+1:d.start()-1])
                        break
                if loopCount >= 20:
                    raise Exception("Error: Infinite loop in update_vocs")

def save_final(root_node, csets, file):
    file.write(str(root_node))
    file.write("Num C Vtx  TimeUsed TotalTimeLeft OT AN PUtility    PWinrate PScoreLd  AI1  Utility1    Winrate1 ScoreLd1  " + 
    "AI2  Utility2    Winrate2 ScoreLd2  AI3  Utility3    Winrate3 ScoreLd3  AI4  Utility4    Winrate4 ScoreLd4  " +
    "AI5  Utility5    Winrate5 ScoreLd5  AI6  Utility6    Winrate6 ScoreLd6 \n")
    for move in csets:
        file.write(str(move) + "\n")

def findBots(root_node):
    whiteIsBot, blackIsBot = False, False

    pw = root_node.get("PW").lower()
    for partial in BOT_PARTIALS:
        if partial in pw.lower():
            whiteIsBot = True
            print("White is a bot")
            break
    
    pb = root_node.get("PB")
    for partial in BOT_PARTIALS:
        if partial in pb.lower():
            blackIsBot = True
            print("Black is a bot")
            break

    return whiteIsBot, blackIsBot

def main_helper(filename):
    filepath = filename
    csets = []
    print("Loading file " + filepath)

    root_node = from_filepath_get_root(filepath)

    if not root_node:
        print("Quitting.")
        return
    
    if not valid_root(root_node):
        print("Quitting. Not a valid root.")
        return
    print("Root is valid")
    
    startTM = root_node.get("TM")

    ot = root_node.get("OT")

    whiteIsBot, blackIsBot = findBots(root_node)
    if whiteIsBot and blackIsBot:
        print("Quitting. Found two bots.")
        return

    # input for generating cset
    cset_input = get_cset_input(root_node, filepath, csets, whiteIsBot, blackIsBot, startTM, ot)
    print("\n" + "INPUT TO KATAGO (CSETS):\n" + cset_input + "\n")

    for move in csets:
        print(" ".join([str(move.num), move.color, move.gtp_vertex, str(move.time_left), str(move.analyzed), str(move.in_overtime)]))
    print(str(len(csets)))

    # low config
    print("Generating consideration set at low config\n")
    low_output_filepath = filename[:-4] + "-lowset.txt"
    with open(low_output_filepath, "w+") as low_output:
        runkata(cset_input, LOW_CFG_FILE, low_output)
    print("Saved output to " + low_output_filepath)
    with open(low_output_filepath, "r") as low_output:
        update_csets_low(csets, low_output)
    
    # high config
    print("Generating consideration set at high config\n")
    high_output_filepath = filename[:-4] + "-highset.txt"
    with open(high_output_filepath, "w+") as high_output:
        runkata(cset_input, HIGH_CFG_FILE, high_output)
    print("Saved output to " + high_output_filepath)
    with open(high_output_filepath, "r") as high_output:
        update_csets_high(csets, high_output)

    # input for analyzing each move in cset
    analysis_input = get_analysis_input(root_node, filepath, csets)
    print("\n" + "INPUT TO KATAGO (ANALYSIS):\n" + analysis_input + "\n")
    
    voc_output_filepath = filename[:-4] + "-voc.txt"
    with open(voc_output_filepath, "w+") as voc_output:
        runkata(analysis_input, HIGH_CFG_FILE, voc_output)
    print("Saved output to " + voc_output_filepath)
    with open(voc_output_filepath, "r") as voc_output:
        update_vocs(csets, voc_output)

    final_output_filepath = filename[:-4] + "-done.txt"
    with open(final_output_filepath, "w+") as final_output:
        save_final(root_node, csets, final_output)

def main():
    is_array_job = False
    on_cluster = True

    if is_array_job:
        job_idx = int(os.environ["SLURM_ARRAY_TASK_ID"]) - 1
    else:
        job_idx = -1

    if on_cluster:
        data_folder = '/scratch/gpfs/otravis/GoGames'
    else:
        data_folder = '/Users/owentravis/Documents/IW/GoGames'

    # with open(os.path.join(data_folder, "gamesList.txt"), "r") as gamesList:
    #     filenames = gamesList.readlines()

    #filepath = "./test_sgf/byoyomi-NH.sgf"
    #filepath = "./test_sgf/canadian1.sgf"
    #filepath = "../GoGames/201803/201831petgo3-luancaius.sgf"
    #filepath = "../GoGames/201803/201831petgo3-Maxime-2.sgf"
    #filepath = "../GoGames/202110/2021101gomancer-S08310220-3.sgf"
    #filepath = "./test_sgf/byoyomi-HA5NP-pass.sgf"
    # main_helper(filenames[3].strip(), data_folder)

    # for i in range(len(filenames)):
    #     if i % NUMJOBS == job_idx or job_idx == -1:
    #         main_helper(filenames[i].strip(), data_folder)
    main_helper("/scratch/gpfs/otravis/GoGames/201907/2019714geomancer2-petgo-4.sgf")

if __name__ == "__main__":
    main()