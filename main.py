import pygame
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.ui import UI
from game.control import MouseController
from game.engine import GameEngine, Fruit, Bomb

class GameState:
    START = 0
    PLAYING = 1
    GAME_OVER = 2
    EXPLOSION = 3

class FruitNinjaGame:
    def __init__(self):
        pygame.init()
        
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 60
        self.GAME_DURATION = 30
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("切水果游戏")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.ui = UI(self.screen, self.WIDTH, self.HEIGHT)
        self.controller = MouseController(self.screen, self.WIDTH, self.HEIGHT)
        self.engine = GameEngine(self.screen, self.WIDTH, self.HEIGHT)
        
        self.state = GameState.START
        self.score = 0
        self.cut_count = 0
        self.missed_count = 0
        self.start_time = 0
        self.total_time = 0
        self.time_left = self.GAME_DURATION
        
        self.background_color = (30, 30, 50)
        self._start_button_rect = None
        self._gameover_button_rect = None
            
    def check_missed_fruits(self):
        for obj in list(self.engine.objects):
            if isinstance(obj, Fruit) and not obj.is_sliced:
                if obj.y > self.HEIGHT + 50:
                    self.missed_count += 1
                    
    def handle_collisions(self, collided_objects):
        fruits_cut = []
        bomb_hit = None
        
        for obj in collided_objects:
            if isinstance(obj, Fruit):
                fruits_cut.append(obj)
            elif isinstance(obj, Bomb):
                bomb_hit = obj
                
        if bomb_hit:
            bomb_hit.explode()
            self.state = GameState.EXPLOSION
            self.total_time = time.time() - self.start_time
            return
            
        if fruits_cut:
            points_earned = min(len(fruits_cut), 3)
            self.score += points_earned
            self.cut_count += len(fruits_cut)
            
            segment = self.controller.get_current_segment()
            if segment:
                direction = (
                    segment[1][0] - segment[0][0],
                    segment[1][1] - segment[0][1]
                )
            else:
                direction = (1, 0)
                
            for fruit in fruits_cut:
                fruit.slice(direction)
                
    def update_timer(self):
        if self.state == GameState.PLAYING:
            elapsed = time.time() - self.start_time
            self.time_left = max(0, self.GAME_DURATION - elapsed)
            
            if self.time_left <= 0:
                self.state = GameState.GAME_OVER
                self.total_time = self.GAME_DURATION
                
    def start_game(self):
        self.state = GameState.PLAYING
        self.start_time = time.time()
        self.engine.reset()
        self.controller.reset()
        self.score = 0
        self.cut_count = 0
        self.missed_count = 0
        self.time_left = self.GAME_DURATION
        
    def reset_game(self):
        self.state = GameState.START
        self.score = 0
        self.cut_count = 0
        self.missed_count = 0
        self.time_left = self.GAME_DURATION
        self.total_time = 0
        self.engine.reset()
        self.controller.reset()
        
    def run(self):
        while self.running:
            self.screen.fill(self.background_color)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                    
                elif self.state == GameState.PLAYING:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.controller.is_dragging = True
                            self.controller.trail.clear()
                            pos = pygame.mouse.get_pos()
                            self.controller.trail.append(pos)
                            
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.controller.is_dragging = False
                            self.controller.trail.clear()
                            
                    elif event.type == pygame.MOUSEMOTION:
                        if self.controller.is_dragging:
                            pos = pygame.mouse.get_pos()
                            self.controller.trail.append(pos)
                            
                elif self.state == GameState.START or self.state == GameState.GAME_OVER:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            pos = pygame.mouse.get_pos()
                            
                            if self.state == GameState.START:
                                if hasattr(self, '_start_button_rect') and self._start_button_rect:
                                    if self._start_button_rect.collidepoint(pos):
                                        self.start_game()
                                        
                            elif self.state == GameState.GAME_OVER:
                                if hasattr(self, '_gameover_button_rect') and self._gameover_button_rect:
                                    if self._gameover_button_rect.collidepoint(pos):
                                        self.reset_game()
            
            if self.state == GameState.START:
                self._start_button_rect = self.ui.draw_start_screen()
                self._gameover_button_rect = None
                
            elif self.state == GameState.PLAYING:
                self.update_timer()
                self.check_missed_fruits()
                
                current_time = pygame.time.get_ticks()
                self.engine.update(current_time)
                
                self.engine.draw()
                
                self.controller.draw_trail()
                
                active_objects = self.engine.get_active_objects()
                collided = self.controller.check_collision(active_objects)
                if collided:
                    self.handle_collisions(collided)
                    
                self.ui.draw_game_ui(self.score, self.time_left, self.cut_count, self.missed_count)
                
            elif self.state == GameState.EXPLOSION:
                current_time = pygame.time.get_ticks()
                self.engine.update(current_time)
                self.engine.draw()
                
                explosion_complete = False
                for obj in self.engine.objects:
                    if isinstance(obj, Bomb) and obj.is_exploded:
                        if obj.is_explosion_complete():
                            explosion_complete = True
                            break
                
                if explosion_complete:
                    self.state = GameState.GAME_OVER
                    
                self.ui.draw_game_ui(self.score, self.time_left, self.cut_count, self.missed_count)
                
            elif self.state == GameState.GAME_OVER:
                self._gameover_button_rect = self.ui.draw_game_over_screen(
                    self.score, self.cut_count, 
                    self.missed_count, self.total_time
                )
                self._start_button_rect = None
                
            pygame.display.flip()
            self.clock.tick(self.FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FruitNinjaGame()
    game.run()
