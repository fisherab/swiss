package uk.org.stevefisher.swiss.logic;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.BufferedReader;
import java.io.FileReader;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Random;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.junit.jupiter.api.RepeatedTest;
import org.junit.jupiter.api.Test;

import uk.org.stevefisher.swiss.logic.BasicSwiss.Colours;
import uk.org.stevefisher.swiss.logic.BasicSwiss.CombResult;

public class TestBasicSwiss {

	private static final Logger logger = LogManager.getLogger(TestBasicSwiss.class);

	@Test
	public void testFormat() {
		System.out.format("%2s %-18.18s %4.4s : %5.5s %-12.12s %9.9s %6.6s%n", " #", "name", "wins", "hoops", "lawns",
				"primaryXS", "starts");
		String name = "ABCDEFGHIJKLMONPQRSTUVWXYZ";
		int pos = 1;
		int wins = 20;
		int hoops = 999;
		int prim = 5;
		List<Integer> lawns = new ArrayList<>();
		lawns.add(6);
		lawns.add(7);
		int starts = 20;
		System.out.format("%2d %-18.18s %4d : %5d %-12.12s %9d %6d%n", pos, name, wins, hoops, lawns.toString(), prim,
				starts);
	}

	@RepeatedTest(1000)
	public void testCreate() throws Exception {
		logger.info("Test testCreate");
		BasicSwiss sw = new BasicSwiss(26, 1000000000, 100, 4);

		sw.addPlayer("A", Colours.PRIMARY);
		sw.addPlayer("B", Colours.SECONDARY);
		sw.addPlayer("C");
		sw.addPlayer("D");
		sw.addPlayer("E");
		sw.addPlayer("F");
		sw.addPlayer("G");
		sw.addPlayer("H");
		/*
		 * sw.addPlayer("I"); sw.addPlayer("J"); sw.addPlayer("K"); sw.addPlayer("L");
		 * sw.addPlayer("M"); sw.addPlayer("N"); sw.addPlayer("O"); sw.addPlayer("P");
		 * sw.addPlayer("Q");
		 */
		sw.start();

		logger.info("KO Rounds " + sw.getKORounds());
		logger.info("Max rounds " + sw.getMaxRounds());
		logger.info("Rec rounds " + sw.getRecRounds());

		for (int j = 0; j < sw.getRecRounds(); j++) {
			if (j != 0) {
				sw.computeRanking();
				System.out.print("Ranking after round " + j + " ");
				for (String name : sw.getRanking()) {
					System.out.print(name + ": " + sw.getPlayers().get(name).getGames() + "  ");
				}
				System.out.println();
				sw.prepareRound();
			}
			List<PersonScore> round = sw.getRound(j);
			sw.setByeScores();
			sw.makeGamesChoices(round);
			int ngames = round.size() / 2;
			Random rand = new Random();
			for (int i = 0; i < ngames; i++) {
				PersonScore p1 = round.get(2 * i);
				PersonScore p2 = round.get(2 * i + 1);
				if (!p1.getName().equals("Bye") && !p2.getName().equals("Bye")) {
					int badScore = rand.nextInt(26);
					int goodScore = badScore + 1 + rand.nextInt(26 - badScore);
					if (p1.getName().compareTo(p2.getName()) < 0) {
						p1.setScore(goodScore);
						p2.setScore(badScore);
					} else {
						p1.setScore(badScore);
						p2.setScore(goodScore);
					}
				}
			}
			logger.info("Score in round " + (j + 1) + ": " + sw.getRound(j));

		}

		sw.computeRanking();
		Map<String, Integer> fr = sw.getFinalRanking();

		System.out.format("%2s %-18.18s %4.4s : %5.5s %-12.12s %9.9s %6.6s%n", " #", "name", "wins", "hoops", "lawns",
				"primaryXS", "starts");

		for (int i = 1; i <= sw.getPlayers().size(); i++) {
			for (Entry<String, Integer> entry : fr.entrySet()) {
				if (entry.getValue() == i) {
					String name = entry.getKey();
					int pos = entry.getValue();
					Player p = sw.getPlayers().get(name);
					int wins = p.getGames();
					int hoops = p.getHoops();
					int prim = p.getPrimaryExcess();
					List<Integer> lawns = new ArrayList<>();
					for (int j = 0; j < sw.getNumLawns(); j++) {
						lawns.add(p.getLawnCount(j));
					}
					int starts = p.getStartCount();

					System.out.format("%2d %-18.18s %4d : %5d %-12.12s %9d %6d%n", pos, name, wins, hoops,
							lawns.toString(), prim, starts);
				}
			}
		}
	}

