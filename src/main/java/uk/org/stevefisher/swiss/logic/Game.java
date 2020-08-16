package uk.org.stevefisher.swiss.logic;

import uk.org.stevefisher.swiss.logic.BasicSwiss.Colours;

public class Game {

	private String name1;
	private String name2;
	private int square;
	private Colours colours;
	private int lawn;
	private boolean start;

	public Game(String name1, String name2, int square) {
		this.name1 = name1;
		this.name2 = name2;
		this.square = square;
	}

	@Override
	public String toString() {
		return name1 + " vs " + name2 + " (" + square + ")";
	}

	public String getName1() {
		return name1;
	}

	public String getName2() {
		return name2;
	}

	public int getSquare() {
		return square;
	}

	public void setColours(Colours colours) {
		this.colours = colours;
	}

	public Colours getColours() {
		return colours;
	}

	public void setLawn(int lawn) {
		this.lawn = lawn;
	}

	public int getLawn() {
		return lawn;
	}

	public void setStart() {
		start = true;
	}

	public boolean getStart() {
		return start;
	}

}
