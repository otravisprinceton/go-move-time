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

def runkata(kata_input, output_file):
    cmd = []
    cmd.append("katago")
    cmd.append("gtp")
    cmd.append("-model")
    cmd.append("/usr/local/Cellar/katago/1.11.0/share/katago/g170-b30c320x2-s4824661760-d1229536699.bin.gz")
    cmd.append("-config")
    cmd.append("/usr/local/Cellar/katago/1.11.0/share/katago/configs/gtp_example.cfg")
    with subprocess.Popen(cmd, text=True,
    stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=output_file) as proc:
        # wait for setup
        while True:
            errLine = proc.stderr.readline()
            if "GTP ready" in errLine:
                break
        # play out the game
        proc.communicate(kata_input)

def main():
    #filepath = "./GoGames/201803/201831petgo3-luancaius.sgf"
    filepath = "./GoGames/201803/201831petgo3-Maxime-2.sgf"
    print("Loading file " + filepath)
    root_node = from_filepath_get_root(filepath)
    if not valid_root(root_node):
        print("Quitting. Not a valid root.")
        return
    print("Root is valid.")
    kata_input = from_root_get_input(root_node, filepath)
    print("\n" + "INPUT TO KATAGO:\n" + kata_input + "\n")
    with open(filepath[:-4] + "-lowset.txt", "w+") as output_file:
        runkata(kata_input, output_file)
        #waits for katago to finish
    print("Saved output to " + filepath[:-4] + "-lowset.txt")

if __name__ == "__main__":
    main()