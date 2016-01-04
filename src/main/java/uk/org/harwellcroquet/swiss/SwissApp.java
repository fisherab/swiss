package uk.org.harwellcroquet.swiss;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.geometry.Rectangle2D;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.stage.Screen;
import javafx.stage.Stage;

public class SwissApp extends Application {

	@Override
	public void start(Stage stage) throws Exception {
		Rectangle2D visualBounds = Screen.getPrimary().getVisualBounds();

		Parent root = FXMLLoader.load(getClass().getResource("MainView.fxml"));
		Scene scene = new Scene(root, visualBounds.getWidth()*.95, visualBounds.getHeight()*.95);
		scene.getStylesheets().add("uk/org/harwellcroquet/swiss/Swiss.css");
		stage.setScene(scene);
		stage.getIcons().add(new Image(SwissApp.class.getResourceAsStream("/icon.png")));
		stage.show();
	}

	public static void main(String[] args) {
		launch(args);
	}
}
