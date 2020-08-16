package uk.org.stevefisher.swiss.logic;

public class PersonScore {

	private String name;
	private int score;

	public PersonScore(String name) {
		this.name = name;
	}

	@Override
	public String toString() {
		return name + ": " + score;
	}

	public String getName() {
		return name;
	}

	public void setScore(int score) {
		this.score = score;
	}

	public int getScore() {
		return score;
	}

}
