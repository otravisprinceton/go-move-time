import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np


def addWinrateVOC(df):
    lowWinrateOpp = df['Winrate1']
    myLowWinrate = 1 - lowWinrateOpp
    minWinrateOpp = df[['Winrate1', 'Winrate2', 'Winrate3', 'Winrate4', 'Winrate5', 'Winrate6']].min(axis=1)
    myMaxWinrate = 1 - minWinrateOpp
    df['WinrateVOC'] = myMaxWinrate - myLowWinrate

def addScoreLdVOC(df):
    lowScoreLdOpp = df['ScoreLd1']
    myLowScoreLd = -lowScoreLdOpp
    minScoreLdOpp = df[['ScoreLd1', 'ScoreLd2', 'ScoreLd3', 'ScoreLd4', 'ScoreLd5', 'ScoreLd6']].min(axis=1)
    myMaxScoreLd = -minScoreLdOpp
    df['ScoreLdVOC'] = myMaxScoreLd - myLowScoreLd

def addUtilityVOC(df):
    lowUtilityOpp = df['Utility1']
    minUtilityOpp = df[['Utility1', 'Utility2', 'Utility3', 'Utility4', 'Utility5', 'Utility6']].min(axis=1)
    df['UtilityVOC'] = lowUtilityOpp - minUtilityOpp

def getRank(row, br, wr):
    if row["C"] == "b":
        return br
    return wr

def get_midpoints(x):
    return (x[1:] + x[:-1]) / 2

def main():
    dfs = []
    timeSysSet = set()
    count = 0
    pathname = '/Users/owentravis/Documents/IW/OutputCL-1'
    for directory in os.listdir(pathname):
        directorypath = os.path.join(pathname, directory)
        for filename in os.listdir(directorypath):
            filepath = os.path.join(directorypath, filename)
            # print("On file " + filename + " " + str(count))
            with open(filepath, "r") as f:
                tm = "None"
                ot = "None"
                br = None
                wr = None
                nskip = 0
                try:
                    for line in f:
                        if line.startswith('OT'):
                            ot = line[3:-2]
                        elif line.startswith('BR'):
                            br = line[3:-2]
                        elif line.startswith("WR"):
                            wr = line[3:-2]
                        elif line.startswith("TM"):
                            tm = line[3:-2]
                        elif line.startswith("RE"):
                            winner = line[3]
                            if winner == "V" or winner == "v":
                                print(filepath)
                        elif line.startswith("Num"):
                            break
                        nskip += 1
                except:
                    print(filepath)
            timeSys = tm + " " + ot
            dfCurr = pd.read_csv(filepath, delim_whitespace=True, skiprows=nskip, header=0)
            dfCurr = dfCurr[dfCurr.AN != 0]
            dfCurr["TimeSys"] = timeSys
            dfCurr["Winner"] = winner
            dfCurr["Rank"] = dfCurr.apply(lambda row: getRank(row, br, wr), axis=1)
            timeSysSet.add(timeSys)
            dfs.append(dfCurr)
            count += 1
    df = pd.concat(dfs)

    print(timeSysSet)
    df = df.reset_index()
    addWinrateVOC(df)
    addScoreLdVOC(df)
    addUtilityVOC(df)

    df.to_csv("/Users/owentravis/Documents/IW/df-all.csv")

    # df = pd.read_csv("/Users/owentravis/Documents/IW/df.csv")


    # for timeSys in df['TimeSys'].unique():
    #     fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
    #     currdf = df[(df["TimeSys"] == timeSys) &
    #     (df["OT"] == 0) &
    #     (df["TimeUsed"] >= 0) &
    #     (df["Rank"].isin(["7d", "8d", "9d"]))
    #     ]
    #     n_voc_bin_bounds = 10
    #     voc_bin_bounds = np.linspace(-.01,.4,n_voc_bin_bounds)
    #     voc_bin_bounds = np.append(voc_bin_bounds, 1)
    #     voc_bin_labels = get_midpoints(voc_bin_bounds)

    #     currdf['wr_voc_bin'] = pd.cut(currdf['WinrateVOC'], voc_bin_bounds, labels=voc_bin_labels)
    #     currdf_groupby_wr = currdf.groupby('wr_voc_bin').agg({'TimeUsed': ['mean']}).reset_index()
    #     ax1.scatter(currdf_groupby_wr.wr_voc_bin, currdf_groupby_wr.TimeUsed)

    #     currdf['sl_voc_bin'] = pd.cut(currdf['ScoreLdVOC'], voc_bin_bounds, labels=voc_bin_labels)
    #     currdf_groupby_sl = currdf.groupby('sl_voc_bin').agg({'TimeUsed': ['mean']}).reset_index()
    #     ax2.scatter(currdf_groupby_sl.sl_voc_bin, currdf_groupby_sl.TimeUsed)

    #     currdf['u_voc_bin'] = pd.cut(currdf['UtilityVOC'], voc_bin_bounds, labels=voc_bin_labels)
    #     currdf_groupby_u = currdf.groupby('u_voc_bin').agg({'TimeUsed': ['mean']}).reset_index()
    #     ax3.scatter(currdf_groupby_u.u_voc_bin, currdf_groupby_u.TimeUsed)
    #     print(timeSys)
    #     plt.show()

if __name__ == '__main__':
    main()