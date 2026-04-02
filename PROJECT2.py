import sys
from time import sleep
import pygame
from pygame.sprite import Sprite, Group


"""
Twisha Space Battle Gameeeee

So my this project is inspired by Python Crash Course (Alien Invasion),
with some of the custom improvements such as:
- Score tracking system
- Increasing difficulty levels
- Lives system
- Pause functionality
- Custom UI design
"""


class TwishaGameSettings:
    

    def __init__(self):
        
        self.screen_width = 1200
        self.screen_height = 750
        self.bg_color = (8, 10, 30)

        self.ship_limit = 3

        self.bullet_width = 4
        self.bullet_height = 18
        self.bullet_color = (255, 220, 90)
        self.bullets_allowed = 5

        self.fleet_drop_speed = 12

        self.speedup_scale = 1.15
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        
        self.ship_speed = 5.0
        self.bullet_speed = 7.0
        self.alien_speed = 1.5
        self.fleet_direction = 1
        self.alien_points = 50

    def increase_speed(self):
       
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)


class TwishaGameStats:
    
    def __init__(self, game):
        
        self.settings = game.settings
        self.reset_stats()
        self.game_active = False
        self.high_score = 0

    def reset_stats(self):
       
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1


class TwishaShip(Sprite):
    

    def __init__(self, game):
       
        super().__init__()
        self.screen = game.screen
        self.settings = game.settings
        self.screen_rect = game.screen.get_rect()

        self.image = pygame.Surface((60, 42), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.image,
            (70, 220, 255),
            [(30, 0), (0, 42), (60, 42)]
        )
        pygame.draw.polygon(
            self.image,
            (210, 245, 255),
            [(30, 6), (10, 38), (50, 38)],
            3
        )

        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom
        self.rect.y -= 10

        self.x = float(self.rect.x)

        self.moving_right = False
        self.moving_left = False

    def update(self):
        
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        self.rect.x = self.x

    def blitme(self):
        
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        
        self.rect.midbottom = self.screen_rect.midbottom
        self.rect.y -= 10
        self.x = float(self.rect.x)


class TwishaBullet(Sprite):
    

    def __init__(self, game):
       
        super().__init__()
        self.screen = game.screen
        self.settings = game.settings
        self.color = self.settings.bullet_color

        self.rect = pygame.Rect(
            0, 0, self.settings.bullet_width, self.settings.bullet_height
        )
        self.rect.midtop = game.ship.rect.midtop

        self.y = float(self.rect.y)

    def update(self):
        
        self.y -= self.settings.bullet_speed
        self.rect.y = self.y

    def draw_bullet(self):
        
        pygame.draw.rect(self.screen, self.color, self.rect)


class TwishaAlien(Sprite):
    

    colors = [
        (0, 255, 140),
        (255, 100, 120),
        (180, 110, 255),
        (255, 180, 60),
    ]

    def __init__(self, game, color_index=0):
        
        super().__init__()
        self.screen = game.screen
        self.settings = game.settings

        color = TwishaAlien.colors[color_index % len(TwishaAlien.colors)]

        self.image = pygame.Surface((44, 32), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (2, 8, 40, 20), border_radius=8)
        pygame.draw.rect(self.image, color, (8, 0, 8, 10), border_radius=3)
        pygame.draw.rect(self.image, color, (28, 0, 8, 10), border_radius=3)
        pygame.draw.circle(self.image, (15, 15, 25), (15, 18), 5)
        pygame.draw.circle(self.image, (15, 15, 25), (29, 18), 5)
        pygame.draw.circle(self.image, (255, 255, 255), (16, 17), 2)
        pygame.draw.circle(self.image, (255, 255, 255), (30, 17), 2)

        self.rect = self.image.get_rect()
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
        self.x = float(self.rect.x)

    def check_edges(self):
       
        screen_rect = self.screen.get_rect()
        return self.rect.right >= screen_rect.right or self.rect.left <= 0

    def update(self):
        
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x


