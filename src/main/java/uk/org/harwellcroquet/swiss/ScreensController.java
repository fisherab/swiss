package uk.org.harwellcroquet.swiss;

import java.util.HashMap;
import java.util.Map;

import javafx.animation.KeyFrame;
import javafx.animation.KeyValue;
import javafx.animation.Timeline;
import javafx.beans.property.DoubleProperty;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.fxml.FXMLLoader;
import javafx.geometry.Rectangle2D;
import javafx.scene.Node;
import javafx.scene.Parent;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.StackPane;
import javafx.stage.Screen;
import javafx.util.Duration;

public class ScreensController extends StackPane {

	private Map<String, Node> screens = new HashMap<>();

	public void addScreen(String name, Node screen) {
		screens.put(name, screen);
	}

	public Node getScreen(String name) {
		return screens.get(name);
	}

	public boolean loadScreen(String name, String fxml) {
		try {
			FXMLLoader myLoader = new FXMLLoader(getClass().getResource(fxml));
			Parent loadScreen = (Parent) myLoader.load();
			ControlledScreen myScreenControler = ((ControlledScreen) myLoader.getController());
			myScreenControler.setScreenParent(this);
			addScreen(name, loadScreen);
			return true;
		} catch (Exception e) {
			e.printStackTrace();
			System.out.println(e.getClass().getSimpleName() + " " + e.getMessage());
			return false;
		}
	}

	public boolean setScreen(final String name) {
		if (screens.get(name) != null) {
			final DoubleProperty opacity = opacityProperty();

			if (!getChildren().isEmpty()) {
				Timeline fade = new Timeline(new KeyFrame(Duration.ZERO, new KeyValue(opacity, 1.0)),
						new KeyFrame(new Duration(1000), new EventHandler<ActionEvent>() {
							@Override
							public void handle(ActionEvent t) {
								getChildren().remove(0);
								getChildren().add(0, screens.get(name));

								Timeline fadeIn = new Timeline(new KeyFrame(Duration.ZERO, new KeyValue(opacity, 0.0)),
										new KeyFrame(new Duration(800), new KeyValue(opacity, 1.0)));
								fadeIn.play();
							}
						}, new KeyValue(opacity, 0.0)));
				fade.play();

			} else {
				setOpacity(0.0);
				getChildren().add(screens.get(name));
				Timeline fadeIn = new Timeline(new KeyFrame(Duration.ZERO, new KeyValue(opacity, 0.0)),
						new KeyFrame(new Duration(2500), new KeyValue(opacity, 1.0)));
				fadeIn.play();
			}

			BorderPane bp = (BorderPane) screens.get(name);

			Rectangle2D visualBounds = Screen.getPrimary().getVisualBounds();
			bp.setPrefSize(visualBounds.getWidth() * .95, visualBounds.getHeight() * 0.95);

			return true;
		} else {
			System.out.println("Screen mnemonic '" + name + "' is not recognised");
			return false;
		}
	}

	public boolean unloadScreen(String name) {
		if (screens.remove(name) == null) {
			System.out.println("Screen didn't exist");
			return false;
		} else {
			return true;
		}
	}

}
