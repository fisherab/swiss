from swiss import Logic
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(filename='cmd.log', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)

class Cmd(object):

    @staticmethod
    def getWithDefaults(name, defaultValue):
        s = input(name + " (" + str(defaultValue) + "): ").strip();
        if s == "": return defaultValue
        if s[0].upper() == "T": return True
        if s[0].upper() == "F": return False
        return int(s)

    def run(self):
        logger.info("We're running")
        tournament = Logic.Tournament()
        journal = Path("journal.txt")
        journalRecovery = journal.is_file()
        lines = []
        if journalRecovery:
            tournament.recoverFromLog(journal)
            tournament.prepareRound()
        
        else: # No journal recovery
            byeScore = Cmd.getWithDefaults("byeScore", 26);
            maxCombis = Cmd.getWithDefaults("maxCombis", 1000000000);
            enoughGood = Cmd.getWithDefaults("enoughGood", 100);
            numLawns = Cmd.getWithDefaults("numLawns", 2);
            randomStart = Cmd.getWithDefaults("randomStart", True);
            tournament.setOpts(byeScore, maxCombis, enoughGood, numLawns, randomStart)
            while True:
                player = input("player (empty to end, finish name with -P or -S if CVD): ").strip()
                if player == "": break
                if player.upper()[-2:] == "-P":
                    tournament.addPlayer(player[:-2].strip(), Logic.Colours.PRIMARY)
                elif player.upper()[-2:] == "-S":
                    tournament.addPlayer(player[:-2].strip(), Logic.Colours.SECONDARY)
                else:
                    tournament.addPlayer(player.strip())
            tournament.start()
          
        print("Rounds KO:" + str(tournament.getKORounds()) + ", Max:" + str(tournament.getMaxRounds())
                + ", Recommended:" + str(tournament.getRecRounds()))

        finished = False
        
        while not finished:
            roundNum = len(tournament.rounds)
            round = tournament.rounds[roundNum - 1]
            print("Starting round", roundNum)
            tournament.setByeScores()
            tournament.makeGamesChoices(round)
            roundInProgress = True
            while roundInProgress:
                cmd = input("Game number, S(tatus), E(nd round) ").upper().strip()
                if cmd == "S":
                    ngame = 1
                    for i in range(len(round) // 2):
                        p1 = round[2 * i]
                        p2 = round[2 * i + 1]
                        if p1[0] != "Bye" and p2[0] != "Bye":
                            print("Game",ngame, ":",p1,"vs",p2)
                            ngame += 1
                elif cmd == "E":
                    if Cmd.isExitAllowed(round): roundInProgress = False        
                else:
                    try:
                        ngame = 1
                        for i in range(len(round) // 2):
                            p1 = round[2 * i]
                            p2 = round[2 * i + 1]
                            if p1[0] != "Bye" and p2[0] != "Bye":
                                ngame += 1
                            if ngame - 1 == int(cmd):
                                Cmd.storeScores(round, i)
                                break
                    except ValueError:
                        print("Invalid input")
             
            try:
                tournament.writeLog(round, roundNum == 1)
            except Exception:
                print("Failed to write log for round", round)

            tournament.computeRanking()
            print("Ranking after round " + str(roundNum) + ":", end="")
            for name in tournament.ranking:
                print(" " + name + ":" + str(tournament.players[name].games), end="")
            print()
            
            finishChoiceMade = False
            while not finishChoiceMade:
                if roundNum >= tournament.getRecRounds(): print("You have completed the recommended number of rounds.")
                if roundNum >= tournament.getMaxRounds():
                    print("You have completed the maximum number of rounds.");
                    finished = True
                    finishChoiceMade = True
                    continue
                
                cmd = input("FINISH (tournament), NEXT (to start next round) ").upper().strip()
                if cmd == "FINISH":
                    finished = True;
                    finishChoiceMade = True;
                elif cmd == "NEXT":
                    try:
                        tournament.prepareRound()
                        finishChoiceMade = True
                    except Exception as e:
                        print(e)
                        print("Tournament will finish")
                        finished = True
                        finishChoiceMade = True
                        continue
  
        source = Path("journal.txt")
        strDate = datetime.today().strftime("%Y-%m-%d")
        target = Path("gamelog-" + strDate + ".txt")
        try:
            source.rename(target)
        except Exception as e:
            print("You have failed to rename", source, "to", target)
            print(e)

        fr = tournament.getFinalRanking();
        print(fr)

        fmt = "{:2} {:.<18} {:4} : {:5} {:>12} {:>10} {:>9}"
        print(fmt.format(" #", "name", "wins", "hoops", "lawns", "primaryXS", "starts"))
        for i in range(1,len(tournament.players)+1):
            for name, val in fr.items():
                if val == i:
                    p = tournament.players[name]
                    wins = p.games
                    hoops = p.hoops
                    prim = p.primarys-p.secondarys
                    lawns = []
                    for j in range(tournament.numLawns):
                        if j in p.lawns: lawns.append(p.lawns[j])
                        else: lawns.append(0)
                    starts = p.startCount
                    print(fmt.format(i, name, wins, hoops, str(lawns), prim, starts))

    @staticmethod
    def storeScores(round, i):
        '''
        Store score at offset i in the round.
        '''
        if i < 0 or i >= len(round) // 2:
            print ("Invalid game number")
            return
        p1 = round[2 * i]
        p2 = round[2 * i + 1]
        
        if p1[0] == "Bye" or p2[0] == "Bye":
            print ("Invalid game number")
            return
           
        if p1[1] != 0 or p2[1] != 0:
            if input("Enter OVERWRITE to change score ").upper().strip() != "OVERWRITE": return
    
        try:
            s1 = int(input("Score for: " + p1[0] + ": "))
            s2 = int(input("Score for: " + p2[0] + ": "))
        except ValueError:
            print("Scores must be integers")
            return
        
        if s1 == s2:
            print("Draws are not allowed")
            return
        
        p1[1] = s1
        p2[1] = s2

    @staticmethod
    def isExitAllowed(round):
        exitAllowed = True
        ngame = 1;
        for i in range(len(round) // 2):
            p1 = round[2 * i]
            p2 = round[2 * i + 1]
            if p1[0] != "Bye" and p2[0] != "Bye":
                if p1[1] == 0 and p2[1] == 0:
                    print("Game", ngame, "has no score recorded")
                    exitAllowed = False
                ngame += 1
        return exitAllowed

def main():
    cmd = Cmd()
    cmd.run()

if __name__ == "__main__":
    main()
