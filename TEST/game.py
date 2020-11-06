import arcade
from explosion import Explosion
import math
import os
import random
from menuscreen import MenuView
from instructionscreen import InstructionView
from pausescreen import PauseView
from gameoverscreen import GameOverView


res = os.path.dirname(os.path.abspath(__file__))
os.chdir(res)


SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Space Survivor"
SCALING = 1 / 3
BULLET_SPEED = 3
SCALING_ENEMY = 1 / 5


class FlyingSprite(arcade.Sprite):
    """Base class for all flying sprites
       Flying sprites include enemies and clouds
    """

    def update(self):
        """Update the position of the sprite
        When it moves off screen to the left, remove it
        """

        # Move the sprite
        super().update()

        # Remove if off the screen
        if (
                self.velocity[0] < 0 and self.right < 0
                or self.velocity[0] > 0 and self.left > SCREEN_WIDTH
        ):
            self.remove_from_sprite_lists()


class SpaceSurvivor(arcade.View):
    """ Main application class."""

    def __init__(self):
        super().__init__()

        self.time_taken = 0
        
        self.frame_count = 0
        self.pause = PauseView(self)
        self.music = None
        self.enemyRemoving_sound = None
        self.projectile_sound = None
        self.background = None
        self.enemies_list = arcade.SpriteList()
        self.clouds_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()
        self.player = arcade.Sprite()
        self.projectile_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosions_list = None

        # Pre-load the animation frame
        self.explosion_texture_list = []

        columns = 16
        count = 60
        sprite_width = 256
        sprite_height = 256

        expl1 = ":resources:images/spritesheets/explosion.png"
        # Load the explosions from a sprite sheet
        self.explosion_texture_list = arcade.load_spritesheet(expl1,
                                                              sprite_width,
                                                              sprite_height,
                                                              columns,
                                                              count)
        # Used to keep track of our scrolling
        self.view_top = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """

        self.background = arcade.load_texture("res/images/space_survivor-background.webp")
        self.player = arcade.Sprite("res/images/space_survivor-space-ship.webp", SCALING)
        self.player.center_y = SCREEN_HEIGHT / 2
        self.player.left = 0
        self.all_sprites.append(self.player)
        self.explosions_list = arcade.SpriteList()

        # set the time interval that enemies and clouds appears
        arcade.schedule(self.add_enemy, 1)
        arcade.schedule(self.add_cloud, 3)

        # play music in game
        self.music = arcade.load_sound("res/sounds/audio_mangler_space_drone_5_206.mp3")

        # add collision sound
        self.enemyRemoving_sound = arcade.load_sound("res/sounds/zap2.ogg")

        self.projectile_sound = arcade.load_sound("res/sounds/laser9.ogg")

        # playing music background in loop
        # arcade.schedule(self.play_background_music, 16)
        self.music.play(volume=0.09, loop=True)

    def on_show(self):
        self.background = arcade.load_texture("res/images/space_survivor-background.webp")
        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)

    def fire_missile(self):
        """Fires a missile against the incoming enemies"""

        projectile = FlyingSprite("res/images/laserRed06.png")

        projectile.center_x = self.player.center_x + 70
        projectile.center_y = self.player.center_y
        projectile.angle = -90
        projectile.velocity = (20, 0)

        self.projectile_list.append(projectile)
        self.all_sprites.append(projectile)

    def add_enemy(self, delta_time: float):
        """Adds a new enemy to the screen
        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """

        enemy = FlyingSprite("res/images/space_survivor-aliens.webp", SCALING_ENEMY)

        # Set its position to a random height and off screen right
        enemy.left = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 80)
        enemy.top = random.randint(40, SCREEN_HEIGHT - 80)
        enemy.bottom = random.randint(40, SCREEN_HEIGHT - 80)

        # Set its speed to a random speed heading left
        enemy.velocity = (random.randint(-4, -2), 0)

        # Add enemy to the enemies_list
        self.enemies_list.append(enemy)
        # Add enemy to the list of all_sprites.
        self.all_sprites.append(enemy)

    def add_cloud(self, delta_time: float):
        """Adds a new enemy to the screen
        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """

        cloud = FlyingSprite("res/images/space_survivor-comet-2.webp", SCALING)

        # Set its position to a random height and off screen right
        cloud.left = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 80)
        cloud.top = random.randint(10, SCREEN_HEIGHT - 10)

        # Set its speed to a random speed heading left
        cloud.velocity = (random.randint(-2, -1), 0)

        # Add it to the enemies list
        self.clouds_list.append(cloud)
        self.all_sprites.append(cloud)

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()

        # Divide screen width/height by two to get the horizontal/vertical center of the screen
        arcade.draw_texture_rectangle(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT,
                                      self.background)

        self.enemies_list.draw()
        self.clouds_list.draw()
        self.player.draw()
        self.projectile_list.draw()
        self.bullet_list.draw()
        self.explosions_list.draw()


        # Draw our score on the screen, scrolling it with the viewport
        score = f"Score: {self.score}"
        arcade.draw_text(score, 10 + self.view_left, 740 + self.view_top,
                         arcade.csscolor.YELLOW, 20)

    def toggle_pause(self):
        # If there is a pause view active we need to unpause the game
        if self.pause:
            self.pause = None
            arcade.schedule(self.add_enemy, 1)
            arcade.schedule(self.add_cloud, 3)
        # Otherwise we pause the game and show the pause view
        else:
            arcade.unschedule(self.add_enemy)
            arcade.unschedule(self.add_cloud)
            self.pause = PauseView(self)
            self.window.show_view(self.pause)
            self.fire_missile()

    def on_key_press(self, symbol: int, modifiers: int):
        """ Handle user keyboard input
        q or ESCAPE: Quit the game
        p or BACKSPACE: Pause/Unpause the game
        z/q/s/d: Move up, left, down and right
        Arrows : Move up, left, down and right
        Arguments:
            symbol {int}: Which key was pressed
            modifiers {int}: Which modifiers were pressed
        """

        if symbol == arcade.key.ESCAPE:
            # quit game window
            arcade.close_window()

        if symbol == arcade.key.P:
            self.toggle_pause()

        if symbol == arcade.key.SPACE:
            # throwing projectiles against enemy
            self.fire_missile()
            self.projectile_sound.play(volume=0.04)

        if symbol == arcade.key.Z or symbol == arcade.key.UP:
            # move player up
            self.player.change_y = 5

        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            # move player down
            self.player.change_y = -5

        if symbol == arcade.key.Q or symbol == arcade.key.LEFT:
            # move player forward
            self.player.change_x = -5

        if symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            # move player backward
            self.player.change_x = 5

    def on_key_release(self, symbol: int, modifiers: int):
        """ cancel movement pressed by a given key in on_key_press function
        when the key is released
        Arguments:
            symbol {int}: Which key was pressed
            modifiers {int}: Which modifiers were pressed
        """

        if (symbol == arcade.key.Z
                or symbol == arcade.key.S
                or symbol == arcade.key.UP
                or symbol == arcade.key.DOWN
        ):
            self.player.change_y = 0

        if (symbol == arcade.key.Q
                or symbol == arcade.key.D
                or symbol == arcade.key.LEFT
                or symbol == arcade.key.RIGHT
        ):
            self.player.change_x = 0

    def on_update(self, delta_time: float):
        """ game logic: updating positions and statuses of all game objects.
            Arguments:
                delta_time {float}: Time since the last update
        """

        self.frame_count += 1
        self.explosions_list.update()
        self.time_taken += delta_time

        for enemy in self.enemies_list:

            # First, calculate the angle to the player. We could do this
            # only when the bullet fires, but in this case we will rotate
            # the enemy to face the player each frame, so we'll do this
            # each frame.

            # Position the start at the enemy's current location
            start_x = enemy.center_x
            start_y = enemy.center_y

            # Get the destination location for the bullet
            dest_x = self.player.center_x
            dest_y = self.player.center_y

            # Do math to calculate how to get the bullet to the destination.
            # Calculation the angle in radians between the start points
            # and end points. This is the angle the bullet will travel.
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            # Set the enemy to face the player.
            enemy.angle = math.degrees(angle) - 90

            # Shoot every 60 frames change of shooting each frame
            if self.frame_count % 300 == 0:
                bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png")
                bullet.center_x = start_x
                bullet.center_y = start_y

                # Angle the bullet sprite
                bullet.angle = math.degrees(angle)

                # Taking into account the angle, calculate our change_x
                # and change_y. Velocity is how fast the bullet travels.
                bullet.change_x = math.cos(angle) * BULLET_SPEED
                bullet.change_y = math.sin(angle) * BULLET_SPEED

                self.bullet_list.append(bullet)

                # for bullet in self.bullet_list():
                if bullet.left < 0:
                    bullet.remove_from_sprite_lists()

        self.bullet_list.update()

        # loop through each projectile to check if it hits an enemy
        for projectile in self.projectile_list:
            # check if a projectile hit an enemy ship
            contact_list = arcade.check_for_collision_with_list(projectile, self.enemies_list)

            # if it is the case of contact projectile/enemy
            if len(contact_list) > 0:
                # Make an explosion
                explosion = Explosion(self.explosion_texture_list)

                # Move it to the location of the enemy ship
                explosion.center_x = contact_list[0].center_x
                explosion.center_y = contact_list[0].center_y

                # update() to set image we start on
                explosion.update()

                # Add to a list of sprites that are explosions
                self.explosions_list.append(explosion)

        # check for collision
        if len(self.player.collides_with_list(self.enemies_list)) > 0:
            self.player.remove_from_sprite_lists()
            game_over_view = GameOverView()
            game_over_view.time_taken = self.time_taken
            self.window.set_mouse_visible(True)
            self.window.show_view(game_over_view)

        if self.player.collides_with_list(self.bullet_list):
            self.player.remove_from_sprite_lists()
            game_over_view = GameOverView()
            game_over_view.time_taken = self.time_taken
            self.window.set_mouse_visible(True)
            self.window.show_view(game_over_view)

        # remove enemies those hit by projectiles
        for enemy in self.enemies_list:
            collisions = enemy.collides_with_list(self.projectile_list)
            if collisions:
                enemy.remove_from_sprite_lists()
                arcade.play_sound(self.enemyRemoving_sound, volume=0.03, pan=0.0)
                # Add one to the score
                self.score += 10
                for projectile in collisions:
                    projectile.remove_from_sprite_lists()

        # updating enemies
        for enemy in self.all_sprites:
            enemy.update()

        # Keep the player on screen
        if self.player.top > SCREEN_HEIGHT:
            self.player.top = SCREEN_HEIGHT

        if self.player.right > SCREEN_WIDTH:
            self.player.right = SCREEN_WIDTH

        if self.player.bottom < 0:
            self.player.bottom = 0

        if self.player.left < 0:
            self.player.left = 0


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