	@Test
	void testWriteLog() throws Exception {
		BasicSwiss sw = new BasicSwiss(26, 1000000000, 100, 4);
		sw.addPlayer("Andrew Aardvark", Colours.PRIMARY);
		sw.addPlayer("Bill Banana", Colours.SECONDARY);
		sw.addPlayer("Cool Cucumber", null);
		sw.addPlayer("Dangerous Dan");
		String logname = "journal.txt";
		List<PersonScore> round = new ArrayList<PersonScore>();
		PersonScore p = new PersonScore("Andrew Aardvark");
		p.setScore(6);
		round.add(p);
		p = new PersonScore("Bill Banana");
		p.setScore(23);
		round.add(p);
		p = new PersonScore("Cool Cucumber");
		p.setScore(22);
		round.add(p);
		p = new PersonScore("Dangerous Dan");
		p.setScore(2);
		round.add(p);
		sw.writeLog(round, true);
		sw.writeLog(round, false);
		try (BufferedReader f = new BufferedReader(new FileReader(logname))) {
			String line;
			int i = 0;
			while ((line = f.readLine()) != null) {
				if (i == 0) {
					assertEquals("Andrew Aardvark -P,Bill Banana -S,Cool Cucumber,Dangerous Dan", line);
				} else {
					if (i % 2 == 1) {
						assertEquals("Bill Banana,beat,Andrew Aardvark,23,6", line);
					} else {
						assertEquals("Cool Cucumber,beat,Dangerous Dan,22,2", line);
					}
				}
				i++;
			}
			assertEquals(5, i);
		}
		Files.deleteIfExists(Paths.get(logname));
	}

	@Test
	void combinationsTwoA() {
		logger.info("Test combinationsTwoA");
		List<Game> games = new ArrayList<Game>();
		games.add(new Game("A", "B", 4));
		games.add(new Game("A", "C", 9));
		games.add(new Game("B", "E", 16));
		games.add(new Game("C", "D", 25));

		int gamesPerRound = 2;
		int maxCombis = 1000000000;
		Integer goodEnough = 10;
		processGames(games, gamesPerRound, maxCombis, goodEnough,
				"More:true numGood:3 bestGames:[A vs C (9), B vs E (16)] bestSumSquares:25");
	}

	private void processGames(List<Game> games, int gamesPerRound, int maxCombis, Integer enoughGood, String expected) {
		logger.debug("gamesPerRound:{}, Maxcombis:{}, enoughGood:{}", gamesPerRound, maxCombis, enoughGood);
		Collections.sort(games, new Comparator<Game>() {
			@Override
			public int compare(Game g1, Game g2) {
				return g1.getSquare() - g2.getSquare();
			}
		});

		BigInteger combis = BasicSwiss.cNR(games.size(), gamesPerRound);
		logger.debug("There are " + games.size() + " with " + combis + " combinations. "
				+ (combis.compareTo(BigInteger.valueOf(maxCombis)) > 0 ? "Truncate. " : ""));
		long start = System.currentTimeMillis();
		CombResult combResult = BasicSwiss.combinationsTwo(games, gamesPerRound, new HashSet<Game>(), 0,
				new HashSet<String>(), combis.compareTo(BigInteger.valueOf(maxCombis)) > 0 ? enoughGood : null);
		long end = System.currentTimeMillis();
		logger.info("combResult {} in {} seconds", combResult, (end - start) / 1000.);
		start = end;
		assertEquals(expected, combResult.toString());
		combResult = BasicSwiss.combinationsThree(games, gamesPerRound,
				combis.compareTo(BigInteger.valueOf(maxCombis)) > 0 ? enoughGood : null);
		end = System.currentTimeMillis();
		logger.info("combResult {} in {} seconds", combResult, (end - start) / 1000.);
	}

	@Test
	void testCNR() {
		logger.info("Test testCNR");
		assertEquals(BigInteger.valueOf(43758), BasicSwiss.cNR(18, 8));
		assertEquals(BigInteger.valueOf(658008), BasicSwiss.cNR(40, 5));
	}

	@Test
	void combinationsTwoB() {
		logger.info("Test combinationsTwoB");
		List<Game> games = new ArrayList<Game>();
		games.add(new Game("A", "B", 9));
		games.add(new Game("A", "C", 9));
		games.add(new Game("A", "G", 25));
		games.add(new Game("B", "E", 16));
		games.add(new Game("B", "H", 1));
		games.add(new Game("C", "D", 16));
		games.add(new Game("I", "J", 1));
		games.add(new Game("K", "E", 25));

		int gamesPerRound = 3;
		int maxCombis = 40;
		Integer goodEnough = 20;
		processGames(games, gamesPerRound, maxCombis, goodEnough,
				"More:false numGood:20 bestGames:[A vs C (9), B vs H (1), I vs J (1)] bestSumSquares:11");
	}

