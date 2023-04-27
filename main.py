"""
Simple program to show moving a sprite with the keyboard.

This program uses the Arcade library found at http://arcade.academy

Artwork from https://kenney.nl/Assets

"""

import arcade
import math



SPRITE_SCALING = 0.6

# Set the size of the screen
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000

# Variables controlling the player
PLAYER_SPEED = 0.5
PLAYER_START_X = 3500
PLAYER_START_Y = 2150
PLAYER_TURN_SPEED = 0.6

# Skidmark variables
SKIDMARK_START_TIME = 0.3

TILE_SCALING = 1.6
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING


class Player(arcade.Sprite):
    """
    The player
    """

    def __init__(self, **kwargs):
        """
        Setup new Player object
        """

        self.speed = 0

        # Graphics to use for Player
        kwargs['filename'] = "Assets/Cars/f1.png"

        # How much to scale the graphics
        kwargs['scale'] = SPRITE_SCALING

        # Giving Graphics correct orientation
        kwargs["flipped_diagonally"] = True,
        kwargs["flipped_horizontally"] = True,
        kwargs["flipped_vertically"] = False


        # Pass arguments to class arcade.Sprite
        super().__init__(**kwargs)



    def update(self):
        """
        Move the sprite
        """

        # Update center_x
        self.center_x += self.change_x
        self.center_y += self.change_y


        # reset change_x and change_y
        self.change_x *= 0.95
        self.change_y *= 0.95


class Skidmark(arcade.Sprite):


    def __init__(self, **kwargs):
        """
        Setup new Player object
        """

        # Graphics to use
        kwargs['filename'] = "Assets/Skidmarks/skidmark_short_1.png"

        # How much to scale the graphics
        kwargs['scale'] = SPRITE_SCALING

        # Giving Graphics correct orientation
        kwargs["flipped_diagonally"] = True,
        kwargs["flipped_horizontally"] = True,
        kwargs["flipped_vertically"] = False


        # Pass arguments to class arcade.SpriteList
        super().__init__(**kwargs)

        # start timer
        self.timer = SKIDMARK_START_TIME

    def on_update(self, delta_time):
        self.timer -= delta_time
        self.timer = max(0, self.timer)

        # fade out effect
        self.alpha = 255 * (self.timer/ SKIDMARK_START_TIME)

        if self.timer <= 0:
            self.kill()



class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__(width, height)

        # Set up engine info
        self.player_list = None
        self.wall_list = None
        self.physics_engine = None

        # Set up the player info
        self.player_sprite = None
        self.player_score = None

        # Set up skidmarks
        self.skidmark_spritelist = None

        # Skidmark the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Cameras
        self.camera = None
        self.gui_camera = None

        # Get list of joysticks
        joysticks = arcade.get_joysticks()

        if joysticks:
            print("Found {} joystick(s)".format(len(joysticks)))

            # Use 1st joystick found
            self.joystick = joysticks[0]

            # Communicate with joystick
            self.joystick.open()

            # Map joysticks functions to local functions
            self.joystick.on_joybutton_press = self.on_joybutton_press
            self.joystick.on_joybutton_release = self.on_joybutton_release
            self.joystick.on_joyaxis_motion = self.on_joyaxis_motion
            self.joystick.on_joyhat_motion = self.on_joyhat_motion

        else:
            print("No joysticks found")
            self.joystick = None

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # No points when the game starts
        self.player_score = 0

        
        # Create a Player object
        self.player_sprite = Player(
            center_x=PLAYER_START_X,
            center_y=PLAYER_START_Y
        )
        # Create skidmark sprite list
        self.skidmark_spritelist = arcade.SpriteList()

        # Tilemap
        map_name = "Tilemaps/sand.tmx"

        layer_options = {
            "Dirt": {"use_spatial_hash": True},
            "Track": {"use_spatial_hash": True},
            "Finish": {"use_spatial_hash": True},
            "Design": {"use_spatial_hash": True},
        }

        
        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(
            map_name, layer_options=layer_options, scaling=TILE_SCALING
        )

        # Set wall and coin SpriteLists
        self.wall_list = self.tile_map.sprite_lists["Dirt"]
        self.track_list = self.tile_map.sprite_lists["Track"]
        self.finish_list = self.tile_map.sprite_lists["Finish"]
        self.design_list = self.tile_map.sprite_lists["Design"]

        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Keep player from running through the wall_list layer
        walls = [self.wall_list, ]
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, walls
        )

        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Center camera on user
        self.pan_camera_to_user()

    def on_draw(self):
        """
        Render the screen.
        """

        # Use camera
        self.camera.use()

        # This command has to happen before we start drawing
        arcade.start_render()



        # Draw map
        self.wall_list.draw()
        self.design_list.draw()
        self.track_list.draw()
        self.finish_list.draw()

        # Draw skidmarks
        self.skidmark_spritelist.draw()
        
        # Draw the player sprite
        self.player_sprite.draw()

        # Gui camera
        self.gui_camera.use()

        # Draw speed on screen
        arcade.draw_text(
            "SPEED_X: {}".format(self.player_sprite.change_x),  # Text to show
            10,                  # X position
            SCREEN_HEIGHT - 20,  # Y positon
            arcade.color.WHITE   # Color of text
        )
        arcade.draw_text(
            "SPEED_Y: {}".format(self.player_sprite.change_y),  # Text to show
            10,                  # X position
            SCREEN_HEIGHT - 40,  # Y positon
            arcade.color.WHITE   # Color of text
        )

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        # Move player with keyboard
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.speed += PLAYER_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.speed -= PLAYER_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.angle += PLAYER_TURN_SPEED * math.sqrt(self.player_sprite.change_x ** 2 + self.player_sprite.change_y ** 2)
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.angle -= PLAYER_TURN_SPEED * math.sqrt(self.player_sprite.change_x ** 2 + self.player_sprite.change_y ** 2)
        
        self.player_sprite.forward(self.player_sprite.speed)

        self.player_sprite.speed = 0
                    # Call update on all sprites
        self.physics_engine.update()

        # Pan to the user
        self.pan_camera_to_user(panning_fraction=0.12)

        # Move player with joystick if present
        if self.joystick:
            self.player_sprite.change_x = round(self.joystick.x) * PLAYER_SPEED

        # Update player sprite
        self.player_sprite.update()

        self.skidmark_spritelist.append(Skidmark(
            center_x=self.player_sprite.center_x,
            center_y=self.player_sprite.center_y,
            angle=self.player_sprite.angle
            ))

        for skidmark in self.skidmark_spritelist:
            skidmark.on_update(delta_time)

    def pan_camera_to_user(self, panning_fraction: float = 1.0):
        """ Manage Scrolling """

        # This spot would center on the user
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        user_centered = screen_center_x, screen_center_y

        self.camera.move_to(user_centered, panning_fraction)
        
        


    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """

        # Skidmark state of arrow keys
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True


    def on_key_release(self, key, modifiers):
        """
        Called whenever a key is released.
        """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_joybutton_press(self, joystick, button_no):
        print("Button pressed:", button_no)
        # Press the fire key

    def on_joybutton_release(self, joystick, button_no):
        print("Button released:", button_no)

    def on_joyaxis_motion(self, joystick, axis, value):
        print("Joystick axis {}, value {}".format(axis, value))

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print("Joystick hat ({}, {})".format(hat_x, hat_y))

def main():
    """
    Main method
    """

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
