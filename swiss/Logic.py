from math import comb
from enum import Enum
import random

class Colours(Enum):
    PRIMARY = 1
    SECONDARY = 2

class Game(object):

    def __init__(self, name1, name2, square = None):
        self.name1 = name1
        self.name2 = name2
        self.square = square
        self.colours = None
        self.start = False

    def __str__(self):
        return "Game " + str(self.name1) + " vs " + str(self.name2) + ("" if self.square is None else " : " + str(self.square))

class Player(object):
    
    def __init__(self, name, col):
        self.name = name
        self.colours = col
        self.games = 0
        self.played = set()
        self.hoops = 0
        self.primarys = 0
        self.secondarys = 0
        self.lawns = {}
        self.startCount = 0

    def __str__(self):
        return "Player " + self.name + str(self.games)

    def getPrimaryExcess(self):
        return self.primarys - self.secondarys;

    def getLawns(self, lawn):
        return self.lawns[lawn] if lawn in self.lawns else 0

    def incLawns(self, lawn):
        if lawn in self.lawns: self.lawns[lawn] +=  1
        else: self.lawns[lawn] = 1

class CombResult:

     def __init__(self, more,  numGood,  bestGames,  bestSumSquares):
        self.more = more
        self.numGood = numGood
        self.bestGames = bestGames
        self.bestSumSquares = bestSumSquares

     def __str__(self):
        return "More:" + str(self.more) + " numGood:" + str(self.numGood) + " bestGames:" + str(self.bestGames) + " bestSumSquares:" + str(self.bestSumSquares)

