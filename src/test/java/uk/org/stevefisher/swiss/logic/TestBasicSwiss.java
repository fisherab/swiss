package uk.org.stevefisher.swiss.logic;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Random;

import org.junit.jupiter.api.Test;

import uk.org.stevefisher.swiss.logic.BasicSwiss.Colours;

public class TestBasicSwiss {

	@Test
	public void testCreate() throws Exception {
		BasicSwiss sw = new BasicSwiss(7, 1000000000, 100, 3);
		sw.addPlayer("A", Colours.PRIMARY);
		sw.addPlayer("B", Colours.SECONDARY);
		sw.addPlayer("C");
		sw.addPlayer("D");
		sw.addPlayer("E");
		sw.addPlayer("F");
		sw.addPlayer("G");
		sw.addPlayer("H");
		sw.addPlayer("I");
		sw.addPlayer("J");
		sw.addPlayer("K");
		sw.addPlayer("L");
		// sw.addPlayer("M");
		// sw.addPlayer("N");
		// sw.addPlayer("O");
		// sw.addPlayer("P");
		// sw.addPlayer("Q");
		sw.start();

		System.out.println("KO Rounds " + sw.getKORounds());
		System.out.println("Max rounds " + sw.getMaxRounds());

		for (int j = 0; j < sw.getKORounds() + 5; j++) {
			if (j != 0) {
				sw.computeRanking();
				sw.prepareRound();
				System.out.print("Ranking after round " + j + " ");
				for (String name : sw.getRanking()) {
					System.out.print(name + ": " + sw.getPlayers().get(name).getGames() + "  ");
				}
				System.out.println();
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
					if (rand.nextDouble() > 0.5) {
						p1.setScore(7);
						p2.setScore(3);
					} else {
						p1.setScore(5);
						p2.setScore(7);
					}
				}
			}
			System.out.println("Score in round " + (j + 1) + ": " + sw.getRound(j));

		}

		sw.computeRanking();
		Map<String, Integer> fr = sw.getFinalRanking();
		
 
		System.out.format("%n                        W   H   Lawns     P+  S%n");

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
					for (int j = 0; j < 3; j++) {
						lawns.add(p.getLawnCount(j));
					}
					int starts = p.getStartCount();

					System.out.format("%2d %-20s %1d : %2d %-10s %2d %2d%n", pos, name, wins, hoops, lawns.toString(), prim, starts);
				}
			}
		}

	}

}