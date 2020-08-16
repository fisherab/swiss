package uk.org.stevefisher.swiss.logic;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import uk.org.stevefisher.swiss.logic.BasicSwiss.Colours;

public class Player {

	private int games;
	private Set<String> played = new HashSet<>();
	private String name;
	private int hoops;
	private Colours col;
	private int primarys;
	private int secondarys;
	private Map<Integer, Integer> lawns = new HashMap<>();
	private int startCount;

	Player(String name, Colours col) {
		this.name = name;
		this.col = col;
	}

	public void incrementGames() {
		games++;
	}

	public void addPlayed(String name) {
		played.add(name);
	}

	public int getGames() {
		return games;
	}

	public boolean hasNotPlayed(String name) {
		return !played.contains(name);
	}

	public String getName() {
		return name;
	}

	@Override
	public String toString() {
		return name + "(" + games + ":" + hoops + ")";
	}

	public void addHoops(int inc) {
		hoops += inc;

	}

	public int getHoops() {
		return hoops;
	}

	public Colours getColours() {
		return col;
	}

	public void incPrimarys() {
		primarys++;
	}

	public void incSecondarys() {
		secondarys++;
	}

	public int getPrimaryExcess() {
		return primarys - secondarys;
	}

	public int getLawnCount(int lawn) {
		Integer count = lawns.get(lawn);
		return (count == null) ? 0 : count;
	}

	public void incLawnCount(int lawn) {
		Integer count = lawns.get(lawn);
		if (count == null) {
			count = 1;
		} else {
			count++;
		}
		lawns.put(lawn, count);

	}

	public int getStartCount() {
		return startCount;
	}
	
	public void incStartCount() {
		startCount++;
	}

}
