// Copyright 2010 owners of the AI Challenge project
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may not
// use this file except in compliance with the License. You may obtain a copy
// of the License at http://www.apache.org/licenses/LICENSE-2.0 . Unless
// required by applicable law or agreed to in writing, software distributed
// under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.
//
// Author: Jeff Cameron (jeff@jpcameron.com)
//
// This class is for testing the map rendering code. It loads one game state
// from a file and renders it.

import java.awt.image.*;
import java.io.*;
import javax.imageio.*;
import java.awt.*;
import java.util.ArrayList;

public class RenderMap {
    public static void main(String[] args) {
        try {
            if (args.length != 2) {
                System.err.println("USAGE: java RenderMap map.txt image.png");
				System.exit(1);
            }
            Game game = new Game(args[0], 100, 0, "log.txt");
            if (game.Init() == 0) {
                System.err.println("Error while loading map " + args[0]);
                System.exit(1);
            }

			ArrayList<Color> colors = new ArrayList<Color>();
			colors.add(new Color(255, 64, 64));
			colors.add(new Color(64, 255, 64));
			colors.add( new Color(64, 64, 255));
			colors.add(new Color(255, 255, 64));

			GraphicsConfiguration gc = GraphicsEnvironment
			.getLocalGraphicsEnvironment().getDefaultScreenDevice()
			.getDefaultConfiguration();

			BufferedImage bgImage = null;
			try {
			  bgImage = ImageIO.read(new File("img/space.jpg"));
			} catch (IOException Err) {
			  // Do nothing
			  System.err.println("Error!  Could not load bgimage!");
			}

			BufferedImage image = gc.createCompatibleImage(640, 480);

			Graphics2D _g = (Graphics2D)image.createGraphics();

			// Turn on AA/Speed
			_g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,
								RenderingHints.VALUE_ANTIALIAS_ON);
			_g.setRenderingHint(RenderingHints.KEY_RENDERING,
								RenderingHints.VALUE_RENDER_SPEED);
			_g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,
								RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

			game.Render(640, 480, 0.0, bgImage, colors, _g);

            File file = new File(args[1]);
            ImageIO.write(image, "png", file);
        } catch (Exception e) {
            System.err.println(e);
        }
    }
}
