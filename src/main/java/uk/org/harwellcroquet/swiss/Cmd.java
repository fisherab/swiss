package uk.org.harwellcroquet.swiss;

import java.io.Console;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import uk.org.harwellcroquet.swiss.logic.BasicSwiss;
import uk.org.harwellcroquet.swiss.logic.PersonScore;
import uk.org.harwellcroquet.swiss.logic.SwissException;

public class Cmd {

	public static void main(String[] args) throws SwissException {
		Console c = System.console();
		int byeScore = Integer.parseInt(c.readLine("byeScore: "));
		int maxCombis = Integer.parseInt(c.readLine("maxCombis: "));
		int enoughGood = Integer.parseInt(c.readLine("enoughGood: "));
		BasicSwiss game = new BasicSwiss(byeScore, maxCombis, enoughGood);
		while (true) {
			String player = c.readLine("player (empty to end): ");
			if (player.isEmpty()) {
				break;
			}
			game.addPlayer(player);
		}
		System.out.println("Rounds KO: " + game.getKORounds() + " Max :" + game.getMaxRounds());
		game.start();

		int roundNum = 1;

		while (true) {
			List<PersonScore> round = game.getRound(roundNum - 1);
			game.setByeScores();
			preRoundPrint(round);
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
					preRoundPrint(game.getRound(0));
				}
			}

			game.computeRanking();
			System.out.print("Ranking after round " + roundNum + " ");
			for (String name : game.getRanking()) {
				System.out.print(name + ": " + game.getPlayers().get(name).getGames() + "  ");
			}
			System.out.println();
			if (c.readLine("Enter FINISHED to end ").equals("FINISHED")) {
				break;
			}
			game.prepareRound();
			roundNum++;
		}
		
		Map<String, Integer> fr = game.getFinalRanking();
		System.out.print("Final ranking ");
		boolean first = true;
		for (int i = 1; i <= game.getPlayers().size(); i++) {
			for (Entry<String, Integer> entry : fr.entrySet()) {
				if (entry.getValue() == i) {
					if (!first) {
						System.out.print(", ");
					} else {
						first = false;
					}
					System.out.print(entry);
				}
			}
		}
		System.out.println();
	}

	private static void preRoundPrint(List<PersonScore> round) {
		String bye = null;
		int ngame = 1;
		for (int i = 0; i < round.size() / 2; i++) {
			PersonScore p1 = round.get(2 * i);
			PersonScore p2 = round.get(2 * i + 1);
			if (p1.getName().equals("Bye")) {
				bye = p2.getName();
			} else if (p2.getName().equals("Bye")) {
				bye = p1.getName();
			} else {
				System.out.println("Game " + ngame++ + ": " + p1 + " vs " + p2);
			}

		}
		if (bye != null) {
			System.out.println(bye + " gets a bye");
		}

	}

}