class Tournament(object):

    def __init__(self, byeScore, maxCombis, enoughGood, numLawns):
        self.byeScore = byeScore
        self.maxCombis = maxCombis
        self.enoughGood = enoughGood
        self.numLawns = numLawns
        self.players = {}
        self.rounds = []

    def addPlayer(self, name, col=None, allowBye=False):
        if name in self.players: raise Exception("Player " + name + " already present")
        if name == "Bye" and not allowBye: raise Exception("The player name 'Bye' is reserved")
        if col != None: print(name + " will get " + col.name)
        self.players[name] = Player(name, col)

    def start(self):
        ### Create first round (numbered 0) and add it to rounds list. ###
        if len(self.players) % 2 == 1: self.players["Bye"] = Player("Bye", None)
        round = []
        for name in self.players: round.append([name,0])
        random.shuffle(round)
        self.rounds.append(round)

    def getKORounds(self):
        maxPeople = 2
        koRounds = 1
        while maxPeople < len(self.players):
            maxPeople = maxPeople * 2
            koRounds += 1
        return koRounds

    def getMaxRounds(self):
        return len(self.players) - 1

    def getRecRounds(self):
        return min(self.getKORounds() + 2, self.getMaxRounds())

    def computeRanking(self):
        roundNum = len(self.rounds) - 1
        maxScore = roundNum + 1
        round = self.rounds[roundNum]
        self.ranking = []
        ngames = len(round) // 2
        for i in range(ngames):
            p1 = round[2 * i]
            p2 = round[2 * i + 1]

            p1Name = p1[0]
            p2Name = p2[0]
            if p1[1] > p2[1]:
                self.players[p1Name].games += 1
            else:
                self.players[p2Name].games += 1
            
            self.players[p1Name].played.add(p2Name)
            self.players[p1Name].hoops += p1[1]
            self.players[p2Name].played.add(p1Name)
            self.players[p2Name].hoops += p2[1]
        
        for i in range(maxScore,-1,-1):
            for ps in round:
                pName = ps[0]
                if self.players[pName].games == i: self.ranking.append(pName)
  
    def prepareRound(self):
        ### Create a new round and add it to the rounds list. ###
        tempRanking = self.ranking.copy()
        round = []
        self.rounds.append(round)
        lowNames = []

        p2 = None
        while True:
            # Find the topmost person
            p1 = None
            for i in range(len(tempRanking)):
                name = tempRanking[i]
                if name != None:
                    p1 = self.players[name]
                    break
            if p1 == None: break
            tempRanking[i] = None

            # and the next person he has not played
            p2 = None;
            for i in range (i+1, len(tempRanking)):
                name = tempRanking[i]
                if name != None and not name in p1.played:
                    p2 = self.players[name]
                    break
            if p2 == None: break
            tempRanking[i] = None
            
            round.append([p1.name,0])
            round.append([p2.name,0])

            # Find the lowest person
            p1 = None;
            for i in range(len(tempRanking) - 1, 0, -1):
                name = tempRanking[i]
                if name != None:
                    p1 = self.players[name]
                    break
            if p1 == None: break
            tempRanking[i] = None

            # and the next person he has not played
            p2 = None
            for i in range (i-1, 0, -1):
                name = tempRanking[i]
                if name != None and not name in p1.played:
                    p2 = self.players[name]
                    break
            if p2 == None: break
            tempRanking[i] = None

            lowNames.append(p1.name)
            lowNames.append(p2.name)

        lowNames.reverse()
        for name in lowNames: round.append([name, 0]);


        if p2 == None:
            print("CCCCCCCCCCCCCCCCCCCC")
            # There were clashes so compute set of all possible (i.e. non-played) games.
            games = []
            for name1 in self.players:
                for name2 in self.players:
                    if name1 < name2 and not name1 in self.players[name2].played:
                        i = self.ranking.index(name1) - self.ranking.index(name2)
                        games.append(Game(name1, name2, i * i))

            # Need to select a set of games that allows each person to play in one game.
            # There may be more than one possible set from the combinations of games. So
            # choose a good one. To be good the players should be close to each other in the 
            # ranking. If there are a lot of combinations don't check all of them but stop
            # when the result is good enough. 
            gamesPerRound = len(self.players) // 2;
            combis = comb(len(games), gamesPerRound);
            print("There are " + str(len(games)) + " games with " + str(combis) + " combinations."
                    + (" Truncate" if combis>self.maxCombis else ""));

            # Sort the games by fairness i.e. how close in ranking
            games.sort(key=lambda game: game.square)
            for g in games: print(g)
           
            # Compute bestGames via recursive call
            combResult = Tournament.combinationsTwo(games, gamesPerRound, set(), 0, set(), enoughGood if combis > self.maxCombis else None)

            # If this fails then ...
            if (combResult.bestGames == None): combResult = combinationsThree(games, gamesPerRound, enoughGood if combis > self.maxCombis else None)
            print("Best is " + str(combResult.bestGames))

            round.clear();

            if combResult.bestGames == None: raise Exception("No valid combination of games found")
            for game in combResult.bestGames:
                round.append([game.name1, 0])
                round.append([game.name2, 0])

    def setByeScores(self):
        round = self.rounds[len(self.rounds) - 1]
        ngames = len(round) // 2;
        for i in range (ngames):
            p1 = round[2 * i]
            p2 = round[2 * i + 1]
            if p1[0] == "Bye": p2[1] = self.byeScore
            if p2[0] == "Bye": p1[1] = self.byeScore
   
    def makeGamesChoices(self, round):
        numPrimarys = self.numLawns
        numSecondarys = self.numLawns
        games = []
        bye = None
        for i in range(len(round) // 2):
            p1 = round[2 * i]
            p2 = round[2 * i + 1]
            if p1[0] =="Bye": bye = p2[0]
            elif p2[0] =="Bye": bye = p1[0]
            else: games.append(Game(p1[0], p2[0]))
     
            
        for game in games:
            p1 = self.players[game.name1]
            p2 = self.players[game.name2]
            if ((p1.colours == Colours.PRIMARY or p2.colours == Colours.PRIMARY)
                    and (p1.colours != Colours.SECONDARY or p2.colours != Colours.SECONDARY)):
                game.colours = Colours.PRIMARY
                p1.primarys += 1
                p2.primarys += 1
                numPrimarys -= 1
            elif ((p1.colours == Colours.SECONDARY or p2.colours == Colours.SECONDARY)
                    and (p1.colours != Colours.PRIMARY or p2.colours != Colours.PRIMARY)):
                game.colours = Colours.SECONDARY
                p1.secondarys += 1
                p2.secondarys += 1
                numSecondarys -= 1
        
        for game in games:
            if game.colours == None:
                p1 = self.players[game.name1]
                p2 = self.players[game.name2]
                if numPrimarys > 0 and numSecondarys > 0:
                    if p1.getPrimaryExcess() + p2.getPrimaryExcess() > 0:
                        game.colours = Colours.SECONDARY
                        p1.secondarys += 1
                        p2.secondarys += 1
                        numSecondarys -= 1
                    else:
                        game.colours = Colours.PRIMARY
                        p1.primarys += 1
                        p2.primarys += 1
                        numPrimarys -= 1
                    
                elif numPrimarys > 0:
                    game.colours = Colours.PRIMARY
                    p1.primarys += 1
                    p2.primarys += 1
                    numPrimarys -= 1
                else:
                    game.colours = Colours.SECONDARY
                    p1.secondarys += 1
                    p2.secondarys += 1
                    numSecondarys -= 1
     
        lawnPos = set()
        for i in range(self.numLawns):
            lawnPos.add(2 * i)
            lawnPos.add(2 * i + 1)
        
        for game in games:
            p1 = self.players[game.name1]
            p2 = self.players[game.name2]
            count = 0
            best = -1
            for lawn in lawnPos:
                if ((game.colours == Colours.PRIMARY and lawn < self.numLawns)
                        or (game.colours == Colours.SECONDARY and lawn >= self.numLawns)):
                    lawnsCount = p1.getLawns(lawn) + p2.getLawns(lawn)
                    if best == -1 or lawnsCount < count: best = lawn
                    count = lawnsCount
            
            p1.incLawns(best % self.numLawns)
            p2.incLawns(best % self.numLawns)
            lawnPos.remove(best)
            game.lawn = best % self.numLawns
        
        for i in range(self.numLawns):
            numStarts = -1
            found = 0
            first = None
            for game in games:
                if game.lawn == i:
                    found += 1
                    p1 = self.players[game.name1]
                    p2 = self.players[game.name2]
                    if found == 1:
                        numStarts = p1.startCount + p2.startCount
                        first = game
                    else:
                        if numStarts >= p1.startCount + p2.startCount:
                            game.start = True
                            p1.startCount += 1
                            p2.startCount += 1
                        else:
                            first.start = True
                            self.players[first.name1].startCount += 1
                            self.players[first.name2].startCount += 1
  
            if found == 1:
                first.start = True
                self.players[first.name1].startCount += 1
                self.players[first.name2].startCount += 1
            
        for game in games:
            print(str(game) + " "
                    + game.colours.name + " on lawn " + str(game.lawn + 1) + " go "
                    + ("first" if game.start else "second"))
        
        if bye != None:
            print(bye + " gets a bye")
        

    




##
##	enum Status {
##		STARTED, SETTING_UP
##	};
##
##	private static final Logger logger = LogManager.getLogger(BasicSwiss.class);;
##
##	
##	static CombResult combinationsThree(List<Game> games, int gamesPerRound, Integer enoughGood) {
##		Iterator<int[]> iterator = CombinatoricsUtils.combinationsIterator(games.size(), gamesPerRound);
##		long bestSumSquares = Long.MAX_VALUE;
##		boolean more = true;
##		Set<Game> bestGames = null;
##		int numGood = 0;
##		while (iterator.hasNext()) {
##			int sum = 0;
##			Set<String> players = new HashSet<String>();
##			int[] gs = iterator.next();
##			for (int g : gs) {
##				Game game = games.get(g);
##				if (!players.add(game.getName1()) || !players.add(game.getName2())) {
##					break;
##				}
##				sum += game.getSquare();
##			}
##			if (players.size() == gamesPerRound * 2) {
##				numGood++;
##				if (sum < bestSumSquares) {
##					bestSumSquares = sum;
##					bestGames = new HashSet<Game>();
##					for (int g : gs) {
##						bestGames.add(games.get(g));
##					}
##				}
##				if (enoughGood != null && numGood >= enoughGood) {
##					logger.debug("Enough results");
##					more = false;
##					break;
##				}
##			}
##		}
##		return new CombResult(more, numGood, bestGames, bestSumSquares);
##	}
##


    @staticmethod
    def combinationsTwo(games, gamesPerRound, inResults, inSum, inNames, enoughGood):
        """
        Recursive function to return best set of games
        
        :param games:         Array of possible Games
        :param gamesPerRound: Number of games to have a complete valid round
        :param inResults:     set of games in the chain so far
        :param inSum:         Count of sum of squares of games in the chain
        :param inNames:       set of player names already allocated in the chain
        :param enoughGood:    if not null the calculation should only consider enoughGood valid combinations
        :return: a CombResult
        """        
        print("Selecting from", len(games), "games inResults", inResults, "inNames", inNames, "inSum", inSum)
        bestSumSquares = None
        bestGames = None
        badGames = set()
        numGood = 0
        more = True
        offset = 0
        for game in games:
            offset += 1
            names = inNames.copy()
            if game.name1 not in names and game.name2 not in names:
                names.add(game.name1)
                names.add(game.name2)
                results = inResults.copy()
                results.add(game);
                sumSq = inSum + game.square
                if len(results) == gamesPerRound:
                    numGood += 1
                    if bestSumSquares == None or sumSq < bestSumSquares:
                        bestSumSquares = sumSq
                        bestGames = results
                else:
                    gamesToConsider = []
                    for g in games[offset:]:
                        if g not in badGames: gamesToConsider.append(g);
                        
                    combresult = Tournament.combinationsTwo(gamesToConsider, gamesPerRound, results, sumSq, names, enoughGood)
                    if combresult.bestSumSquares != None and (bestSumSquares == None or combresult.bestSumSquares < bestSumSquares):
                        bestSumSquares = combresult.bestSumSquares
                        bestGames = combresult.bestGames
                    
                    numGood += combresult.numGood;
                    if enoughGood != None and numGood >= enoughGood:
                        print("Enough results")
                        more = false
                        break
            else:
                badGames.add(game);
                print("Game rejected {}", game);
            
        combresult = CombResult(more, numGood, bestGames, bestSumSquares);
        print("Returning combresult", combresult);
        return combresult;
    


##
##
##	/* Set will always have at least two members */
##	private String getBest(List<Player> set) {
##		Map<String, Integer> names = new HashMap<>();
##		for (Player p : set) {
##			names.put(p.getName(), 0);
##		}
##
##		int wins = 0;
##		for (List<PersonScore> round : rounds) {
##			int ngames = round.size() / 2;
##			for (int i = 0; i < ngames; i++) {
##				PersonScore p1r = round.get(2 * i);
##				PersonScore p2r = round.get(2 * i + 1);
##				if (names.containsKey(p1r.getName()) && names.containsKey(p2r.getName())) {
##					if (p1r.getScore() > p2r.getScore()) {
##						names.put(p1r.getName(), names.get(p1r.getName()) + 1);
##					} else {
##						names.put(p2r.getName(), names.get(p2r.getName()) + 1);
##					}
##					wins++;
##				}
##			}
##		}
##
##		if (set.size() == 2) {
##			String n1 = set.get(0).getName();
##			String n2 = set.get(1).getName();
##			if (wins == 1) {
##				if (names.get(n1) > names.get(n2)) {
##					System.out.println(", " + n1 + " beat " + n2 + " in a round");
##					return n1;
##				} else {
##					System.out.println(", " + n2 + " beat " + n1 + " in a round");
##					return n2;
##				}
##			} else {
##				return mostHooper(set);
##			}
##		} else {// Three or more in tie
##			System.out.print(", games won in tie " + names);
##			if (wins == set.size() * (set.size() - 1) / 2) {
##				System.out.print(", all played");
##				int max = 0;
##				for (Entry<String, Integer> name : names.entrySet()) {
##					if (name.getValue() > max) {
##						max = name.getValue();
##					}
##				}
##				String best = null;
##				for (Entry<String, Integer> name : names.entrySet()) {
##					if (name.getValue() == max) {
##						if (best == null) {
##							best = name.getKey();
##						} else {
##							return mostHooper(set);
##						}
##					}
##				}
##				System.out.println(", " + best + " beat others in tie ");
##				return best;
##			} else {
##				System.out.print(", not all played");
##				int needed = set.size() - 1;
##				String best = null;
##				for (Entry<String, Integer> name : names.entrySet()) {
##					if (name.getValue() == needed) {
##						if (best == null) {
##							best = name.getKey();
##						} else {
##							return mostHooper(set);
##						}
##					}
##				}
##				if (best != null) {
##					System.out.println(", " + best + " beat others in tie ");
##					return best;
##				} else {
##					return mostHooper(set);
##				}
##			}
##		}
##
##	}
##
##	public Map<String, Integer> getFinalRanking() {
##		Map<Integer, Set<Player>> r = new HashMap<>();
##
##		for (Player p : players.values()) {
##			if (!p.getName().equals("Bye")) {
##				int n = p.getGames();
##				Set<Player> set = r.get(n);
##				if (set == null) {
##					set = new HashSet<>();
##					r.put(n, set);
##				}
##				set.add(p);
##			}
##		}
##		List<Integer> keys = new ArrayList<>(r.keySet());
##		Collections.sort(keys);
##		Collections.reverse(keys);
##		Map<String, Integer> result = new HashMap<>();
##		int npos = 1;
##		for (Integer key : keys) {
##			// Set of players with same number of wins
##			List<Player> set = new ArrayList<>(r.get(key));
##			while (set.size() > 0) {
##				if (set.size() == 1) {
##					result.put(set.get(0).getName(), npos++);
##					set.clear();
##				} else {
##					System.out.print("Need winner from " + set);
##					String best = getBest(set);
##					if (best != null) {
##						Iterator<Player> iter = set.iterator();
##						while (iter.hasNext()) {
##							if (iter.next().getName().equals(best)) {
##								result.put(best, npos++);
##								iter.remove();
##								break;
##							}
##						}
##					} else {
##						for (Player p : set) {
##							result.put(p.getName(), npos);
##						}
##						npos += set.size();
##						set.clear();
##					}
##				}
##			}
##		}
##		return result;
##	}
##

##
##	public int getNumLawns() {
##		return numLawns;
##	}
##
##	public Map<String, Player> getPlayers() {
##		return players;
##	}
##
##
##
##
##	public List<PersonScore> getRound(int i) {
##		return rounds.get(i);
##	}
##

##
##	private String mostHooper(List<Player> set) {
##		int maxHoops = 0;
##		for (Player p : set) {
##			int hoops = p.getHoops();
##			if (hoops > maxHoops) {
##				maxHoops = hoops;
##			}
##		}
##		String best = null;
##		for (Player p : set) {
##			if (p.getHoops() == maxHoops) {
##				if (best == null) {
##					best = p.getName();
##				} else {
##					System.out.println(", draw");
##					return null;
##				}
##			}
##		}
##		System.out.println(", " + best + " got most hoops");
##		return best;
##	}
##

##


##
##	/**
##	 * Create first round (numbered 0) using names ordered as specified for
##	 * recovering from journal
##	 * 
##	 * @param names List of names to set for the first round
##	 */
##	public void start(List<String> names) {
##		List<PersonScore> round = new ArrayList<>();
##		for (String name : names) {
##			PersonScore ps = new PersonScore(name);
##			round.add(ps);
##		}
##		rounds.add(round);
##	}
##
##	public void writeLog(List<PersonScore> round, boolean firstRound) throws SwissException {
##		String logname = "journal.txt";
##		try (FileWriter f = new FileWriter(logname, !firstRound)) {
##			if (firstRound) {
##				for (int i = 0; i < round.size(); i++) {
##					if (i != 0) {
##						f.write(",");
##					}
##					String name = round.get(i).getName();
##					f.write(name);
##					Colours col = players.get(name).getColours();
##					if (col != null) {
##						f.write(" -" + col.name().charAt(0));
##					}
##				}
##				f.write("\n");
##			}
##			int ngames = round.size() / 2;
##			for (int i = 0; i < ngames; i++) {
##				PersonScore p1 = round.get(2 * i);
##				PersonScore p2 = round.get(2 * i + 1);
##				if (p1.getScore() > p2.getScore()) {
##					f.write(p1.getName() + ",beat," + p2.getName() + "," + p1.getScore() + "," + p2.getScore() + "\n");
##				} else if (p1.getScore() < p2.getScore()) {
##					f.write(p2.getName() + ",beat," + p1.getName() + "," + p2.getScore() + "," + p1.getScore() + "\n");
##				} else {
##					f.write(p1.getName() + ",draws with," + p2.getName() + "," + p1.getScore() + "," + p2.getScore()
##							+ "\n");
##				}
##			}
##		} catch (IOException e) {
##			throw new SwissException(e.getClass() + " " + e.getMessage());
##		}
##	}
##
##}
