package uk.org.stevefisher.swiss;

import java.io.BufferedReader;
import java.io.Console;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import uk.org.stevefisher.swiss.logic.BasicSwiss;
import uk.org.stevefisher.swiss.logic.BasicSwiss.Colours;
import uk.org.stevefisher.swiss.logic.PersonScore;
import uk.org.stevefisher.swiss.logic.Player;
import uk.org.stevefisher.swiss.logic.SwissException;

public class Cmd {

	private static String readLine(String prompt) {
		String line = null;
		Console c = System.console();
		if (c != null) {
			line = c.readLine(prompt);
		} else {
			System.out.print(prompt);
			BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(System.in));
			try {
				line = bufferedReader.readLine();
			} catch (IOException e) {
				// Ignore
			}
		}
		return line;
	}

	public static int getWithDefaults(String name, int defaultValue) {
		String s = readLine(name + " (" + defaultValue + "): ");
		if (s.isEmpty()) {
			return defaultValue;
		} else {
			return Integer.parseInt(s);
		}
	}

	public static void main(String[] args) throws SwissException {
		int byeScore = getWithDefaults("byeScore", 26);
		int maxCombis = getWithDefaults("maxCombis", 1000000000);
		int enoughGood = getWithDefaults("enoughGood", 100);
		int numLawns = getWithDefaults("numLawns", 2);
		BasicSwiss tournament = new BasicSwiss(byeScore, maxCombis, enoughGood, numLawns);
		while (true) {
			String player = readLine("player (empty to end, finish name with -P or -S if CVD): ");
			if (player.isEmpty()) {
				break;
			}
			try {
				if (player.toUpperCase().endsWith("-P")) {
					tournament.addPlayer(player.substring(0, player.length() - 2).trim(), Colours.PRIMARY);
				} else if (player.toUpperCase().endsWith("-S")) {
					tournament.addPlayer(player.substring(0, player.length() - 2).trim(), Colours.SECONDARY);
				} else {
					tournament.addPlayer(player.trim());
				}
			} catch (SwissException e) {
				System.err.println(e.getMessage());
			}
		}
		System.out.println("Rounds KO:" + tournament.getKORounds() + ", Max:" + tournament.getMaxRounds()
				+ ", Recommended:" + tournament.getRecRounds());
		tournament.start();

		int roundNum = 1;

		boolean finished = false;
		while (!finished) {
			List<PersonScore> round = tournament.getRound(roundNum - 1);
			tournament.setByeScores();
			tournament.makeGamesChoices(round);
			boolean roundInProgress = true;
			while (roundInProgress) {
				try {
					int gameNum = Integer.parseInt(readLine("Game number (0 to continue) "));
					if (gameNum == 0) {
						if (isExitAllowed(round)) {
							roundInProgress = false;
						}
					} else {
						storeScores(round, gameNum);
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
			if (readLine("Enter FINISHED to end ").equals("FINISHED")) {
				finished = true;
			} else {
				tournament.prepareRound();
				roundNum++;
			}
		}

		Map<String, Integer> fr = tournament.getFinalRanking();
		System.out.println();

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

					System.out.format("%2d %s %d : %d %s %d %d%n", pos, name, wins, hoops, lawns.toString(), prim,
							starts);
				}
			}
		}
	}

	private static void storeScores(List<PersonScore> round, int gameNum) {
		int ngame = 1;
		for (int i = 0; i < round.size() / 2; i++) {
			PersonScore p1 = round.get(2 * i);
			PersonScore p2 = round.get(2 * i + 1);

			if (p1.getName().equals("Bye") || p2.getName().equals("Bye")) {
				// NOP
			} else if (gameNum == ngame++) {
				if (p1.getScore() != 0 || p2.getScore() != 0) {
					if (!readLine("Enter OVERWRITE to change score ").equals("OVERWRITE")) {
						return;
					}
				}
				int s1;
				int s2;
				try {
					s1 = Integer.parseInt(readLine("Score for: " + p1.getName() + ": "));
					s2 = Integer.parseInt(readLine("Score for: " + p2.getName() + ": "));
				} catch (NumberFormatException e) {
					System.out.println("Scores must be integers");
					return;
				}
				if (s1 == s2) {
					System.out.println("Draws are not allowed");
				} else {
					p1.setScore(s1);
					p2.setScore(s2);
				}
			}
		}

	}

	private static boolean isExitAllowed(List<PersonScore> round) {
		boolean exitAllowed = true;
		int ngame = 1;
		for (int i = 0; i < round.size() / 2; i++) {
			PersonScore p1 = round.get(2 * i);
			PersonScore p2 = round.get(2 * i + 1);
			if (p1.getName().equals("Bye") || p2.getName().equals("Bye")) {
				// NOP
			} else {
				if (p1.getScore() == 0 && p2.getScore() == 0) {
					System.out.println("Game " + ngame + " has no score recorded");
					exitAllowed = false;
				}
				ngame++;
			}
		}
		return exitAllowed;
	}

}
