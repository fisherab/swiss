package uk.org.harwellcroquet.swiss.logic;

import java.util.HashSet;
import java.util.Set;

public class Player {

	private int games;
	private Set<String> played = new HashSet<>();
	private String name;

	Player(String name) {
		this.name = name;
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
		return name + "(" + games + ")";
	}

}
