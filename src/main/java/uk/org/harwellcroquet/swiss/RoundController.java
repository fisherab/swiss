package uk.org.harwellcroquet.swiss;

import java.net.URL;
import java.util.ResourceBundle;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TableView;
import javafx.scene.control.TextField;
import uk.org.harwellcroquet.swiss.logic.BasicSwiss;
import uk.org.harwellcroquet.swiss.logic.SwissException;

public class RoundController implements Initializable, ControlledScreen {

	@FXML
	private Button addPlayerButton;

	@FXML
	private TableView<PersonRecord> table;

	@FXML
	private TextField newPlayerName;

	@FXML
	private Label msg;

	@FXML
	protected void addPlayer(ActionEvent event) {
		screensController.setScreen("top");
	}

	private final ObservableList<PersonRecord> data = FXCollections.observableArrayList();

	private ScreensController screensController;

	@Override
	public void initialize(URL url, ResourceBundle rb) {
		table.setItems(data);

	}

	@Override
	public void setScreenParent(ScreensController screenPage) {
		screensController = screenPage;

	}

}