	private List<Game> getGames(String gamesString) {
		List<Game> games = new ArrayList<Game>();
		for (String gameString : gamesString.split(",")) {
			String[] ws = gameString.trim().split(" ");
			String g1 = ws[0];
			String g2 = ws[2];
			String g3 = ws[3];
			g3 = g3.substring(1, g3.length() - 1);
			int ig3 = Integer.parseInt(g3);
			games.add(new Game(g1, g2, ig3));
		}
		return games;
	}

	@Test
	void combinationsTwoC() {
		logger.info("Test combinationsTwoC");
		String gamesString = "B vs E (1), C vs D (1), C vs G (1), F vs K (1), G vs I (1), H vs I (1), H vs M (1), J vs K (1), J vs N (1), L vs N (1), Bye vs P (1), P vs Q (1),"
				+ "A vs E (4), C vs E (4), D vs G (4), F vs H (4), F vs J (4), I vs M (4), J vs L (4), K vs M (4), K vs N (4), L vs Q (4), N vs O (4), O vs P (4),"
				+ "A vs D (9), B vs C (9), C vs H (9), E vs G (9), F vs I (9), F vs N (9), G vs M (9), H vs K (9), J vs M (9), L vs P (9), N vs Q (9), Bye vs O (9),"
				+ "B vs G (16), D vs H (16), E vs I (16), F vs L (16), H vs J (16), J vs Q (16), Bye vs L (16),"
				+ "A vs G (25), B vs I (25), C vs F (25), D vs M (25), E vs H (25), F vs O (25), G vs K (25), H vs N (25), I vs J (25), J vs P (25), K vs Q (25), L vs M (25),"
				+ "A vs I (36), B vs H (36), C vs K (36), D vs F (36), E vs M (36), F vs Q (36), I vs N (36), K vs P (36), M vs O (36),"
				+ "B vs M (49), D vs K (49), F vs P (49), G vs N (49), H vs O (49), M vs Q (49), Bye vs K (49),"
				+ "A vs M (64), C vs N (64), D vs J (64), E vs K (64), G vs L (64), H vs Q (64), I vs O (64), Bye vs F (64),"
				+ "A vs F (81), B vs K (81), C vs L (81), D vs N (81), E vs J (81), G vs O (81), H vs P (81), I vs Q (81), Bye vs M (81),"
				+ "B vs J (100), C vs O (100), D vs L (100), I vs P (100),"
				+ "A vs J (121), B vs N (121), C vs Q (121), D vs O (121), E vs L (121), G vs P (121), Bye vs I (121),"
				+ "A vs N (144), B vs L (144), C vs P (144), E vs O (144), Bye vs G (144),"
				+ "A vs L (169), B vs O (169), D vs P (169), E vs Q (169), Bye vs C (169),"
				+ "A vs O (196), B vs Q (196), Bye vs D (196)," + "A vs Q (225), Bye vs E (225),"
				+ "A vs P (256), B vs Bye (256), A vs Bye (289)";
		List<Game> games = getGames(gamesString);

		int gamesPerRound = 9;
		int maxCombis = 1000000000;
		Integer goodEnough = 100;
		processGames(games, gamesPerRound, maxCombis, goodEnough,
				"More:false numGood:110 bestGames:[A vs M (64), N vs O (4), Bye vs P (1), F vs K (1), B vs E (1), H vs J (16), C vs D (1), G vs I (1), L vs Q (4)] bestSumSquares:93");
	}

	@Test
	void combinationsTwoD() {
		logger.info("Test combinationsTwoD");
		List<Game> games = getGames(
				"H vs J (1), J vs K (1), F vs I (4), G vs L (25), H vs N (25), I vs M (25), E vs K (36), E vs L (49), G vs N (49), D vs M (81), F vs P (100), C vs O (144), D vs P (144), B vs O (169), C vs Q (196), A vs Q (256), B vs Bye (256), A vs Bye (289)");

		int gamesPerRound = 9;
		int maxCombis = 1000000000;
		Integer goodEnough = 100;
		processGames(games, gamesPerRound, maxCombis, goodEnough,
				"More:true numGood:0 bestGames:null bestSumSquares:9223372036854775807");

	}

}
