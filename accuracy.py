from sgfmillplus import get_root, is_go, has_multiple_moves, get_player_names, get_player_ranks
from sgfmillplus import get_time_system, get_overtime_system, get_game_result
from sgfmill import common
import os
import subprocess
import pandas as pd

NUMJOBS = 300


# Local
# KATAGO = "katago"
# MODEL = "/usr/local/Cellar/katago/1.13.2/share/katago/g170-b30c320x2-s4824661760-d1229536699.bin.gz"
# CFG_FILE = "./gtp_high.cfg"

# Della
KATAGO = "/home/otravis/software/KataGoOpenCL/katago"
MODEL = "/home/otravis/software/g170-b30c320x2-s4824661760-d1229536699.bin.gz" #30
CFG_FILE = "/home/otravis/go-move-time/gtp_high.cfg"

BOT_PARTIALS = {"kata", "zen", "petgo", "gnugo", "gomancer", "nexus",
"neural", "sgmdb", "alphacent1", "dcnn", "golois", "bot", "tw001", "pachipachi"}

class MoveInfo:
    def __init__(self,
                 num,
                 color,
                 gtp_vertex,
                 in_overtime,
                 playerName,
                 gameFile,
                 playerRank,
                 timeSystem,
                 overtimeSystem,
                 gameResult):
        self.num = num
        self.color = color
        self.gtp_vertex = gtp_vertex
        self.in_overtime = in_overtime
        self.playerName = playerName
        self.gameFile = gameFile
        self.playerRank = playerRank
        self.timeSystem = timeSystem
        self.overtimeSystem = overtimeSystem
        self.gameResult = gameResult
        self.played_dx = None
        self.played_dy = None
        self.analyzed = None
        self.bestMove = None
        self.prev_gtp_vertex = None
        self.best_dx = None
        self.best_dy = None
        self.isBot = None

    def __str__(self):
        res = f"{self.num:<3} {self.color:<1}"
        res = res +  f" {self.gtp_vertex:<4} {self.in_overtime:<2} "
        res += f"{self.played_dx} "
        res += f"{self.played_dy} "
        res += str(self.analyzed) + " "
        res += str(self.bestMove) + " "
        res += str(self.prev_gtp_vertex) + " "
        return res

def findBots(root):
    whiteIsBot, blackIsBot = False, False

    pw = root.get("PW").lower()
    for partial in BOT_PARTIALS:
        if partial in pw.lower():
            whiteIsBot = True
            print("White is a bot")
            break
    
    pb = root.get("PB")
    for partial in BOT_PARTIALS:
        if partial in pb.lower():
            blackIsBot = True
            print("Black is a bot")
            break

    return whiteIsBot, blackIsBot

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

def get_katago_input(root, filepath, data_folder, allMovesL, whiteIsBot, blackIsBot):
    kata_list = []
    curr = root[0]

    # Advance past the handicap moves
    try:
        handicap, curr = handle_handicap(root, curr)
    except Exception as e:
        print(e)
        return False
    
    # Command: start katago, load file past handicap
    kata_list.append(" ".join(["loadsgf", os.path.join(data_folder, filepath), str(handicap + 1)]))
    kata_list.append("kata-time_settings none")

    # track move count
    count = 1

    bots = set()
    if whiteIsBot:
        bots.add('w')
    if blackIsBot:
        bots.add('b')

    player_names = get_player_names(root)
    player_ranks = get_player_ranks(root)
    time_system = get_time_system(root)
    overtime_system = get_overtime_system(root)
    game_result = get_game_result(root)

    prev_sgf_vertex = None

    while True:
        color, sgf_vertex = curr.get_move()
        gtp_vertex = common.format_vertex(sgf_vertex)

        moveO = MoveInfo(count,
                         color,
                         gtp_vertex,
                         in_overtime=curr.has_property("O" + color.upper()),
                         playerName = player_names[color],
                         gameFile = filepath,
                         playerRank = player_ranks[color],
                         timeSystem = time_system,
                         overtimeSystem = overtime_system,
                         gameResult = game_result
                         )

        moveO.prev_gtp_vertex = common.format_vertex(prev_sgf_vertex)
        if prev_sgf_vertex and sgf_vertex:
            moveO.played_dx = int(abs(sgf_vertex[1]-prev_sgf_vertex[1]))
            moveO.played_dy = int(abs(sgf_vertex[0]-prev_sgf_vertex[0]))

        moveO.isBot = color in bots

        if color in bots or not prev_sgf_vertex:
            moveO.analyzed = False
        else:
            moveO.analyzed = True
            kata_list.append("clear_cache")
            kata_list.append("kata-genmove_analyze " + color + " maxmoves 3")
            kata_list.append("undo")
    
        allMovesL.append(moveO)
        kata_list.append(" ".join(["play", color, gtp_vertex]))

        if len(curr) == 0:
            break
        
        if sgf_vertex:
            prev_sgf_vertex = sgf_vertex
        curr = curr[0]
        count += 1
    
    return "\n".join(kata_list) + "\n"        

