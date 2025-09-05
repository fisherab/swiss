import unittest

from math import comb
from swiss import Logic
from datetime import datetime
from pathlib import Path
import random
import logging
import os

logging.basicConfig(filename='test.log', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)

class AllTests(unittest.TestCase):

    def combis(self, gamesPerRound, numClash, enoughGood = None):
        games= []
        for i in range(gamesPerRound): games.append(Logic.Game("Win " + str(i), "Lose " + str(i),i*i))
        for i in range(numClash): games.append(Logic.Game("Win 0", "Clash " + str(i),i *1))
        random.shuffle(games)
        start = datetime.now()
        res = Logic.Tournament.bestCombinations(games,gamesPerRound, set(), 0, set(), enoughGood)
        t = datetime.now()
        logger.info("For %s combinations and enoughGood %s gave %s good with sq %s and took %s", comb(len(games), gamesPerRound), enoughGood, res.numGood, res.bestSumSquares, t-start)
        return res

    def testCombinationsFast(self):
        res = self.combis(gamesPerRound = 6, numClash = 3, enoughGood = 4)
        self.assertEqual(4,res.numGood)
        self.assertEqual(55,res.bestSumSquares)
        res = self.combis(gamesPerRound = 6, numClash = 3)
        self.assertEqual(4,res.numGood)
        self.assertEqual(55,res.bestSumSquares)
        self.combis(gamesPerRound = 8, numClash = 50, enoughGood = 4)
        self.combis(gamesPerRound = 16, numClash = 500, enoughGood = 1)
        self.combis(gamesPerRound = 16, numClash = 500, enoughGood = 4)
 
        self.combis(gamesPerRound = 8, numClash = 500, enoughGood = 1)
        self.combis(gamesPerRound = 8, numClash = 500, enoughGood = 4)
        self.combis(gamesPerRound = 8, numClash = 500, enoughGood = 100)
        res = self.combis(gamesPerRound = 8, numClash = 500)
        self.assertEqual(501,res.numGood)
        self.assertEqual(140,res.bestSumSquares)

    @unittest.skip("Takes a few minutes")
    def testCombinationsSlow(self):
        self.combis(gamesPerRound = 16, numClash = 500, enoughGood = 100)

    def testCreate1(self):
        sw =  Logic.Tournament();
        sw.setOpts(26, 1000000000, 100, 4, True)
        sw.addPlayer("A", Logic.Colours.PRIMARY)
        sw.addPlayer("B", Logic.Colours.SECONDARY)
        sw.addPlayer("C")
        sw.addPlayer("D")
        sw.addPlayer("E")
        sw.addPlayer("F")
        sw.addPlayer("G")
        sw.addPlayer("H")
                
        self.assertEqual(3, sw.getKORounds())
        self.assertEqual(7, sw.getMaxRounds())
        self.assertEqual(5, sw.getRecRounds())
        self.assertEqual(Logic.Colours.PRIMARY, sw.players["A"].colours)
        self.assertEqual(Logic.Colours.SECONDARY, sw.players["B"].colours)
        self.assertEqual(None, sw.players["C"].colours)

    def testCreate2(self):
        sw =  Logic.Tournament();
        sw.setOpts(26, 1000000000, 100, 4, False)
        sw.addPlayer("A", Logic.Colours.PRIMARY)
        sw.addPlayer("B", Logic.Colours.SECONDARY)
        sw.addPlayer("C")
        sw.addPlayer("D")
        sw.addPlayer("E")
        sw.addPlayer("F")
        sw.addPlayer("G")
        sw.addPlayer("H")
        sw.addPlayer("I")
                
        self.assertEqual(4, sw.getKORounds())
        self.assertEqual(8, sw.getMaxRounds())
        self.assertEqual(6, sw.getRecRounds())

    def testGetBest1(self):
        sw =  Logic.Tournament();
        sw.setOpts(26, 1000000000, 100, 4, False)
        for l in "ABCDEFGH": sw.addPlayer(l)
        if len(sw.players) % 2 == 1: sw.players["Bye"] = Player("Bye", None)
        sw.rounds.append([['G', 25], ['F', 26], ['D', 15], ['H', 12], ['E', 16], ['C', 21], ['B', 24], ['A', 25]]); sw.computeRanking()
        sw.rounds.append([['F', 22], ['D', 25], ['C', 16], ['A', 18], ['G', 9], ['H', 4], ['E', 15], ['B', 26]]); sw.computeRanking()
        sw.rounds.append([['D', 6], ['A', 9], ['F', 18], ['C', 19], ['G', 9], ['B', 25], ['H', 17], ['E', 20]]); sw.computeRanking()
        sw.rounds.append([['A', 6], ['F', 2], ['D', 16], ['C', 20], ['G', 0], ['E', 14], ['B', 22], ['H', 8]]); sw.computeRanking()
       
        logger.info("Ranking after round 4") 
        res = ""
        for name in sw.ranking:
            res += name + ": " + str(sw.players[name].games) + "  "
        logger.info(res)
            
        fr = sw.getFinalRanking()
        self.assertDictEqual({'A': 1, 'B': 2, 'C': 3, 'E': 4, 'D': 5, 'F': 6, 'G': 7, 'H': 8}, fr)

    def testGetBest2(self):
        sw =  Logic.Tournament();
        sw.setOpts(26, 1000000000, 100, 4, False)
        for l in "ABCDEFGH": sw.addPlayer(l)
        if len(sw.players) % 2 == 1: sw.players["Bye"] = Player("Bye", None)
        sw.rounds.append([['G', 25], ['F', 26], ['D', 15], ['H', 12], ['E', 16], ['C', 21], ['B', 24], ['A', 25]]); sw.computeRanking()
        sw.rounds.append([['F', 22], ['D', 25], ['C', 16], ['A', 18], ['G', 9], ['H', 4], ['E', 15], ['B', 26]]); sw.computeRanking()
        sw.rounds.append([['D', 6], ['A', 9], ['F', 18], ['C', 19], ['G', 9], ['B', 25], ['H', 17], ['E', 20]]); sw.computeRanking()
        sw.rounds.append([['A', 2], ['F', 6], ['D', 16], ['C', 20], ['G', 0], ['E', 14], ['B', 22], ['H', 8]]); sw.computeRanking()
       
        logger.info("Ranking after round 4") 
        res = ""
        for name in sw.ranking:
            res += name + ": " + str(sw.players[name].games) + "  "
        logger.info(res)
            
        fr = sw.getFinalRanking()
        self.assertDictEqual({'A': 1, 'B': 2, 'C': 3, 'F': 4, 'E': 5, 'D': 6, 'G': 7, 'H': 8}, fr)

    def testGetBest3(self):
        sw =  Logic.Tournament();
        sw.setOpts(26, 1000000000, 100, 4, False)
        for l in "ABCDEFGH": sw.addPlayer(l)
        if len(sw.players) % 2 == 1: sw.players["Bye"] = Player("Bye", None)
        sw.rounds.append([['D', 15], ['H', 9], ['G', 21], ['E', 25], ['A', 26], ['B', 24], ['F', 13], ['C', 22]]); sw.computeRanking()
        sw.rounds.append([['D', 17], ['E', 6], ['A', 26], ['C', 23], ['H', 10], ['G', 11], ['B', 18], ['F', 0]]); sw.computeRanking()
        sw.rounds.append([['D', 5], ['A', 13], ['E', 22], ['C', 24], ['G', 20], ['B', 22], ['H', 15], ['F', 17]]); sw.computeRanking()
        sw.rounds.append([['A', 10], ['E', 4], ['D', 14], ['C', 23], ['G', 25], ['F', 26], ['B', 24], ['H', 16]]); sw.computeRanking()
       
        logger.info("Ranking after round 4") 
        res = ""
        for name in sw.ranking:
            res += name + ": " + str(sw.players[name].games) + "  "
        logger.info(res)
            
        fr = sw.getFinalRanking()
        self.assertDictEqual({'A': 1, 'C': 2, 'B': 3, 'F': 4, 'D': 5, 'E': 6, 'G': 7, 'H': 8}, fr) 

    def testStarts(self):
        for n in range(1000):
            self.testStart()
         
    def testStart(self):
        sw =  Logic.Tournament();
        sw.setOpts(26, 1000000000, 100, 4, True)
        sw.addPlayer("A", Logic.Colours.PRIMARY)
        sw.addPlayer("B", Logic.Colours.SECONDARY)
        sw.addPlayer("C")
        sw.addPlayer("D")
        sw.addPlayer("E")
        sw.addPlayer("F")
        sw.addPlayer("G")
        sw.addPlayer("H")
                     
        sw.start();
 
        for j in range(sw.getMaxRounds()):
            if j != 0:
                sw.computeRanking()
                logger.info("Ranking after round " + str(j) + " ")
                res = ""
                for name in sw.ranking:
                    res += name + ": " + str(sw.players[name].games) + "  "
                logger.info(res)
                sw.prepareRound()
            
            round = sw.rounds[j]
            if len(round) == 0:
                logger.info("Stopping early as no more game combination after round " + str(j))
                j -= 1
                break
            else:
                sw.setByeScores();
                sw.makeGamesChoices(round);
                ngames = len(round) // 2;
     
                for i in range(ngames):
                    p1 = round[2 * i]
                    p2 = round[2 * i + 1]
                    if p1[0] != "Bye" and p2[0] != "Bye":
                        badScore = random.randrange(26);
                        goodScore = badScore + 1 + random.randrange(26 - badScore);
                        if p1[0] < p2[0]:
                            p1[1] = goodScore
                            p2[1] = badScore
                        else:
                            p1[1] = badScore
                            p2[1] = goodScore
                        
                logger.info("Score in round %s : %s", j + 1, round)
            
        sw.computeRanking()
        logger.info("Ranking after round " + str(j + 1) + " ")
        res = ""
        for name in sw.ranking:
            res += name + ": " + str(sw.players[name].games) + "  "
        logger.info(res)
            
        fr = sw.getFinalRanking()

        logger.info("Final ranking")
        logger.info(fr)

        fmt = "{:2} {:.<18} {:4} : {:5} {:>12} {:>10} {:>9}"
        ## print(fmt.format(" #", "name", "wins", "hoops", "lawns", "primaryXS", "starts"))
        for i in range(1,len(sw.players)+1):
            for name, val in fr.items():
                if val == i:
                    p = sw.players[name]
                    wins = p.games
                    hoops = p.hoops
                    prim = p.primarys-p.secondarys
                    lawns = []
                    for j in range(sw.numLawns):
                        if j in p.lawns: lawns.append(p.lawns[j])
                        else: lawns.append(0)
                    starts = p.startCount
                    ## print(fmt.format(i, name, wins, hoops, str(lawns), prim, starts))

    def testStart7(self):
        sw =  Logic.Tournament();
        sw.setOpts(13, 1000000000, 100, 4, True)
        sw.addPlayer("A", Logic.Colours.PRIMARY)
        sw.addPlayer("B", Logic.Colours.SECONDARY)
        sw.addPlayer("C")
        sw.addPlayer("D")
        sw.addPlayer("E")
        sw.addPlayer("F")
        sw.addPlayer("G")
                     
        sw.start();

        for j in range(sw.getMaxRounds()-1):

            if j != 0:
                try:
                    sw.writeLog(round, j == 1)
                except Exception as e:
                    print(e)
                    print("Failed to write log for round", round)    
                sw.computeRanking()
                logger.info("Ranking after round " + str(j) + " ")
                res = ""
                for name in sw.ranking:
                    res += name + ": " + str(sw.players[name].games) + "  "
                logger.info(res)

                # Add, remove or restore players
                if j == 1:
                    sw.removePlayer("A")
                elif j == 2:
                    sw.removePlayer("B")
                elif j == 3:
                    sw.restorePlayer("A")
                elif j == 4:
                    sw.addLatePlayer("Z")
                sw.prepareRound()
            
            round = sw.rounds[j]
            if len(round) == 0:
                logger.info("Stopping early as no more game combination after round " + str(j))
                j -= 1
                break
            else:
                sw.setByeScores();
                sw.makeGamesChoices(round);
                ngames = len(round) // 2;
     
                for i in range(ngames):
                    p1 = round[2 * i]
                    p2 = round[2 * i + 1]
                    if p1[0] != "Bye" and p2[0] != "Bye":
                        badScore = random.randrange(26);
                        goodScore = badScore + 1 + random.randrange(26 - badScore);
                        if p1[0] < p2[0]:
                            p1[1] = goodScore
                            p2[1] = badScore
                        else:
                            p1[1] = badScore
                            p2[1] = goodScore
                        
                logger.info("Score in round %s : %s", j + 1, round)

        sw.computeRanking()
        logger.info("Ranking after round " + str(j + 1) + " ")
        res = ""
        for name in sw.ranking:
            res += name + ": " + str((sw.players|sw.resting)[name].games) + "  "
        logger.info(res)
            
        fr = sw.getFinalRanking()

        logger.info("Final ranking")
        logger.info(fr)

        fmt = "{:2} {:.<18} {:4} : {:5} {:>12} {:>10} {:>9}"
        print(fmt.format(" #", "name", "wins", "hoops", "lawns", "primaryXS", "starts"))
        for i in range(1,len(sw.players|sw.resting)+1):
            for name, val in fr.items():
                if val == i:
                    p = (sw.players|sw.resting)[name]
                    wins = p.games
                    hoops = p.hoops
                    prim = p.primarys-p.secondarys
                    lawns = []
                    for j in range(sw.numLawns):
                        if j in p.lawns: lawns.append(p.lawns[j])
                        else: lawns.append(0)
                    starts = p.startCount
                    print(fmt.format(i, name, wins, hoops, str(lawns), prim, starts))


    def testStart15(self):
        sw =  Logic.Tournament();
        sw.setOpts(14, 1000000000, 100, 4, True)
        sw.addPlayer("A", Logic.Colours.PRIMARY)
        sw.addPlayer("B", Logic.Colours.SECONDARY)
        sw.addPlayer("C")
        sw.addPlayer("D")
        sw.addPlayer("E")
        sw.addPlayer("F")
        sw.addPlayer("G")
        sw.addPlayer("H")
        sw.addPlayer("I")
        sw.addPlayer("J")
        sw.addPlayer("K")
        sw.addPlayer("L")
        sw.addPlayer("M")
        sw.addPlayer("N")
        sw.addPlayer("O")
                     
        sw.start();
 
        for j in range(sw.getMaxRounds()):
            if j != 0:
                sw.computeRanking()
                logger.info("Ranking after round " + str(j) + " ")
                res = ""
                for name in sw.ranking:
                    res += name + ": " + str(sw.players[name].games) + "  "
                logger.info(res)
                sw.prepareRound()
            
            round = sw.rounds[j]
            if len(round) == 0:
                logger.info("Stopping early as no more game combination after round " + str(j))
                j -= 1
                break
            else:
                sw.setByeScores();
                sw.makeGamesChoices(round);
                ngames = len(round) // 2;
     
                for i in range(ngames):
                    p1 = round[2 * i]
                    p2 = round[2 * i + 1]
                    if p1[0] != "Bye" and p2[0] != "Bye":
                        badScore = random.randrange(26);
                        goodScore = badScore + 1 + random.randrange(26 - badScore);
                        if p1[0] < p2[0]:
                            p1[1] = goodScore
                            p2[1] = badScore
                        else:
                            p1[1] = badScore
                            p2[1] = goodScore
                        
                logger.info("Score in round %s : %s", j + 1, round)
            
        sw.computeRanking()
        logger.info("Ranking after round " + str(j + 1) + " ")
        res = ""
        for name in sw.ranking:
            res += name + ": " + str(sw.players[name].games) + "  "
        logger.info(res)
            
        fr = sw.getFinalRanking()

        logger.info("Final ranking")
        logger.info(fr)

        fmt = "{:2} {:.<18} {:4} : {:5} {:>12} {:>10} {:>9}"
        print(fmt.format(" #", "name", "wins", "hoops", "lawns", "primaryXS", "starts"))
        for i in range(1,len(sw.players)+1):
            for name, val in fr.items():
                if val == i:
                    p = sw.players[name]
                    wins = p.games
                    hoops = p.hoops
                    prim = p.primarys-p.secondarys
                    lawns = []
                    for j in range(sw.numLawns):
                        if j in p.lawns: lawns.append(p.lawns[j])
                        else: lawns.append(0)
                    starts = p.startCount
                    print(fmt.format(i, name, wins, hoops, str(lawns), prim, starts))


    def writeLog(self):
        sw =  Logic.Tournament()
        sw.setOpts(26, 1000000000, 100, 4, False)
        sw.addPlayer("Andrew Aardvark", Logic.Colours.PRIMARY)
        sw.addPlayer("Bill Banana", Logic.Colours.SECONDARY)
        sw.addPlayer("Cool Cucumber", None)
        sw.addPlayer("Dangerous Dan")
        
        round = []
        round.append(["Andrew Aardvark", 6])
        round.append(["Bill Banana", 23])
        round.append(["Cool Cucumber", 22])
        round.append(["Dangerous Dan",2])
        sw.writeLog(round, True)
        
        round = []
        round.append(["Bill Banana", 23])
        round.append(["Cool Cucumber", 22])
        round.append(["Andrew Aardvark", 6])
        round.append(["Dangerous Dan",2])
        sw.writeLog(round, False)

    def testWriteLog(self):
        self.writeLog()

        logname = "journal.txt"
        with open (logname) as f:
            lines = f.readlines()
            i = 0
            for line in lines:
                if i == 0: self.assertEqual("{'byeScore': 26, 'maxCombis': 1000000000, 'enoughGood': 100, 'numLawns': 4, 'randomStart': False}\n", line)
                elif i == 1: self.assertEqual("Andrew Aardvark -P,Bill Banana -S,Cool Cucumber,Dangerous Dan\n", line)
                elif i == 2: self.assertEqual("Bill Banana,beat,Andrew Aardvark,23,6\n", line)
                elif i == 3: self.assertEqual("Cool Cucumber,beat,Dangerous Dan,22,2\n", line)
                elif i == 4: self.assertEqual("Bill Banana,beat,Cool Cucumber,23,22\n", line)
                elif i == 5: self.assertEqual("Andrew Aardvark,beat,Dangerous Dan,6,2\n", line)
                i += 1
            self.assertEqual(6, i)
        os.remove(logname)

    def testRecoverFromLog(self):
        self.writeLog()
        sw =  Logic.Tournament()
        logname = "journal.txt"
        sw.recoverFromLog(Path(logname))
        fr = sw.getFinalRanking()
        self.assertEqual({'Bill Banana': 1, 'Andrew Aardvark': 3, 'Cool Cucumber': 2, 'Dangerous Dan': 4}, fr)
        logger.info("Final ranking")
        logger.info(fr)

if __name__ == '__main__':
    unittest.main()
