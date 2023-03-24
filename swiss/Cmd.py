from swiss import Logic
import logging
from pathlib import Path

logging.basicConfig(filename='cmd.log', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)

class Cmd(object):

    @staticmethod
    def getWithDefaults(name, defaultValue):
        s = input(name + " (" + str(defaultValue) + "): ").strip();
        if s == "": return defaultValue
        else: return int(s)

    def run(self):
        logger.info("We're running")

        byeScore = Cmd.getWithDefaults("byeScore", 26);
        maxCombis = Cmd.getWithDefaults("maxCombis", 1000000000);
        enoughGood = Cmd.getWithDefaults("enoughGood", 100);
        numLawns = Cmd.getWithDefaults("numLawns", 2);

        print(byeScore)

        tournament = Logic.Tournament(byeScore, maxCombis, enoughGood, numLawns)
        journal = Path("journal.txt")
        journalRecovery = False
        lines = []
        if journal.is_file():
            journalRecovery = True
            logger.info("Recovering from journal file")
            names = []
            with journal.open() as j:
                players = j.readline().strip().split(",")
                print (players)
                for player in players:
                    player = player.strip()
                    if player.upper()[-2:] == "-P":
                        name = player[:-2].trim()
                        names.append(name);
                        tournament.addPlayer(name, Colours.PRIMARY, allowBye = True);
                    elif player.upper()[-2:] == "-S":
                        name = player[:-2].trim()
                        names.append(name);
                        tournament.addPlayer(name, Colours.SECONDARY, allowBye = True);
                    else:
                        name = player
                        names.append(name);
                        tournament.addPlayer(name, allowBye = True);
                    
                for line in j: lines.append(line)
                tournament.startWithNames(names);
                
        else: # No journal recovery
            while True:
                player = input("player (empty to end, finish name with -P or -S if CVD): ").trim()
                if player == "": break
                
                if player.upper()[-2:] == "-P":
                    tournament.addPlayer(player[:-2].trim(), Colours.PRIMARY)
                elif player.upper()[-2:] == "-S":
                    tournament.addPlayer(player[:-2].trim(), Colours.SECONDARY)
                else:
                    tournament.addPlayer(player.trim())
                        
            tournament.start();
          
        print("Rounds KO:" + str(tournament.getKORounds()) + ", Max:" + str(tournament.getMaxRounds())
                + ", Recommended:" + str(tournament.getRecRounds()))

        roundNum = 1
        if journalRecovery:
            roundsInJournal = len(lines)* 2 // len(tournament.players)
            if len(lines) * 2 % len(tournament.players) != 0: raise Exception("The journal.txt file has an incomplete round - please correct it manually and try again");
            linenum = 0
            for roff in range(roundsInJournal):
                round = tournament.rounds[roff]
                tournament.makeGamesChoices(round)
                psj = {}
                for k in range(len(tournament.players) // 2):
                    bits = lines[linenum].split(",")
                    linenum += 1           
                    psj[bits[0]] = int(bits[3])
                    psj[bits[2]] = int(bits[4])
                
                for pos in range(len(round)):
                    name = round[pos][0]
                    round[pos] = [name, psj[name]]
                tournament.computeRanking()
                res = "Ranking after round " + str(roundNum)
                for name in tournament.ranking: res += "  " + name + ": " + str(tournament.players[name].games)
                logger.info(res)
                
                tournament.prepareRound()
                roundNum += 1
              
            logger.info("Recovery of " + str(roundsInJournal) + " rounds complete")
 
        finished = False
        
##		while (!finished) {
##			System.out.println("Starting round " + roundNum);
##			List<PersonScore> round = tournament.getRound(roundNum - 1);
##			tournament.setByeScores();
##			tournament.makeGamesChoices(round);
##			boolean roundInProgress = true;
##			while (roundInProgress) {
##				String cmd = readLine("Game number, S(tatus), E(nd round) ").toUpperCase().trim();
##				if ("S".equals(cmd)) {
##					printStatus(round);
##				} else if ("E".equals(cmd)) {
##					if (isExitAllowed(round)) {
##						roundInProgress = false;
##					}
##				} else {
##					try {
##						int gameNum = Integer.parseInt(cmd);
##						storeScores(round, gameNum);
##					} catch (NumberFormatException e) {
##						System.out.println("Invalid input");
##					}
##				}
##			}
##
##			try {
##				tournament.writeLog(round, roundNum == 1);
##			} catch (SwissException e) {
##				System.out.println("Failed to write log");
##			}
##
##			tournament.computeRanking();
##			System.out.print("Ranking after round " + roundNum + " ");
##			for (String name : tournament.getRanking()) {
##				System.out.print(name + ": " + tournament.getPlayers().get(name).getGames() + "  ");
##			}
##			System.out.println();
##			boolean finishChoiceMade = false;
##			while (!finishChoiceMade) {
##				if (roundNum >= tournament.getRecRounds()) {
##					System.out.println("You have completed the recommended number of rounds.");
##				}
##				if (roundNum >= tournament.getMaxRounds()) {
##					System.out.println("You have completed the maximum number of rounds.");
##					finished = true;
##					finishChoiceMade = true;
##					continue;
##				}
##				String cmd = readLine("FINISH (tournament), NEXT (to start next round) ").toUpperCase().trim();
##				if ("FINISH".equals(cmd)) {
##					finished = true;
##					finishChoiceMade = true;
##				} else if ("NEXT".equals(cmd)) {
##					try {
##						tournament.prepareRound();
##					} catch (SwissException e) {
##						System.out.println(e.getMessage());
##						System.out.println("Tournament will finish");
##						finished = true;
##						finishChoiceMade = true;
##						continue;
##					}
##					roundNum++;
##					finishChoiceMade = true;
##				}
##			}
##		}
##
##		Path source = Paths.get("journal.txt");
##		String strDate = new SimpleDateFormat("yyyy-MM-dd").format(Calendar.getInstance().getTime());
##		Path target = Paths.get("gamelog-" + strDate + ".txt");
##		try {
##			Files.move(source, target, StandardCopyOption.REPLACE_EXISTING);
##		} catch (IOException e) {
##			System.out.println("You have failed to rename " + source + " to " + target);
##		}
##
##		Map<String, Integer> fr = tournament.getFinalRanking();
##		System.out.println();
##
##		System.out.format("%2s %-18.18s %4.4s : %5.5s %-12.12s %9.9s %6.6s%n", " #", "name", "wins", "hoops", "lawns",
##				"primaryXS", "starts");
##		for (int i = 1; i <= tournament.getPlayers().size(); i++) {
##			for (Entry<String, Integer> entry : fr.entrySet()) {
##				if (entry.getValue() == i) {
##					String name = entry.getKey();
##					int pos = entry.getValue();
##					Player p = tournament.getPlayers().get(name);
##					int wins = p.getGames();
##					int hoops = p.getHoops();
##					int prim = p.getPrimaryExcess();
##					List<Integer> lawns = new ArrayList<>();
##					for (int j = 0; j < numLawns; j++) {
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
##	private static void printStatus(List<PersonScore> round) {
##		int ngame = 1;
##		for (int i = 0; i < round.size() / 2; i++) {
##			PersonScore p1 = round.get(2 * i);
##			PersonScore p2 = round.get(2 * i + 1);
##			if (!p1.getName().equals("Bye") && !p2.getName().equals("Bye")) {
##				System.out.println("Game " + ngame++ + ": " + p1 + " vs " + p2);
##			}
##		}
##	}
##
##	private static void storeScores(List<PersonScore> round, int gameNum) {
##		int ngame = 1;
##		for (int i = 0; i < round.size() / 2; i++) {
##			PersonScore p1 = round.get(2 * i);
##			PersonScore p2 = round.get(2 * i + 1);
##
##			if (p1.getName().equals("Bye") || p2.getName().equals("Bye")) {
##				// NOP
##			} else if (gameNum == ngame++) {
##				if (p1.getScore() != 0 || p2.getScore() != 0) {
##					if (!readLine("Enter OVERWRITE to change score ").toUpperCase().trim().equals("OVERWRITE")) {
##						return;
##					}
##				}
##				int s1;
##				int s2;
##				try {
##					s1 = Integer.parseInt(readLine("Score for: " + p1.getName() + ": "));
##					s2 = Integer.parseInt(readLine("Score for: " + p2.getName() + ": "));
##				} catch (NumberFormatException e) {
##					System.out.println("Scores must be integers");
##					return;
##				}
##				if (s1 == s2) {
##					System.out.println("Draws are not allowed");
##				} else {
##					p1.setScore(s1);
##					p2.setScore(s2);
##				}
##			}
##		}
##
##	}
##
##	private static boolean isExitAllowed(List<PersonScore> round) {
##		boolean exitAllowed = true;
##		int ngame = 1;
##		for (int i = 0; i < round.size() / 2; i++) {
##			PersonScore p1 = round.get(2 * i);
##			PersonScore p2 = round.get(2 * i + 1);
##			if (p1.getName().equals("Bye") || p2.getName().equals("Bye")) {
##				// NOP
##			} else {
##				if (p1.getScore() == 0 && p2.getScore() == 0) {
##					System.out.println("Game " + ngame + " has no score recorded");
##					exitAllowed = false;
##				}
##				ngame++;
##			}
##		}
##		return exitAllowed;
##	}


def main():
    cmd = Cmd()
    cmd.run()

if __name__ == "__main__":
    main()
