import unittest

from math import comb
from swiss import Logic
from datetime import datetime
import random
import logging

logging.basicConfig(filename='example.log', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)

class TestBasicSwiss(unittest.TestCase):

    def game3(self,games, gamesPerRound):
        logger.info("Number of combinations %s", comb(len(games), gamesPerRound))
        start = datetime.now()
 #       res2 = Logic.Tournament.combinationsThree(games,gamesPerRound,100)
        t = datetime.now()
 #       logger.info("Two %s took %s", res2, t-start)
       
        start = t
        res3 = Logic.Tournament.combinationsTwo(games,gamesPerRound, set(), 0, set(), 100)
        t = datetime.now()
        logger.info("Three %s took %s", res3, t-start)
        
    def testCombinations2and3(self):
        games = []
        games.append(Logic.Game("A","B",1))
        games.append(Logic.Game("A","C",2))
        games.append(Logic.Game("A","D",4))
        games.append(Logic.Game("C","D",8))
        self.game3(games,2)
        games.append(Logic.Game("C","E",16))
        games.append(Logic.Game("E","F",32))
        self.game3(games,20)
        for i in range(40):
             games.append(Logic.Game("A","B" + str(i),10*i*1))
        games.append(Logic.Game("1Z1","1Z2",8))
        games.append(Logic.Game("2Z1","2Z2",8))
        games.append(Logic.Game("3Z1","3Z2",8))
        games.append(Logic.Game("4Z1","4Z2",8))
 #       games.append(Logic.Game("5Z1","5Z2",8))
 #       games.append(Logic.Game("6Z1","6Z2",8))
 #       games.append(Logic.Game("7Z1","7Z2",8))
 #       games.append(Logic.Game("8Z1","8Z2",8))
        self.game3(games,8)
             
    def testCreate(self):
 
        sw =  Logic.Tournament(26, 1000000000, 100, 4);

        sw.addPlayer("A", Logic.Colours.PRIMARY)
        sw.addPlayer("B", Logic.Colours.SECONDARY)
        sw.addPlayer("C")
        sw.addPlayer("D")
        sw.addPlayer("E")
        sw.addPlayer("F")
        sw.addPlayer("G")
        sw.addPlayer("H")
        
##        sw.addPlayer("I"); sw.addPlayer("J"); sw.addPlayer("K"); sw.addPlayer("L");
##        sw.addPlayer("M"); sw.addPlayer("N"); sw.addPlayer("O"); sw.addPlayer("P");
##        sw.addPlayer("Q");
        
        sw.start();

        logger.info("KO Rounds " + str(sw.getKORounds()))
        logger.info("Max rounds " + str(sw.getMaxRounds()))
        logger.info("Rec rounds " + str(sw.getRecRounds()))

        for j in range(sw.getRecRounds()+2):
            if j != 0:
                sw.computeRanking()
                logger.info("Ranking after round " + str(j) + " ")
                res = ""
                for name in sw.ranking:
                    res += name + ": " + str(sw.players[name].games) + "  "
                logger.info(res)
                sw.prepareRound()
            
            round = sw.rounds[j]
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

        