def readOutput(allMovesL, outputF):
    index = 0
    for line in outputF:
        if line.startswith("play"):
            while not allMovesL[index].analyzed:
                index += 1
            moveO = allMovesL[index]
            moveO.bestMove = line.split()[-1]

            index += 1

def addDistancesToMoveO(moveO):
    bestMoveSGF = common.move_from_vertex(moveO.bestMove, 19) #best move in this position
    prevVertexSGF = common.move_from_vertex(moveO.prev_gtp_vertex, 19)
    if bestMoveSGF and prevVertexSGF:
        moveO.best_dx = int(abs(bestMoveSGF[1] - prevVertexSGF[1]))
        moveO.best_dy = int(abs(bestMoveSGF[0] - prevVertexSGF[0]))

# Runs once per game file
def main_helper(filepath, data_folder, dfs):
    allMovesL = []
    print(f"Loading file {filepath}.")

    # Get the root of the file
    try:
        root = get_root(os.path.join(data_folder, filepath))
    except:
        print("Quitting. Not a valid sgf file.")
        return
    
    # Check that the game is valid
    if not is_go(root):
        print("Quitting. Game not identified as Go.")
        return
    if not has_multiple_moves(root):
        print("Quitting. Game has fewer than two moves.")
        return
    print("Root is valid.")
    
    # Identify bots
    whiteIsBot, blackIsBot = findBots(root)
    if whiteIsBot and blackIsBot:
        print("Quitting. Found two bots.")
        return
    
    katago_input = get_katago_input(root, filepath, data_folder, allMovesL, whiteIsBot, blackIsBot)
    if not katago_input:
        print("Quitting. Issue generating katago input.")
        return

    print(katago_input)

    # Local
    # output_filepath = os.path.normpath(os.path.join(data_folder, "../localtmpout/", filepath[7:-4] + "-out.txt"))

    # DELLA
    output_filepath = data_folder[:-7] + "OutputAccuracyFeb13-24/" + filepath[:-4] + "-acc.txt"

    print("Saving to " + str(output_filepath))
    print("Running katago.")
    with open(output_filepath, "w+") as outputF:
        runkata(katago_input, CFG_FILE, outputF)
    print("Saved output to: " + output_filepath)

    with open(output_filepath, "r") as outputF:
        readOutput(allMovesL, outputF)

    # Calculate distances
    for moveO in allMovesL:
        if moveO.analyzed:
            addDistancesToMoveO(moveO)

    allMovesL[0].prev_gtp_vertex = None
    dfs.append(pd.DataFrame([vars(s) for s in allMovesL]))
    

def main():
    dfs = []

    is_array_job = True
    on_cluster = True

    if is_array_job:
        job_idx = int(os.environ["SLURM_ARRAY_TASK_ID"]) - 1
    else:
        job_idx = -1

    if on_cluster:
        data_folder = '/scratch/gpfs/otravis/GoGames'
    else:
        data_folder = '/Users/owentravis/Documents/IW/go-move-time/test_sgf'

    with open(os.path.join(data_folder, "gamesList.txt"), "r") as gamesList:
        filenames = gamesList.readlines()

    for i in range(len(filenames)):
        if i % NUMJOBS == job_idx or job_idx == -1:
            main_helper(filenames[i].strip(), data_folder, dfs)

    # main_helper("test_weird_passes.sgf", data_folder, dfs)

    # Della
    pd.concat(dfs, ignore_index=True).to_csv(f'/scratch/gpfs/otravis/accuracy-{job_idx}.csv')
    # pd.concat(dfs, ignore_index=True).to_csv(f'/scratch/gpfs/otravis/tmp-testing.csv')

    # Local
    # pd.concat(dfs, ignore_index=True).to_csv(f'/Users/owentravis/Documents/IW/go-move-time/tmp-out.csv')



if __name__ == "__main__":
    main()