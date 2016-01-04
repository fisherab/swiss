package uk.org.harwellcroquet.swiss.logic;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

public class BasicSwiss {

	enum Status {
		STARTED, SETTING_UP
	};

	Status status = Status.SETTING_UP;

	private Map<String, Player> players = new HashMap<>();

	private List<List<PersonScore>> rounds = new ArrayList<>();

	private int byeScore;

	private ArrayList<String> ranking;

	private Game[] bestGames;

	private int bestSumSquares;

	private BigInteger maxCombis;

	private int enoughGood;

	private BigInteger combis;

	private int numGood;

	public BasicSwiss(int byeScore, int maxCombis, int enoughGood) {
		this.byeScore = byeScore;
		this.maxCombis = BigInteger.valueOf(maxCombis);
		this.enoughGood = enoughGood;
	}

	public void addPlayer(String name) throws SwissException {
		if (players.containsKey(name)) {
			throw new SwissException("Player " + name + " already present");
		} else if (name.equals("Bye")) {
			throw new SwissException("The player name 'Bye' is reserved");
		}
		players.put(name, new Player(name));
	}

	/** Create first round (numbered 0) and add it to rounds list */
	public void start() throws SwissException {
		if (status == Status.SETTING_UP) {
			status = Status.STARTED;
			if (players.size() % 2 == 1) {
				players.put("Bye", new Player("Bye"));
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
			players.get(p2.getName()).addPlayed(p1.getName());
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
			Set<Game> games = new HashSet<>();
			for (String name1 : players.keySet()) {
				for (String name2 : players.keySet()) {
					if (name1.compareTo(name2) < 0 && players.get(name1).hasNotPlayed(name2)) {
						int i = ranking.indexOf(name1) - ranking.indexOf(name2) - 1;
						games.add(new Game(name1, name2, i * i));
					}
				}
			}

			int ngames = players.size() / 2;
			combis = binomial(games.size(), ngames);
			System.out.print("There are " + games.size() + " with " + combis + " combinations. "
					+ (combis.compareTo(maxCombis) > 0 ? "Truncate. " : ""));
			numGood = 0;

			Game[] gameList = games.toArray(new Game[0]);
			Arrays.sort(gameList, new Comparator<Game>() {
				@Override
				public int compare(Game g1, Game g2) {
					return g1.getSquare() - g2.getSquare();
				}
			});

			bestGames = null;
			bestSumSquares = 0;

			combinations2(gameList, ngames, 0, new Game[ngames]);

			System.out.println("Best is " + Arrays.toString(bestGames));
			round.clear();
			for (Game game : bestGames) {
				round.add(new PersonScore(game.getName1()));
				round.add(new PersonScore(game.getName2()));
			}
		}

	}

	static BigInteger binomial(final int N, final int K) {
		BigInteger ret = BigInteger.ONE;
		for (int k = 0; k < K; k++) {
			ret = ret.multiply(BigInteger.valueOf(N - k)).divide(BigInteger.valueOf(k + 1));
		}
		return ret;
	}

	boolean combinations2(Game[] arr, int len, int startPosition, Game[] result) {
		if (len == 0) {
			Set<String> names = new HashSet<>();
			boolean good = true;
			for (Game game : result) {
				if (!names.add(game.getName1()) || !names.add(game.getName2())) {
					good = false;
					break;
				}
			}
			if (good) {
				int sum = 0;
				for (Game game : result) {
					sum = sum + game.getSquare();
				}
				numGood++;
				if (bestGames == null || sum < bestSumSquares) {
					bestGames = result.clone();
					bestSumSquares = sum;
				}
				if (combis.compareTo(maxCombis) > 0) {
					if (numGood > enoughGood) {
						return false;
					}
				}
			}
			return true;
		}
		for (int i = startPosition; i <= arr.length - len; i++) {
			result[result.length - len] = arr[i];
			int sum = 0;

			Set<String> names = new HashSet<>();
			boolean good = true;

			for (int j = 0; j < result.length - len; j++) {
				if (!names.add(result[j].getName1()) || !names.add(result[j].getName2())) {
					good = false;
					break;
				}
				sum += result[j].getSquare();
				if (bestGames != null && sum >= bestSumSquares) {
					good = false;
					break;
				}
			}

			if (good) {
				if (!combinations2(arr, len - 1, i + 1, result)) {
					return false;
				}
			}
		}
		return true;
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

	public Map<String, Integer> getFinalRanking() {
		computeRanking();
		System.out.print("Ranking after last round (" + rounds.size() + ") ");
		for (String name : ranking) {
			System.out.print(name + ": " + players.get(name).getGames() + "  ");
		}
		System.out.println();

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
			if (wins == 1) {
				String n1 = set.get(0).getName();
				String n2 = set.get(1).getName();
				if (names.get(n1) > names.get(n2)) {
					System.out.println(", " + n1 + " beat " + n2 + " in a round");
					return n1;
				} else {
					System.out.println(", " + n2 + " beat " + n1 + " in a round");
					return n2;
				}
			} else {
				System.out.println(", draw");
				return null;
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
							System.out.println(", draw");
							return null;
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
							System.out.println(", draw");
							return null;
						}
					}
				}
				if (best != null) {
					System.out.println(", " + best + " beat others in tie ");
					return best;
				} else {
					System.out.println(", draw");
					return null;
				}
			}
		}

	}

}
