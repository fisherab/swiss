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
import javafx.scene.layout.BorderPane;
import uk.org.harwellcroquet.swiss.logic.BasicSwiss;
import uk.org.harwellcroquet.swiss.logic.SwissException;

public class MainViewController implements Initializable, ControlledScreen {

	@FXML
	private Button go;

	@FXML
	private Button addPlayerButton;

	@FXML
	private TableView<PersonRecord> table;

	@FXML
	private TextField newPlayerName;

	@FXML
	private Label msg;

	@FXML
	private BorderPane bp;

	@FXML
	protected void addPlayer(ActionEvent event) {
		data.add(new PersonRecord(newPlayerName.getText()));
		newPlayerName.setText("");
	}

	private final ObservableList<PersonRecord> data = FXCollections.observableArrayList();

	private ScreensController screensController;

	@Override
	public void initialize(URL url, ResourceBundle rb) {

		table.setItems(data);

		go.setOnAction(new EventHandler<ActionEvent>() {
			@Override
			public void handle(ActionEvent event) {
				addPlayerButton.setDisable(true);
				BasicSwiss sw = new BasicSwiss(7, 1000000000, 100);
				try {
					for (PersonRecord p : data) {
						sw.addPlayer(p.getName());
					}
					sw.start();
				} catch (SwissException e) {
					msg.setText(e.getMessage());
					;
				}

				int koRounds = sw.getKORounds();
				int maxRounds = sw.getMaxRounds();
				int recRounds = Math.min(koRounds + 2, maxRounds);
				if (koRounds + 2 > maxRounds) {
					msg.setText("Not really enough players for a Swiss Tournament. Recommended rounds: " + recRounds);
				} else {
					msg.setText("Recommended rounds: " + recRounds);
				}
				screensController.setScreen("round");

			}
		});

	}

	@Override
	public void setScreenParent(ScreensController screenPage) {
		screensController = screenPage;
		
//		bp.prefWidthProperty().bind(screensController.widthProperty());
//		bp.prefHeightProperty().bind(screensController.heightProperty());

	}

}
