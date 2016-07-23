package uk.org.harwellcroquet.swiss;

import java.io.Console;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import uk.org.harwellcroquet.swiss.logic.BasicSwiss;
import uk.org.harwellcroquet.swiss.logic.BasicSwiss.Colours;
import uk.org.harwellcroquet.swiss.logic.PersonScore;
import uk.org.harwellcroquet.swiss.logic.Player;
import uk.org.harwellcroquet.swiss.logic.SwissException;

public class Cmd {

	public static void main(String[] args) throws SwissException {
		Console c = System.console();
		int byeScore = Integer.parseInt(c.readLine("byeScore: "));
		int maxCombis = Integer.parseInt(c.readLine("maxCombis: "));
		int enoughGood = Integer.parseInt(c.readLine("enoughGood: "));
		int numLawns = Integer.parseInt(c.readLine("numLawns: "));
		BasicSwiss tournament = new BasicSwiss(byeScore, maxCombis, enoughGood, numLawns);
		while (true) {
			String player = c.readLine("player (empty to end, finish name with -P or -S if CVD): ");
			if (player.isEmpty()) {
				break;
			}
			if (player.endsWith("-P")) {
				tournament.addPlayer(player.substring(0, player.length() - 3), Colours.PRIMARY);
			} else if (player.endsWith("-S")) {
				tournament.addPlayer(player.substring(0, player.length() - 3), Colours.SECONDARY);
			} else {
				tournament.addPlayer(player);
			}
		}
		System.out.println("Rounds KO: " + tournament.getKORounds() + " Max :" + tournament.getMaxRounds());
		tournament.start();

		int roundNum = 1;

		while (true) {
			List<PersonScore> round = tournament.getRound(roundNum - 1);
			tournament.setByeScores();
			tournament.makeGamesChoices(round);
			outer: while (true) {
				try {
					int gameNum = Integer.parseInt(c.readLine("Game number (0 to continue) "));
					int ngame = 1;
					if (gameNum == 0) {
						for (int i = 0; i < round.size() / 2; i++) {
							PersonScore p1 = round.get(2 * i);
							PersonScore p2 = round.get(2 * i + 1);
							if (p1.getName().equals("Bye") || p2.getName().equals("Bye")) {
								// NOP
							} else {
								if (p1.getScore() == 0 && p2.getScore() == 0) {
									System.out.println("Game " + ngame + " has no score recorded");
									continue outer;
								}
								ngame++;
							}
						}
						break;
					} else {
						for (int i = 0; i < round.size() / 2; i++) {
							PersonScore p1 = round.get(2 * i);
							PersonScore p2 = round.get(2 * i + 1);
							if (p1.getName().equals("Bye") || p2.getName().equals("Bye")) {
								// NOP
							} else if (gameNum == ngame++) {
								if (p1.getScore() != 0 || p2.getScore() != 0) {
									if (!c.readLine("Enter OVERWRITE to change score ").equals("OVERWRITE")) {
										continue outer;
									}
								}
								int s1 = Integer.parseInt(c.readLine("Score for: " + p1.getName() + ": "));
								int s2 = Integer.parseInt(c.readLine("Score for: " + p2.getName() + ": "));
								if (s1 == s2) {
									System.out.println("Draws are not allowed");
								} else {
									p1.setScore(s1);
									p2.setScore(s2);
								}
							}
						}
					}
				} catch (NumberFormatException e) {
					int ngame = 1;
					for (int i = 0; i < round.size() / 2; i++) {
						PersonScore p1 = round.get(2 * i);
						PersonScore p2 = round.get(2 * i + 1);
						if (!p1.getName().equals("Bye") && !p2.getName().equals("Bye")) {
							System.out.println("Game " + ngame++ + ": " + p1 + " vs " + p2);
						}
					}
				}
			}

			tournament.computeRanking();
			System.out.print("Ranking after round " + roundNum + " ");
			for (String name : tournament.getRanking()) {
				System.out.print(name + ": " + tournament.getPlayers().get(name).getGames() + "  ");
			}
			System.out.println();
			if (c.readLine("Enter FINISHED to end ").equals("FINISHED")) {
				break;
			}
			tournament.prepareRound();
			roundNum++;
		}

		Map<String, Integer> fr = tournament.getFinalRanking();
		System.out.format("%n                        W   H   Lawns     P+  S%n");

		for (int i = 1; i <= tournament.getPlayers().size(); i++) {
			for (Entry<String, Integer> entry : fr.entrySet()) {
				if (entry.getValue() == i) {
					String name = entry.getKey();
					int pos = entry.getValue();
					Player p = tournament.getPlayers().get(name);
					int wins = p.getGames();
					int hoops = p.getHoops();
					int prim = p.getPrimaryExcess();
					List<Integer> lawns = new ArrayList<>();
					for (int j = 0; j < numLawns; j++) {
						lawns.add(p.getLawnCount(j));
					}
					int starts = p.getStartCount();

					System.out.format("%2d %-20s %1d : %2d %-10s %2d %2d%n", pos, name, wins, hoops, lawns.toString(),
							prim, starts);
				}
			}
		}
	}

}
