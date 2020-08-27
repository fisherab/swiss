package uk.org.stevefisher.swiss.logic;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import org.apache.commons.math3.util.CombinatoricsUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class BasicSwiss {

	public static class CombResult {

		Boolean more;
		int numGood;
		public Set<Game> bestGames;
		public long bestSumSquares;

		public CombResult(Boolean more, int numGood, Set<Game> bestGames, long bestSumSquares) {
			this.more = more;
			this.numGood = numGood;
			this.bestGames = bestGames;
			this.bestSumSquares = bestSumSquares;
		}

		@Override
		public String toString() {
			return "More:" + more + " numGood:" + numGood + " bestGames:" + bestGames + " bestSumSquares:"
					+ bestSumSquares;
		}

	}

	private static final Logger logger = LogManager.getLogger(BasicSwiss.class);

	public enum Colours {
		PRIMARY, SECONDARY
	};

	enum Status {
		STARTED, SETTING_UP
	};

	Status status = Status.SETTING_UP;

	private Map<String, Player> players = new HashMap<>();

	private List<List<PersonScore>> rounds = new ArrayList<>();

	private int byeScore;

	private ArrayList<String> ranking;

	private BigInteger maxCombis;

	private Integer enoughGood;

	private BigInteger combis;

	private int numLawns;

	public BasicSwiss(int byeScore, int maxCombis, Integer enoughGood, int numLawns) {
		this.byeScore = byeScore;
		this.maxCombis = BigInteger.valueOf(maxCombis);
		this.enoughGood = enoughGood;
		this.numLawns = numLawns;
	}

	public void addPlayer(String name, Colours col) throws SwissException {
		if (players.containsKey(name)) {
			throw new SwissException("Player " + name + " already present");
		} else if (name.equals("Bye")) {
			throw new SwissException("The player name 'Bye' is reserved");
		}
		if (col != null) {
			logger.info(name + " will get " + col);
		}
		players.put(name, new Player(name, col));
	}

	/** Create first round (numbered 0) and add it to rounds list */
	public void start() throws SwissException {
		if (status == Status.SETTING_UP) {
			status = Status.STARTED;
			if (players.size() % 2 == 1) {
				players.put("Bye", new Player("Bye", null));
			}
			List<PersonScore> round = new ArrayList<>();
			for (String name : players.keySet()) {
				PersonScore ps = new PersonScore(name);
				round.add(ps);
			}
			Collections.shuffle(round);
			rounds.add(round);
		} else {
			throw new SwissException("Invalid status for start to be called");
		}
	}

	public List<PersonScore> getRound(int i) {
		return rounds.get(i);
	}

	public void setByeScores() {
		List<PersonScore> round = rounds.get(rounds.size() - 1);
		int ngames = round.size() / 2;
		for (int i = 0; i < ngames; i++) {
			PersonScore p1 = round.get(2 * i);
			PersonScore p2 = round.get(2 * i + 1);
			if (p1.getName().equals("Bye")) {
				p2.setScore(byeScore);
			} else if (p2.getName().equals("Bye")) {
				p1.setScore(byeScore);
			}
		}
	}

	public void computeRanking() {
		int roundNum = rounds.size() - 1;
		int maxScore = roundNum + 1;
		List<PersonScore> round = rounds.get(roundNum);
		ranking = new ArrayList<>();
		int ngames = round.size() / 2;
		for (int i = 0; i < ngames; i++) {
			PersonScore p1 = round.get(2 * i);
			PersonScore p2 = round.get(2 * i + 1);
			if (p1.getScore() > p2.getScore()) {
				players.get(p1.getName()).incrementGames();
			} else {
				players.get(p2.getName()).incrementGames();
			}
			players.get(p1.getName()).addPlayed(p2.getName());
			players.get(p1.getName()).addHoops(p1.getScore());
			players.get(p2.getName()).addPlayed(p1.getName());
			players.get(p2.getName()).addHoops(p2.getScore());
		}
		for (int i = maxScore; i >= 0; i--) {
			for (PersonScore ps : round) {
				if (players.get(ps.getName()).getGames() == i) {
					ranking.add(ps.getName());
				}
			}
		}
	}

	/**
	 * Create a new round and add it to the rounds list.
	 */
	public void prepareRound() throws SwissException {
		List<String> tempRanking = new ArrayList<>(ranking);
		List<PersonScore> round = new ArrayList<>();
		rounds.add(round);
		List<String> lowNames = new ArrayList<>();

		Player p2 = null;
		while (true) {
			// Find the topmost person
			Player p1 = null;
			int i;
			for (i = 0; i < tempRanking.size(); i++) {
				String name = tempRanking.get(i);
				if (name != null) {
					p1 = players.get(name);
					break;
				}
			}
			if (p1 == null) {
				break;
			}
			tempRanking.set(i, null);

			// and the next person he has not played
			p2 = null;
			for (i++; i < tempRanking.size(); i++) {
				String name = tempRanking.get(i);
				if (name != null && p1.hasNotPlayed(name)) {
					p2 = players.get(name);
					break;
				}
			}
			if (p2 == null) {
				break;
			}
			tempRanking.set(i, null);
			round.add(new PersonScore(p1.getName()));
			round.add(new PersonScore(p2.getName()));

			// Find the lowest person
			p1 = null;
			for (i = tempRanking.size() - 1; i >= 0; i--) {
				String name = tempRanking.get(i);
				if (name != null) {
					p1 = players.get(name);
					break;
				}
			}
			if (p1 == null) {
				break;
			}
			tempRanking.set(i, null);

			// and the next person he has not played
			p2 = null;
			for (i--; i >= 0; i--) {
				String name = tempRanking.get(i);
				if (name != null && p1.hasNotPlayed(name)) {
					p2 = players.get(name);
					break;
				}
			}
			if (p2 == null) {
				break;
			}
			tempRanking.set(i, null);
			lowNames.add(p1.getName());
			lowNames.add(p2.getName());

		}
		Collections.reverse(lowNames);
		for (String name : lowNames) {
			round.add(new PersonScore(name));
		}

		if (p2 == null) {
			// There were clashes so compute set of all possible (i.e. non-played) games
			List<Game> games = new ArrayList<>();
			for (String name1 : players.keySet()) {
				for (String name2 : players.keySet()) {
					if (name1.compareTo(name2) < 0 && players.get(name1).hasNotPlayed(name2)) {
						int i = ranking.indexOf(name1) - ranking.indexOf(name2);
						games.add(new Game(name1, name2, i * i));
					}
				}
			}

			// These games could be played in any order - work out how many combinations and
			// print for information
			int gamesPerRound = players.size() / 2;
			combis = cNR(games.size(), gamesPerRound);
			System.out.print("There are " + games.size() + " with " + combis + " combinations. "
					+ (combis.compareTo(maxCombis) > 0 ? "Truncate. " : ""));

			// Sort the games by fairness i.e. how close in ranking
			Collections.sort(games, new Comparator<Game>() {
				@Override
				public int compare(Game g1, Game g2) {
					return g1.getSquare() - g2.getSquare();
				}
			});

			// Compute bestGames via recursive call
			CombResult combResult = combinationsTwo(games, gamesPerRound, new HashSet<Game>(), 0, new HashSet<String>(),
					combis.compareTo(maxCombis) > 0 ? enoughGood : null);
			if (combResult.bestGames == null) {
				combResult = combinationsThree(games, gamesPerRound,
						combis.compareTo(maxCombis) > 0 ? enoughGood : null);
			}
			logger.debug("Best is {}", combResult.bestGames);

			round.clear();

			if (combResult.bestGames == null) {
				throw new SwissException("No valid combination of games found");
			}
			for (Game game : combResult.bestGames) {
				round.add(new PersonScore(game.getName1()));
				round.add(new PersonScore(game.getName2()));
			}

		}

	}

	static BigInteger cNR(final int N, final int K) {
		BigInteger ret = BigInteger.ONE;
		for (int k = 0; k < K; k++) {
			ret = ret.multiply(BigInteger.valueOf(N - k)).divide(BigInteger.valueOf(k + 1));
		}
		return ret;
	}

	/**
	 * Recursive function to return best set of games
	 * 
	 * @param games         Array of possible Games
	 * @param gamesPerRound Number of games to have a complete valid round
	 * @param inResults     games in the chain so far
	 * @param inSum         Count of sum of squares of games in the chain
	 * @param inNames       set of player names already allocated in the chain
	 * @param enoughGood    if not null the calculation should only consider
	 *                      enoughGood valid combinations
	 * @return CombResult
	 */
	static CombResult combinationsTwo(List<Game> games, int gamesPerRound, Set<Game> inResults, long inSum,
			Set<String> inNames, Integer enoughGood) {
		logger.debug("Selecting from games:{}, inResults:{}, inNames:{}, inSum:{}", games, inResults, inNames, inSum);
		long bestSumSquares = Long.MAX_VALUE;
		Set<Game> bestGames = null;
		Set<Game> badGames = new HashSet<Game>();
		int numGood = 0;
		boolean more = true;
		int offset = 0;
		for (Game game : games) {
			offset++;
			Set<String> names = new HashSet<>(inNames);
			if (names.add(game.getName1()) && names.add(game.getName2())) {
				Set<Game> results = new HashSet<Game>(inResults);
				results.add(game);
				long sum = inSum + game.getSquare();
				if (results.size() == gamesPerRound) {
					numGood++;
					if (sum < bestSumSquares) {
						bestSumSquares = sum;
						bestGames = results;
					}
				} else {
					List<Game> gamesToConsider = new ArrayList<>();
					for (Game g : games.subList(offset, games.size())) {
						if (!badGames.contains(g)) {
							gamesToConsider.add(g);
						}
					}
					CombResult combresult = combinationsTwo(gamesToConsider, gamesPerRound, results, sum, names,
							enoughGood);
					if (combresult.bestSumSquares < bestSumSquares) {
						bestSumSquares = combresult.bestSumSquares;
						bestGames = combresult.bestGames;
					}
					numGood += combresult.numGood;
					if (enoughGood != null && numGood >= enoughGood) {
						logger.debug("Enough results");
						more = false;
						break;
					}
				}
			} else {
				badGames.add(game);
				logger.debug("Game rejected {}", game);
			}
		}
		CombResult combresult = new CombResult(more, numGood, bestGames, bestSumSquares);
		logger.debug("Returning {}", combresult);
		return combresult;
	}

	static CombResult combinationsThree(List<Game> games, int gamesPerRound, Integer enoughGood) {
		Iterator<int[]> iterator = CombinatoricsUtils.combinationsIterator(games.size(), gamesPerRound);
		long bestSumSquares = Long.MAX_VALUE;
		boolean more = true;
		Set<Game> bestGames = null;
		int numGood = 0;
		while (iterator.hasNext()) {
			int sum = 0;
			Set<String> players = new HashSet<String>();
			int[] gs = iterator.next();
			for (int g : gs) {
				Game game = games.get(g);
				if (!players.add(game.getName1()) || !players.add(game.getName2())) {
					break;
				}
				sum += game.getSquare();
			}
			if (players.size() == gamesPerRound * 2) {
				numGood++;
				if (sum < bestSumSquares) {
					bestSumSquares = sum;
					bestGames = new HashSet<Game>();
					for (int g : gs) {
						bestGames.add(games.get(g));
					}
				}
				if (enoughGood != null && numGood >= enoughGood) {
					logger.debug("Enough results");
					more = false;
					break;
				}
			}
		}
		return new CombResult(more, numGood, bestGames, bestSumSquares);
	}

	public ArrayList<String> getRanking() {
		return ranking;
	}

	public Map<String, Player> getPlayers() {
		return players;
	}

	public int getKORounds() {
		int maxPeople = 2;
		int koRounds = 1;
		while (maxPeople < players.size()) {
			maxPeople = maxPeople * 2;
			koRounds++;
		}
		return koRounds;
	}

	public int getMaxRounds() {
		return players.size() - 1;
	}

	public int getRecRounds() {
		return Math.min(getKORounds() + 2, getMaxRounds());
	}

	public Map<String, Integer> getFinalRanking() {
		Map<Integer, Set<Player>> r = new HashMap<>();

		for (Player p : players.values()) {
			if (!p.getName().equals("Bye")) {
				int n = p.getGames();
				Set<Player> set = r.get(n);
				if (set == null) {
					set = new HashSet<>();
					r.put(n, set);
				}
				set.add(p);
			}
		}
		List<Integer> keys = new ArrayList<>(r.keySet());
		Collections.sort(keys);
		Collections.reverse(keys);
		Map<String, Integer> result = new HashMap<>();
		int npos = 1;
		for (Integer key : keys) {
			// Set of players with same number of wins
			List<Player> set = new ArrayList<>(r.get(key));
			while (set.size() > 0) {
				if (set.size() == 1) {
					result.put(set.get(0).getName(), npos++);
					set.clear();
				} else {
					System.out.print("Need winner from " + set);
					String best = getBest(set);
					if (best != null) {
						Iterator<Player> iter = set.iterator();
						while (iter.hasNext()) {
							if (iter.next().getName().equals(best)) {
								result.put(best, npos++);
								iter.remove();
								break;
							}
						}
					} else {
						for (Player p : set) {
							result.put(p.getName(), npos);
						}
						npos += set.size();
						set.clear();
					}
				}
			}
		}
		return result;
	}

	/* Set will always have at least two members */
	private String getBest(List<Player> set) {
		Map<String, Integer> names = new HashMap<>();
		for (Player p : set) {
			names.put(p.getName(), 0);
		}

		int wins = 0;
		for (List<PersonScore> round : rounds) {
			int ngames = round.size() / 2;
			for (int i = 0; i < ngames; i++) {
				PersonScore p1r = round.get(2 * i);
				PersonScore p2r = round.get(2 * i + 1);
				if (names.containsKey(p1r.getName()) && names.containsKey(p2r.getName())) {
					if (p1r.getScore() > p2r.getScore()) {
						names.put(p1r.getName(), names.get(p1r.getName()) + 1);
					} else {
						names.put(p2r.getName(), names.get(p2r.getName()) + 1);
					}
					wins++;
				}
			}
		}

		if (set.size() == 2) {
			String n1 = set.get(0).getName();
			String n2 = set.get(1).getName();
			if (wins == 1) {
				if (names.get(n1) > names.get(n2)) {
					System.out.println(", " + n1 + " beat " + n2 + " in a round");
					return n1;
				} else {
					System.out.println(", " + n2 + " beat " + n1 + " in a round");
					return n2;
				}
			} else {
				return mostHooper(set);
			}
		} else {// Three or more in tie
			System.out.print(", games won in tie " + names);
			if (wins == set.size() * (set.size() - 1) / 2) {
				System.out.print(", all played");
				int max = 0;
				for (Entry<String, Integer> name : names.entrySet()) {
					if (name.getValue() > max) {
						max = name.getValue();
					}
				}
				String best = null;
				for (Entry<String, Integer> name : names.entrySet()) {
					if (name.getValue() == max) {
						if (best == null) {
							best = name.getKey();
						} else {
							return mostHooper(set);
						}
					}
				}
				System.out.println(", " + best + " beat others in tie ");
				return best;
			} else {
				System.out.print(", not all played");
				int needed = set.size() - 1;
				String best = null;
				for (Entry<String, Integer> name : names.entrySet()) {
					if (name.getValue() == needed) {
						if (best == null) {
							best = name.getKey();
						} else {
							return mostHooper(set);
						}
					}
				}
				if (best != null) {
					System.out.println(", " + best + " beat others in tie ");
					return best;
				} else {
					return mostHooper(set);
				}
			}
		}

	}

	private String mostHooper(List<Player> set) {
		int maxHoops = 0;
		for (Player p : set) {
			int hoops = p.getHoops();
			if (hoops > maxHoops) {
				maxHoops = hoops;
			}
		}
		String best = null;
		for (Player p : set) {
			if (p.getHoops() == maxHoops) {
				if (best == null) {
					best = p.getName();
				} else {
					System.out.println(", draw");
					return null;
				}
			}
		}
		System.out.println(", " + best + " got most hoops");
		return best;
	}

	public void addPlayer(String name) throws SwissException {
		addPlayer(name, null);
	}

	public void makeGamesChoices(List<PersonScore> round) {
		int numPrimarys = numLawns;
		int numSecondarys = numLawns;
		List<Game> games = new ArrayList<>();
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
				games.add(new Game(p1.getName(), p2.getName(), ngame++));
			}
		}
		for (Game game : games) {
			Player p1 = players.get(game.getName1());
			Player p2 = players.get(game.getName2());
			if ((p1.getColours() == Colours.PRIMARY || p2.getColours() == Colours.PRIMARY)
					&& (p1.getColours() != Colours.SECONDARY || p2.getColours() != Colours.SECONDARY)) {
				game.setColours(Colours.PRIMARY);
				p1.incPrimarys();
				p2.incPrimarys();
				numPrimarys--;
			} else if ((p1.getColours() == Colours.SECONDARY || p2.getColours() == Colours.SECONDARY)
					&& (p1.getColours() != Colours.PRIMARY || p2.getColours() != Colours.PRIMARY)) {
				game.setColours(Colours.SECONDARY);
				p1.incSecondarys();
				p2.incSecondarys();
				numSecondarys--;
			}
		}
		for (Game game : games) {
			if (game.getColours() == null) {
				Player p1 = players.get(game.getName1());
				Player p2 = players.get(game.getName2());
				if (numPrimarys > 0 && numSecondarys > 0) {
					if (p1.getPrimaryExcess() + p2.getPrimaryExcess() > 0) {
						game.setColours(Colours.SECONDARY);
						p1.incSecondarys();
						p2.incSecondarys();
						numSecondarys--;
					} else {
						game.setColours(Colours.PRIMARY);
						p1.incPrimarys();
						p2.incPrimarys();
						numPrimarys--;
					}
				} else if (numPrimarys > 0) {
					game.setColours(Colours.PRIMARY);
					p1.incPrimarys();
					p2.incPrimarys();
					numPrimarys--;
				} else {
					game.setColours(Colours.SECONDARY);
					p1.incSecondarys();
					p2.incSecondarys();
					numSecondarys--;
				}
			}
		}
		Set<Integer> lawnPos = new HashSet<>();
		for (int i = 0; i < numLawns; i++) {
			lawnPos.add(2 * i);
			lawnPos.add(2 * i + 1);
		}
		for (Game game : games) {
			Player p1 = players.get(game.getName1());
			Player p2 = players.get(game.getName2());
			int count = 0;
			int best = -1;
			for (int lawn : lawnPos) {
				if ((game.getColours() == Colours.PRIMARY && lawn < numLawns)
						|| (game.getColours() == Colours.SECONDARY && lawn >= numLawns)) {
					int lawnsCount = p1.getLawnCount(lawn) + p2.getLawnCount(lawn);
					if (best == -1 || lawnsCount < count)
						best = lawn;
					count = lawnsCount;
				}
			}
			p1.incLawnCount(best % numLawns);
			p2.incLawnCount(best % numLawns);
			lawnPos.remove(best);
			game.setLawn(best % numLawns);
		}
		for (int i = 0; i < numLawns; i++) {
			int numStarts = -1;
			int found = 0;
			Game first = null;
			for (Game game : games) {
				if (game.getLawn() == i) {
					found++;
					Player p1 = players.get(game.getName1());
					Player p2 = players.get(game.getName2());
					if (found == 1) {
						numStarts = p1.getStartCount() + p2.getStartCount();
						first = game;
					} else {
						if (numStarts >= p1.getStartCount() + p2.getStartCount()) {
							game.setStart();
							p1.incStartCount();
							p2.incStartCount();
						} else {
							first.setStart();
							players.get(first.getName1()).incStartCount();
							players.get(first.getName2()).incStartCount();
						}
					}
				}
			}
			if (found == 1) {
				first.setStart();
				players.get(first.getName1()).incStartCount();
				players.get(first.getName2()).incStartCount();
			}
		}
		for (Game game : games) {
			System.out.println("Game " + game.getSquare() + ": " + game.getName1() + " vs " + game.getName2() + " "
					+ game.getColours() + " on lawn " + (game.getLawn() + 1) + " go "
					+ (game.getStart() ? "first" : "second"));

		}
		if (bye != null) {
			System.out.println(bye + " gets a bye");
		}

	}

}
