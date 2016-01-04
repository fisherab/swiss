package uk.org.harwellcroquet.swiss;

import javafx.beans.property.SimpleIntegerProperty;
import javafx.beans.property.SimpleStringProperty;

public class PersonRecord {

	private final SimpleStringProperty name = new SimpleStringProperty("");;
	private final SimpleIntegerProperty wins = new SimpleIntegerProperty(0);

	public PersonRecord(String name) {
		setName(name);
	}

	public String getName() {
		return name.get();
	}

	public void setName(String name) {
		this.name.set(name);
	}

	public int getWins() {
		return wins.get();
	}

	public void setWins(int wins) {
		this.wins.set(wins);
	}

}
