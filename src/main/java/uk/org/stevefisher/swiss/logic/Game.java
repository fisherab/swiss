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
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((name1 == null) ? 0 : name1.hashCode());
		result = prime * result + ((name2 == null) ? 0 : name2.hashCode());
		result = prime * result + square;
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		Game other = (Game) obj;
		if (name1 == null) {
			if (other.name1 != null)
				return false;
		} else if (!name1.equals(other.name1))
			return false;
		if (name2 == null) {
			if (other.name2 != null)
				return false;
		} else if (!name2.equals(other.name2))
			return false;
		if (square != other.square)
			return false;
		return true;
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