##		sw.computeRanking();
##		Map<String, Integer> fr = sw.getFinalRanking();
##
##		System.out.format("%2s %-18.18s %4.4s : %5.5s %-12.12s %9.9s %6.6s%n", " #", "name", "wins", "hoops", "lawns",
##				"primaryXS", "starts");
##
##		for (int i = 1; i <= sw.getPlayers().size(); i++) {
##			for (Entry<String, Integer> entry : fr.entrySet()) {
##				if (entry.getValue() == i) {
##					String name = entry.getKey();
##					int pos = entry.getValue();
##					Player p = sw.getPlayers().get(name);
##					int wins = p.getGames();
##					int hoops = p.getHoops();
##					int prim = p.getPrimaryExcess();
##					List<Integer> lawns = new ArrayList<>();
##					for (int j = 0; j < sw.getNumLawns(); j++) {
##						lawns.add(p.getLawnCount(j));
##					}
##					int starts = p.getStartCount();
##
##					System.out.format("%2d %-18.18s %4d : %5d %-12.12s %9d %6d%n", pos, name, wins, hoops,
##							lawns.toString(), prim, starts);
##				}
##			}
##		}
##	}
##
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
##
##	@Test
##	void combinationsTwoA() {
##		logging.info("Test combinationsTwoA");
##		List<Game> games = new ArrayList<Game>();
##		games.add(new Game("A", "B", 4));
##		games.add(new Game("A", "C", 9));
##		games.add(new Game("B", "E", 16));
##		games.add(new Game("C", "D", 25));
##
##		int gamesPerRound = 2;
##		int maxCombis = 1000000000;
##		Integer goodEnough = 10;
##		processGames(games, gamesPerRound, maxCombis, goodEnough,
##				"More:true numGood:3 bestGames:[A vs C (9), B vs E (16)] bestSumSquares:25");
##	}
##
##	private void processGames(List<Game> games, int gamesPerRound, int maxCombis, Integer enoughGood, String expected) {
##		logging.debug("gamesPerRound:{}, Maxcombis:{}, enoughGood:{}", gamesPerRound, maxCombis, enoughGood);
##		Collections.sort(games, new Comparator<Game>() {
##			@Override
##			public int compare(Game g1, Game g2) {
##				return g1.getSquare() - g2.getSquare();
##			}
##		});
##
##		BigInteger combis = BasicSwiss.cNR(games.size(), gamesPerRound);
##		logging.debug("There are " + games.size() + " with " + combis + " combinations. "
##				+ (combis.compareTo(BigInteger.valueOf(maxCombis)) > 0 ? "Truncate. " : ""));
##		long start = System.currentTimeMillis();
##		CombResult combResult = BasicSwiss.combinationsTwo(games, gamesPerRound, new HashSet<Game>(), 0,
##				new HashSet<String>(), combis.compareTo(BigInteger.valueOf(maxCombis)) > 0 ? enoughGood : null);
##		long end = System.currentTimeMillis();
##		logging.info("combResult {} in {} seconds", combResult, (end - start) / 1000.);
##		start = end;
##		assertEquals(expected, combResult.toString());
##		combResult = BasicSwiss.combinationsThree(games, gamesPerRound,
##				combis.compareTo(BigInteger.valueOf(maxCombis)) > 0 ? enoughGood : null);
##		end = System.currentTimeMillis();
##		logging.info("combResult {} in {} seconds", combResult, (end - start) / 1000.);
##	}
##

