import unittest

from math import comb
from swiss import Logic
from datetime import datetime
import random
import logging

logging.basicConfig(filename='test.log', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)

class TestBasicSwiss(unittest.TestCase):

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

    def testCombinations(self):
        res = self.combis(gamesPerRound = 6, numClash = 3, enoughGood = 4)
        self.assertEqual(4,res.numGood)
        self.assertEqual(55,res.bestSumSquares)
        res = self.combis(gamesPerRound = 6, numClash = 3)
        self.assertEqual(4,res.numGood)
        self.assertEqual(55,res.bestSumSquares)
        self.combis(gamesPerRound = 8, numClash = 50, enoughGood = 4)
        self.combis(gamesPerRound = 16, numClash = 500, enoughGood = 1)
        self.combis(gamesPerRound = 16, numClash = 500, enoughGood = 4)
        self.combis(gamesPerRound = 16, numClash = 500, enoughGood = 100)
        self.combis(gamesPerRound = 8, numClash = 500, enoughGood = 1)
        self.combis(gamesPerRound = 8, numClash = 500, enoughGood = 4)
        self.combis(gamesPerRound = 8, numClash = 500, enoughGood = 100)
        res = self.combis(gamesPerRound = 8, numClash = 500)
        self.assertEqual(501,res.numGood)
        self.assertEqual(140,res.bestSumSquares)

    def testCreate1(self):
        sw =  Logic.Tournament(26, 1000000000, 100, 4);
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
        sw =  Logic.Tournament(26, 1000000000, 100, 4);
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
        sw =  Logic.Tournament(26, 1000000000, 100, 4);
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
        sw =  Logic.Tournament(26, 1000000000, 100, 4);
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
        self.assertDictEqual({'A': 1, 'B': 2, 'C': 3, 'E': 4, 'D': 5, 'F': 6, 'G': 7, 'H': 8}, fr)    
        
    def testStart(self):
        sw =  Logic.Tournament(26, 1000000000, 100, 4);
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

        logger.info( (fr))

##        System.out.format("%2s %-18.18s %4.4s : %5.5s %-12.12s %9.9s %6.6s%n", " #", "name", "wins", "hoops", "lawns",
##                "primaryXS", "starts");
##
##        for (int i = 1; i <= sw.getPlayers().size(); i++) {
##            for (Entry<String, Integer> entry : fr.entrySet()) {
##                if (entry.getValue() == i) {
##                    String name = entry.getKey();
##                    int pos = entry.getValue();
##                    Player p = sw.getPlayers().get(name);
##                    int wins = p.getGames();
##                    int hoops = p.getHoops();
##                    int prim = p.getPrimaryExcess();
##                    List<Integer> lawns = new ArrayList<>();
##                    for (int j = 0; j < sw.getNumLawns(); j++) {
##                        lawns.add(p.getLawnCount(j));
##                    }
##                    int starts = p.getStartCount();
##
##                    System.out.format("%2d %-18.18s %4d : %5d %-12.12s %9d %6d%n", pos, name, wins, hoops,
##                            lawns.toString(), prim, starts);


 

##	@Test
##	void testWriteLog() throws Exception {
##		BasicSwiss sw = new BasicSwiss(26, 1000000000, 100, 4);
##		sw.addPlayer("Andrew Aardvark", Colours.PRIMARY);
##		sw.addPlayer("Bill Banana", Colours.SECONDARY);
##		sw.addPlayer("Cool Cucumber", null);
##		sw.addPlayer("Dangerous Dan");
##		String logname = "journal.txt";
##		List<PersonScore> round = new ArrayList<PersonScore>();
##		PersonScore p = new PersonScore("Andrew Aardvark");
##		p.setScore(6);
##		round.add(p);
##		p = new PersonScore("Bill Banana");
##		p.setScore(23);
##		round.add(p);
##		p = new PersonScore("Cool Cucumber");
##		p.setScore(22);
##		round.add(p);
##		p = new PersonScore("Dangerous Dan");
##		p.setScore(2);
##		round.add(p);
##		sw.writeLog(round, true);
##		sw.writeLog(round, false);
##		try (BufferedReader f = new BufferedReader(new FileReader(logname))) {
##			String line;
##			int i = 0;
##			while ((line = f.readLine()) != null) {
##				if (i == 0) {
##					assertEquals("Andrew Aardvark -P,Bill Banana -S,Cool Cucumber,Dangerous Dan", line);
##				} else {
##					if (i % 2 == 1) {
##						assertEquals("Bill Banana,beat,Andrew Aardvark,23,6", line);
##					} else {
##						assertEquals("Cool Cucumber,beat,Dangerous Dan,22,2", line);
##					}
##				}
##				i++;
##			}
##			assertEquals(5, i);
##		}
##		Files.deleteIfExists(Paths.get(logname));
##	}

if __name__ == '__main__':
    unittest.main()
