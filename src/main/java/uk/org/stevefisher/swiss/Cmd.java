package uk.org.stevefisher.swiss;

import java.io.BufferedReader;
import java.io.Console;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.HashMap;
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
		String s = readLine(name + " (" + defaultValue + "): ").trim();
		if (s.isEmpty()) {
			return defaultValue;
		} else {
			return Integer.parseInt(s);
		}
	}

	public static void main(String[] args) {
		Cmd cmd = new Cmd();
		cmd.run();
	}

	private void run() {

		int byeScore = getWithDefaults("byeScore", 26);
		int maxCombis = getWithDefaults("maxCombis", 1000000000);
		int enoughGood = getWithDefaults("enoughGood", 100);
		int numLawns = getWithDefaults("numLawns", 2);

		BasicSwiss tournament = new BasicSwiss(byeScore, maxCombis, enoughGood, numLawns);
		Path journal = Paths.get("journal.txt");
		boolean journalRecovery = false;
		List<String> lines = new ArrayList<String>();
		if (Files.exists(journal)) {
			journalRecovery = true;
			System.out.println("Recovering from journal file");
			List<String> names = new ArrayList<String>();
			try (BufferedReader f = new BufferedReader(new FileReader(journal.toFile()))) {
				String[] players = f.readLine().split(",");
				for (String player : players) {

					if (player.toUpperCase().endsWith("-P")) {
						String name = player.substring(0, player.length() - 2).trim();
						names.add(name);
						tournament.addPlayer(name, Colours.PRIMARY, true);
					} else if (player.toUpperCase().endsWith("-S")) {
						String name = player.substring(0, player.length() - 2).trim();
						names.add(name);
						tournament.addPlayer(name, Colours.SECONDARY, true);
					} else {
						String name = player.trim();
						names.add(name);
						tournament.addPlayer(name, true);
					}
				}
				String line;
				while ((line = f.readLine()) != null) {
					lines.add(line);
				}
				tournament.start(names);
			} catch (Exception e) {
				System.err.println(e.getMessage());
				System.exit(1);
			}
		} else {
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
			try {
				tournament.start();
			} catch (SwissException e) {
				System.err.println(e.getMessage());
				System.exit(1);
			}
		}

		System.out.println("Rounds KO:" + tournament.getKORounds() + ", Max:" + tournament.getMaxRounds()
				+ ", Recommended:" + tournament.getRecRounds());

		int roundNum = 1;
		if (journalRecovery) {
			int roundsInJournal = lines.size() * 2 / tournament.getPlayers().size();
			if ((lines.size() * 2 % tournament.getPlayers().size()) != 0) {
				System.err.println("The journal.txt file has an incomplete round - please correct it manually and try again");
				System.exit(1);
			}
			int linenum = 0;
			for (int roff = 0; roff < roundsInJournal; roff++) {
				List<PersonScore> round = tournament.getRound(roff);
				tournament.makeGamesChoices(round);
				Map<String, Integer> psj = new HashMap<String, Integer>();
				for (int k = 0; k < tournament.getPlayers().size() / 2; k++) {
					String[] bits = lines.get(linenum++).split(",");
					psj.put(bits[0], Integer.parseInt(bits[3]));
					psj.put(bits[2], Integer.parseInt(bits[4]));
				}
				for (PersonScore ps : round) {
					ps.setScore(psj.get(ps.getName()));
				}
				tournament.computeRanking();
				System.out.print("Ranking after round " + roundNum + " ");
				for (String name : tournament.getRanking()) {
					System.out.print(name + ": " + tournament.getPlayers().get(name).getGames() + "  ");
				}
				System.out.println();
				try {
					tournament.prepareRound();
					roundNum++;
				} catch (SwissException e) {
					System.err.println(e.getMessage());
					System.exit(1);
				}
			}
			System.out.println("Recovery of " + roundsInJournal + " rounds complete\n");
		}

		boolean finished = false;
		while (!finished) {
			System.out.println("Starting round " + roundNum);
			List<PersonScore> round = tournament.getRound(roundNum - 1);
			tournament.setByeScores();
			tournament.makeGamesChoices(round);
			boolean roundInProgress = true;
			while (roundInProgress) {
				String cmd = readLine("Game number, S(tatus), E(nd round) ").toUpperCase().trim();
				if ("S".equals(cmd)) {
					printStatus(round);
				} else if ("E".equals(cmd)) {
					if (isExitAllowed(round)) {
						roundInProgress = false;
					}
				} else {
					try {
						int gameNum = Integer.parseInt(cmd);
						storeScores(round, gameNum);
					} catch (NumberFormatException e) {
						System.out.println("Invalid input");
					}
				}
			}

			try {
				tournament.writeLog(round, roundNum == 1);
			} catch (SwissException e) {
				System.out.println("Failed to write log");
			}

			tournament.computeRanking();
			System.out.print("Ranking after round " + roundNum + " ");
			for (String name : tournament.getRanking()) {
				System.out.print(name + ": " + tournament.getPlayers().get(name).getGames() + "  ");
			}
			System.out.println();
			boolean finishChoiceMade = false;
			while (!finishChoiceMade) {
				if (roundNum >= tournament.getRecRounds()) {
					System.out.println("You have completed the recommended number of rounds.");
				}
				if (roundNum >= tournament.getMaxRounds()) {
					System.out.println("You have completed the maximum number of rounds.");
					finished = true;
					finishChoiceMade = true;
					continue;
				}
				String cmd = readLine("FINISH (tournament), NEXT (to start next round) ").toUpperCase().trim();
				if ("FINISH".equals(cmd)) {
					finished = true;
					finishChoiceMade = true;
				} else if ("NEXT".equals(cmd)) {
					try {
						tournament.prepareRound();
					} catch (SwissException e) {
						System.out.println(e.getMessage());
						System.out.println("Tournament will finish");
						finished = true;
						finishChoiceMade = true;
						continue;
					}
					roundNum++;
					finishChoiceMade = true;
				}
			}
		}

		Path source = Paths.get("journal.txt");
		String strDate = new SimpleDateFormat("yyyy-MM-dd").format(Calendar.getInstance().getTime());
		Path target = Paths.get("gamelog-" + strDate + ".txt");
		try {
			Files.move(source, target, StandardCopyOption.REPLACE_EXISTING);
		} catch (IOException e) {
			System.out.println("You have failed to rename " + source + " to " + target);
		}

		Map<String, Integer> fr = tournament.getFinalRanking();
		System.out.println();

		System.out.format("%2s %-18.18s %4.4s : %5.5s %-12.12s %9.9s %6.6s%n", " #", "name", "wins", "hoops", "lawns",
				"primaryXS", "starts");
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

					System.out.format("%2d %-18.18s %4d : %5d %-12.12s %9d %6d%n", pos, name, wins, hoops,
							lawns.toString(), prim, starts);
				}
			}
		}
	}

	private static void printStatus(List<PersonScore> round) {
		int ngame = 1;
		for (int i = 0; i < round.size() / 2; i++) {
			PersonScore p1 = round.get(2 * i);
			PersonScore p2 = round.get(2 * i + 1);
			if (!p1.getName().equals("Bye") && !p2.getName().equals("Bye")) {
				System.out.println("Game " + ngame++ + ": " + p1 + " vs " + p2);
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
					if (!readLine("Enter OVERWRITE to change score ").toUpperCase().trim().equals("OVERWRITE")) {
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
