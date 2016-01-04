package uk.org.harwellcroquet.swiss.logic;

public class Game {

	private String name1;
	private String name2;
	private int square;

	public Game(String name1, String name2, int square) {
		this.name1 = name1;
		this.name2 = name2;
		this.square = square;
	}

	@Override
	public String toString() {
		return name1 + " vs " + name2 + " (" + square +")";
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

}
