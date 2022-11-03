file1 = open('claimed.txt', 'r')
claimed = file1.readlines()

file2 = open('downloaded.txt', 'r')
downloaded = file2.readlines()

downloaded_map = {}
for line in downloaded:
    line.strip()
    downloaded_map[line] = True

print(len(downloaded_map))

claimed_map = {}
for line in claimed:
    line.strip()
    if line in claimed_map:
        print(line)
    else:
        claimed_map[line] = True

print(len(claimed_map))

