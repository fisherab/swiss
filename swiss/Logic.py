from math import comb
from enum import Enum
from itertools import combinations
import random
import logging
logger = logging.getLogger(__name__)

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
        return "Game " + str(self.name1) + " vs " + str(self.name2) + ("" if self.square is None else " sq:" + str(self.square))

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
        return "Player " + self.name + " " + str(self.games)

    def getPrimaryExcess(self):
        return self.primarys - self.secondarys;

    def getLawns(self, lawn):
        return self.lawns[lawn] if lawn in self.lawns else 0

    def incLawns(self, lawn):
        if lawn in self.lawns: self.lawns[lawn] +=  1
        else: self.lawns[lawn] = 1

class CombResult:

     def __init__(self, numGood,  bestGames,  bestSumSquares):
        self.numGood = numGood
        self.bestGames = bestGames
        self.bestSumSquares = bestSumSquares

     def __str__(self):
        ret = "numGood:" + str(self.numGood) + " bestGames:"
        if self.bestGames != None:
            for game in self.bestGames: ret += " " + str(game)
        if self.bestSumSquares != None: ret += " bestSumSquares:" + str(self.bestSumSquares)
        return ret

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
        if col != None: logger.debug(name + " will get " + col.name)
        self.players[name] = Player(name, col)

    def start(self):
        """
        Create first round (numbered 0) and add it to rounds list.
        """
        if len(self.players) % 2 == 1: self.players["Bye"] = Player("Bye", None)
        round = []
        for name in self.players: round.append([name,0])
        random.shuffle(round)
        self.rounds.append(round)

    def startWithNames(self, names):
        """
        Create first round (numbered 0) using names ordered as specified for
        recovering from journal
     
        :param names List of names to set for the first round
        """
        round = []
        for name in names: round.append([name, 0])
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
            logger.info("There are " + str(len(games)) + " games with " + str(combis) + " combinations."
                    + (" Truncate" if combis>self.maxCombis else ""))
            for game in games: logger.debug(game)

            # Sort the games by fairness i.e. how close in ranking
            games.sort(key=lambda game: game.square)
           
            # Compute bestGames via recursive call
            combResult = Tournament.bestCombinations(games, gamesPerRound, set(), 0, set(), enoughGood if combis > self.maxCombis else None)

            round.clear()
            if combResult.bestGames == None:
                logger.info("No valid combination of games found")
            else:
                res = "Best is"
                for g in combResult.bestGames: res += " " + str(g)
                logger.info(res)
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
            logger.debug(str(game) + " "
                    + game.colours.name + " on lawn " + str(game.lawn + 1) + " go "
                    + ("first" if game.start else "second"))
        
        if bye != None:
            logger.debug(bye + " gets a bye")
        
    @staticmethod
    def bestCombinations(games, gamesPerRound, inResults, inSum, inNames, enoughGood):
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
        logger.debug("Selecting from " + str(len(games)) + " done " + str(len(inResults)) + " inNames " + str(inNames) + " inSum " + str(inSum))
        bestSumSquares = None
        bestGames = None
        badGames = set()
        numGood = 0
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
                        
                    combresult = Tournament.bestCombinations(gamesToConsider, gamesPerRound, results, sumSq, names, enoughGood)
                    if combresult.bestSumSquares != None and (bestSumSquares == None or combresult.bestSumSquares < bestSumSquares):
                        bestSumSquares = combresult.bestSumSquares
                        bestGames = combresult.bestGames
                    
                    numGood += combresult.numGood;
                    if enoughGood != None and numGood >= enoughGood:
                        logger.debug("Enough results")
                        break
            else:
                badGames.add(game);
                logger.debug("Game rejected " + str(game))
            
        combresult = CombResult(numGood, bestGames, bestSumSquares)
        logger.debug("Returning combresult" + str(combresult))
        return combresult;
    
    def getFinalRanking(self):
        r = {}
        for name, player in self.players.items():
            if name != "Bye":
                numGames = player.games
                if numGames not in r: r[numGames] = set()
                r[numGames].add(player)
    
        result = {}
        npos = 1
        for key in reversed(sorted(r.keys())):     
            players = list(r[key])

            while len(players) > 0:
                if len(players) == 1:
                    result[players[0].name] = npos
                    npos += 1
                    players.clear()
                else:
                    logger.info("Need winner from " + str([p.name for p in players]));
                    best = self.getBest(players)
                    if best != None:
                        result[best] = npos
                        npos += 1
                        for p in players:
                            if p.name == best:
                                bestPlayer = p
                                break
                        players.remove(bestPlayer)
                    else: # best was None
                        for p in players: result[p.name] = npos
                        npos += len(players)
                        players.clear()
        return result;

    def getBest(self, players):
        """Find the best of two or more players"""
        names = {}
        for p in players: names[p.name] = 0
   
        wins = 0
        for round in self.rounds:
            ngames = len(round) // 2
            for i in range(ngames):
                p1r = round[2 * i]
                p2r = round[2 * i + 1]
                if p1r[0] in names and p2r[0] in names:
                    if p1r[1] > p2r[1]: names[p1r[0]] +=1
                    else: names[p2r[0]] +=1
                    wins += 1
  
        if len(players) == 2:
            n1 = list(players)[0].name
            n2 = list(players)[1].name
       
            if wins == 1: 
                if names[n1] > names[n2]:
                    logger.info(n1 + " beat " + n2 + " in a round")
                    return n1
                else:
                    logger.info(n2 + " beat " + n1 + " in a round")
                    return n2
            else: return Tournament.mostHooper(players);

        else: # Three or more in tie
            print(", games won in tie " + names)
            if wins == len(players) * (len(players) - 1) // 2:
                print(", all played")
                max = 0
##                for (Entry<String, Integer> name : names.entrySet()) {
##                    if (name.getValue() > max) {
##                        max = name.getValue();
##                    }
##                }
##                String best = null;
##                for (Entry<String, Integer> name : names.entrySet()) {
##                    if (name.getValue() == max) {
##                        if (best == null) {
##                            best = name.getKey();
##                        } else {
##                            return mostHooper(set);
##                        }
##                    }
##                }
                print(", " + best + " beat others in tie ")
                return best
            else: 
                print(", not all played")
##                int needed = set.size() - 1;
##                String best = null;
##                for (Entry<String, Integer> name : names.entrySet()) {
##                    if (name.getValue() == needed) {
##                        if (best == null) {
##                            best = name.getKey();
##                        } else {
##                            return mostHooper(set);
##                        }
##                    }
##                }
##                if (best != null) {
##                    System.out.println(", " + best + " beat others in tie ");
##                    return best;
##                } else {
##                    return mostHooper(set);
##                }
 

    @staticmethod
    def mostHooper(players):
        maxHoops = 0;
        for p in players:
            hoops = p.hoops
            if hoops > maxHoops: maxHoops = hoops
        best = None
        for p in players:
            if p.hoops == maxHoops:
                if best == None:
                    best = p.name
                else: 
                    logger.info("draw");
                    return None
        logger.info(best + " got most hoops")
        return best

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