##
##	@Test
##	void combinationsTwoB() {
##		logging.info("Test combinationsTwoB");
##		List<Game> games = new ArrayList<Game>();
##		games.add(new Game("A", "B", 9));
##		games.add(new Game("A", "C", 9));
##		games.add(new Game("A", "G", 25));
##		games.add(new Game("B", "E", 16));
##		games.add(new Game("B", "H", 1));
##		games.add(new Game("C", "D", 16));
##		games.add(new Game("I", "J", 1));
##		games.add(new Game("K", "E", 25));
##
##		int gamesPerRound = 3;
##		int maxCombis = 40;
##		Integer goodEnough = 20;
##		processGames(games, gamesPerRound, maxCombis, goodEnough,
##				"More:false numGood:20 bestGames:[A vs C (9), B vs H (1), I vs J (1)] bestSumSquares:11");
##	}
##
##	private List<Game> getGames(String gamesString) {
##		List<Game> games = new ArrayList<Game>();
##		for (String gameString : gamesString.split(",")) {
##			String[] ws = gameString.trim().split(" ");
##			String g1 = ws[0];
##			String g2 = ws[2];
##			String g3 = ws[3];
##			g3 = g3.substring(1, g3.length() - 1);
##			int ig3 = Integer.parseInt(g3);
##			games.add(new Game(g1, g2, ig3));
##		}
##		return games;
##	}
##
##	@Test
##	void combinationsTwoC() {
##		logging.info("Test combinationsTwoC");
##		String gamesString = "B vs E (1), C vs D (1), C vs G (1), F vs K (1), G vs I (1), H vs I (1), H vs M (1), J vs K (1), J vs N (1), L vs N (1), Bye vs P (1), P vs Q (1),"
##				+ "A vs E (4), C vs E (4), D vs G (4), F vs H (4), F vs J (4), I vs M (4), J vs L (4), K vs M (4), K vs N (4), L vs Q (4), N vs O (4), O vs P (4),"
##				+ "A vs D (9), B vs C (9), C vs H (9), E vs G (9), F vs I (9), F vs N (9), G vs M (9), H vs K (9), J vs M (9), L vs P (9), N vs Q (9), Bye vs O (9),"
##				+ "B vs G (16), D vs H (16), E vs I (16), F vs L (16), H vs J (16), J vs Q (16), Bye vs L (16),"
##				+ "A vs G (25), B vs I (25), C vs F (25), D vs M (25), E vs H (25), F vs O (25), G vs K (25), H vs N (25), I vs J (25), J vs P (25), K vs Q (25), L vs M (25),"
##				+ "A vs I (36), B vs H (36), C vs K (36), D vs F (36), E vs M (36), F vs Q (36), I vs N (36), K vs P (36), M vs O (36),"
##				+ "B vs M (49), D vs K (49), F vs P (49), G vs N (49), H vs O (49), M vs Q (49), Bye vs K (49),"
##				+ "A vs M (64), C vs N (64), D vs J (64), E vs K (64), G vs L (64), H vs Q (64), I vs O (64), Bye vs F (64),"
##				+ "A vs F (81), B vs K (81), C vs L (81), D vs N (81), E vs J (81), G vs O (81), H vs P (81), I vs Q (81), Bye vs M (81),"
##				+ "B vs J (100), C vs O (100), D vs L (100), I vs P (100),"
##				+ "A vs J (121), B vs N (121), C vs Q (121), D vs O (121), E vs L (121), G vs P (121), Bye vs I (121),"
##				+ "A vs N (144), B vs L (144), C vs P (144), E vs O (144), Bye vs G (144),"
##				+ "A vs L (169), B vs O (169), D vs P (169), E vs Q (169), Bye vs C (169),"
##				+ "A vs O (196), B vs Q (196), Bye vs D (196)," + "A vs Q (225), Bye vs E (225),"
##				+ "A vs P (256), B vs Bye (256), A vs Bye (289)";
##		List<Game> games = getGames(gamesString);
##
##		int gamesPerRound = 9;
##		int maxCombis = 1000000000;
##		Integer goodEnough = 100;
##		processGames(games, gamesPerRound, maxCombis, goodEnough,
##				"More:false numGood:110 bestGames:[A vs M (64), N vs O (4), Bye vs P (1), F vs K (1), B vs E (1), H vs J (16), C vs D (1), G vs I (1), L vs Q (4)] bestSumSquares:93");
##	}
##
##	@Test
##	void combinationsTwoD() {
##		logging.info("Test combinationsTwoD");
##		List<Game> games = getGames(
##				"H vs J (1), J vs K (1), F vs I (4), G vs L (25), H vs N (25), I vs M (25), E vs K (36), E vs L (49), G vs N (49), D vs M (81), F vs P (100), C vs O (144), D vs P (144), B vs O (169), C vs Q (196), A vs Q (256), B vs Bye (256), A vs Bye (289)");
##
##		int gamesPerRound = 9;
##		int maxCombis = 1000000000;
##		Integer goodEnough = 100;
##		processGames(games, gamesPerRound, maxCombis, goodEnough,
##				"More:true numGood:0 bestGames:null bestSumSquares:9223372036854775807");
##
##	}
##
##}

if __name__ == '__main__':
    unittest.main()