class TwishaButton:
    

    def __init__(self, game, msg):
        
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()

        self.width, self.height = 220, 60
        self.button_color = (40, 180, 120)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 42)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        self.prep_msg(msg)

    def prep_msg(self, msg):
       
        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
       
        pygame.draw.rect(self.screen, self.button_color, self.rect, border_radius=14)
        self.screen.blit(self.msg_image, self.msg_image_rect)


class TwishaScoreboard:
    

    def __init__(self, game):
        
        self.game = game
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = game.settings
        self.stats = game.stats

        self.text_color = (255, 255, 255)
        self.level_color = (120, 210, 255)
        self.high_score_color = (255, 220, 90)
        self.font = pygame.font.SysFont("consolas", 28)

        self.prep_images()

    def prep_images(self):
       
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

    def prep_score(self):
        
        rounded_score = round(self.stats.score, -1)
        score_str = f"Score: {rounded_score:,}"
        self.score_image = self.font.render(
            score_str, True, self.text_color, self.settings.bg_color
        )

        self.score_rect = self.score_image.get_rect()
        self.score_rect.left = 20
        self.score_rect.top = 20

    def prep_high_score(self):
        
        high_score = round(self.stats.high_score, -1)
        high_score_str = f"High Score: {high_score:,}"
        self.high_score_image = self.font.render(
            high_score_str, True, self.high_score_color, self.settings.bg_color
        )

        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.midtop = self.screen_rect.midtop
        self.high_score_rect.y = 20

    def prep_level(self):
       
        level_str = f"Level: {self.stats.level}"
        self.level_image = self.font.render(
            level_str, True, self.level_color, self.settings.bg_color
        )

        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.screen_rect.right - 20
        self.level_rect.top = 20

    def prep_ships(self):
        
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = TwishaShip(self.game)
            ship.rect.x = 20 + ship_number * 45
            ship.rect.y = 60
            self.ships.add(ship)

    def check_high_score(self):
        
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def show_score(self):
        
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)


class TwishaGame:
    

    def __init__(self):
        
        pygame.init()
        self.settings = TwishaGameSettings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Twisha Space Battle")

        self.clock = pygame.time.Clock()

        self.stats = TwishaGameStats(self)
        self.ship = TwishaShip(self)
        self.bullets = Group()
        self.aliens = Group()
        self.button = TwishaButton(self, "Play")
        self.scoreboard = TwishaScoreboard(self)

        self.stars = self.create_stars()

        self.title_font = pygame.font.SysFont("consolas", 72, bold=True)
        self.info_font = pygame.font.SysFont("consolas", 28)
        self.pause_font = pygame.font.SysFont("consolas", 52, bold=True)

        self.paused = False

        self.create_fleet()

    def create_stars(self):
        
        stars = []
        for x in range(30, self.settings.screen_width, 95):
            for y in range(25, self.settings.screen_height, 75):
                stars.append((x, y))
        return stars

    def run_game(self):
       
        while True:
            self.check_events()

            if self.stats.game_active and not self.paused:
                self.ship.update()
                self.update_bullets()
                self.update_aliens()

            self.update_screen()
            self.clock.tick(60)

    def check_events(self):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self.check_keyup_events(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.check_play_button(mouse_pos)

    def check_keydown_events(self, event):
        
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            if self.stats.game_active and not self.paused:
                self.fire_bullet()
        elif event.key == pygame.K_p:
            if self.stats.game_active:
                self.paused = not self.paused
        elif event.key == pygame.K_q:
            sys.exit()

    def check_keyup_events(self, event):
        
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def check_play_button(self, mouse_pos):
        
        button_clicked = self.button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.paused = False

            self.scoreboard.prep_images()

            self.aliens.empty()
            self.bullets.empty()

            self.create_fleet()
            self.ship.center_ship()

            pygame.mouse.set_visible(False)

    def fire_bullet(self):
        
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = TwishaBullet(self)
            self.bullets.add(new_bullet)

    def update_bullets(self):
        
        self.bullets.update()

        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self.check_bullet_alien_collisions()

    def check_bullet_alien_collisions(self):
       
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True
        )

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)

            self.scoreboard.prep_score()
            self.scoreboard.check_high_score()

        if not self.aliens:
            self.bullets.empty()
            self.create_fleet()
            self.settings.increase_speed()

            self.stats.level += 1
            self.scoreboard.prep_level()

    def update_aliens(self):
        
        self.check_fleet_edges()
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self.ship_hit()

        self.check_aliens_bottom()

    def ship_hit(self):
        
        if self.stats.ships_left > 1:
            self.stats.ships_left -= 1
            self.scoreboard.prep_ships()

            self.aliens.empty()
            self.bullets.empty()

            self.create_fleet()
            self.ship.center_ship()

            sleep(0.5)
        else:
            self.stats.ships_left = 0
            self.scoreboard.prep_ships()
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def check_aliens_bottom(self):
        
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self.ship_hit()
                break

    def create_fleet(self):
        
        alien = TwishaAlien(self)
        alien_width, alien_height = alien.rect.size

        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        ship_height = self.ship.rect.height
        available_space_y = (
            self.settings.screen_height - (3 * alien_height) - ship_height - 80
        )
        number_rows = available_space_y // (2 * alien_height)

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self.create_alien(alien_number, row_number)

    def create_alien(self, alien_number, row_number):
       
        alien = TwishaAlien(self, row_number)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = 100 + 2 * alien_height * row_number
        self.aliens.add(alien)

    def check_fleet_edges(self):
        
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self.change_fleet_direction()
                break

    def change_fleet_direction(self):
       
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def draw_background(self):
        
        self.screen.fill(self.settings.bg_color)
        for star in self.stars:
            pygame.draw.circle(self.screen, (220, 220, 240), star, 2)

    def draw_title_screen(self):
        
        title_image = self.title_font.render(
            "TWISHA SPACE BATTLE", True, (70, 220, 255)
        )
        title_rect = title_image.get_rect(
            center=(self.settings.screen_width // 2, 180)
        )
        self.screen.blit(title_image, title_rect)

        sub_image = self.info_font.render(
            
            True,
            (230, 230, 230)
        )
        sub_rect = sub_image.get_rect(
            center=(self.settings.screen_width // 2, 250)
        )
        self.screen.blit(sub_image, sub_rect)

        note_image = self.info_font.render(
            
            True,
            (255, 220, 90)
        )
        note_rect = note_image.get_rect(
            center=(self.settings.screen_width // 2, 290)
        )
        self.screen.blit(note_image, note_rect)

    def draw_pause_text(self):
    
        pause_image = self.pause_font.render("PAUSED", True, (255, 120, 120))
        pause_rect = pause_image.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(pause_image, pause_rect)

    def draw_game_over_text(self):
        
        over_image = self.pause_font.render("GAME OVER", True, (255, 90, 90))
        over_rect = over_image.get_rect(
            center=(self.settings.screen_width // 2, 330)
        )
        self.screen.blit(over_image, over_rect)

        restart_image = self.info_font.render(
            
            True,
            (255, 255, 255)
        )
        restart_rect = restart_image.get_rect(
            center=(self.settings.screen_width // 2, 385)
        )
        self.screen.blit(restart_image, restart_rect)

    def update_screen(self):
        
        self.draw_background()

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.scoreboard.show_score()

        if not self.stats.game_active:
            self.draw_title_screen()
            self.button.draw_button()

            if self.stats.ships_left == 0:
                self.draw_game_over_text()

        if self.paused and self.stats.game_active:
            self.draw_pause_text()

        pygame.display.flip()


if __name__ == '__main__':
    game = TwishaGame()
    game.run_game()