import pygame
import random
import math

class PhysicsObject:
    def __init__(self, x, y, vx, vy, radius, gravity=0.3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.gravity = gravity
        self.is_sliced = False
        self.is_exploded = False
        
    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        
    def is_off_screen(self, width, height):
        return self.y > height + 100 or self.x < -100 or self.x > width + 100


class Fruit(PhysicsObject):
    FRUIT_TYPES = {
        'apple': {'color': (255, 100, 100), 'name': '苹果'},
        'banana': {'color': (255, 255, 100), 'name': '香蕉'},
        'pineapple': {'color': (255, 200, 100), 'name': '菠萝'}
    }
    
    def __init__(self, x, y, vx, vy, fruit_type, gravity=0.3):
        super().__init__(x, y, vx, vy, 35, gravity)
        self.fruit_type = fruit_type
        self.color = self.FRUIT_TYPES[fruit_type]['color']
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.05, 0.05)
        self.sliced_pieces = []
        
    def update(self):
        if not self.is_sliced:
            super().update()
            self.rotation += self.rotation_speed
        else:
            for piece in self.sliced_pieces:
                piece.update()
                
    def draw(self, screen):
        if not self.is_sliced:
            self.draw_whole(screen)
        else:
            for piece in self.sliced_pieces:
                piece.draw(screen)
                
    def draw_whole(self, screen):
        surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        if self.fruit_type == 'apple':
            pygame.draw.circle(surface, self.color, (self.radius, self.radius), self.radius)
            pygame.draw.circle(surface, (100, 255, 100), (self.radius, self.radius - 15), 5)
            
        elif self.fruit_type == 'banana':
            pygame.draw.ellipse(surface, self.color, (0, self.radius - 10, self.radius * 2, 25))
            pygame.draw.arc(surface, (200, 200, 50), (5, self.radius - 5, self.radius * 2 - 10, 15), 0, 3.14, 3)
            
        elif self.fruit_type == 'pineapple':
            pygame.draw.ellipse(surface, self.color, (self.radius - 15, 0, 30, self.radius * 2))
            pygame.draw.polygon(surface, (100, 255, 100), [
                (self.radius, 5),
                (self.radius - 20, 25),
                (self.radius + 20, 25)
            ])
            
        rotated_surface = pygame.transform.rotate(surface, math.degrees(self.rotation))
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surface, rotated_rect.topleft)
        
    def slice(self, direction_vector):
        if self.is_sliced:
            return
            
        self.is_sliced = True
        
        angle = math.atan2(direction_vector[1], direction_vector[0])
        
        left_piece = FruitPiece(
            self.x, self.y,
            self.vx - 1, self.vy - 0.5,
            self.fruit_type, self.rotation, 'left', angle
        )
        right_piece = FruitPiece(
            self.x, self.y,
            self.vx + 1, self.vy - 0.5,
            self.fruit_type, self.rotation, 'right', angle
        )
        
        self.sliced_pieces = [left_piece, right_piece]


class FruitPiece(PhysicsObject):
    def __init__(self, x, y, vx, vy, fruit_type, rotation, side, slice_angle, gravity=0.3):
        super().__init__(x, y, vx, vy, 30, gravity)
        self.fruit_type = fruit_type
        self.color = Fruit.FRUIT_TYPES[fruit_type]['color']
        self.rotation = rotation
        self.side = side
        self.slice_angle = slice_angle
        self.rotation_speed = random.choice([-0.1, 0.1])
        
    def update(self):
        super().update()
        self.rotation += self.rotation_speed
        
    def draw(self, screen):
        surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        if self.side == 'left':
            pygame.draw.circle(surface, self.color, (self.radius, self.radius), self.radius)
            pygame.draw.polygon(surface, (255, 255, 255, 50), [
                (self.radius, 0),
                (self.radius, self.radius * 2),
                (0, self.radius)
            ])
        else:
            pygame.draw.circle(surface, self.color, (self.radius, self.radius), self.radius)
            pygame.draw.polygon(surface, (255, 255, 255, 50), [
                (self.radius, 0),
                (self.radius, self.radius * 2),
                (self.radius * 2, self.radius)
            ])
            
        rotated_surface = pygame.transform.rotate(surface, math.degrees(self.rotation + self.slice_angle))
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surface, rotated_rect.topleft)


class Bomb(PhysicsObject):
    def __init__(self, x, y, vx, vy, gravity=0.3):
        super().__init__(x, y, vx, vy, 30, gravity)
        self.color = (50, 50, 50)
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.03, 0.03)
        self.explosion_particles = []
        self.explosion_frame = 0
        
    def update(self):
        if not self.is_exploded:
            super().update()
            self.rotation += self.rotation_speed
        else:
            self.explosion_frame += 1
            for particle in self.explosion_particles:
                particle.update()
                
    def draw(self, screen):
        if not self.is_exploded:
            surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            
            pygame.draw.circle(surface, self.color, (self.radius, self.radius), self.radius)
            pygame.draw.circle(surface, (30, 30, 30), (self.radius - 5, self.radius - 5), 5)
            
            pygame.draw.rect(surface, (150, 100, 50), (self.radius - 3, 0, 6, 15))
            
            spark = random.choice([(255, 200, 50), (255, 100, 50), (255, 255, 50)])
            pygame.draw.circle(surface, spark, (self.radius, -5), 5)
            
            rotated_surface = pygame.transform.rotate(surface, math.degrees(self.rotation))
            rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
            screen.blit(rotated_surface, rotated_rect.topleft)
        else:
            for particle in self.explosion_particles:
                particle.draw(screen)
                
    def explode(self):
        if self.is_exploded:
            return
            
        self.is_exploded = True
        
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            color = random.choice([
                (255, 100, 50), (255, 200, 50),
                (255, 50, 50), (255, 255, 100)
            ])
            self.explosion_particles.append(
                Particle(self.x, self.y, 
                        math.cos(angle) * speed, 
                        math.sin(angle) * speed,
                        color)
            )
            
    def is_explosion_complete(self):
        return self.is_exploded and self.explosion_frame > 30


class Particle(PhysicsObject):
    def __init__(self, x, y, vx, vy, color, lifetime=60):
        super().__init__(x, y, vx, vy, 3, 0.1)
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        
    def update(self):
        super().update()
        self.age += 1
        
    def draw(self, screen):
        if self.age < self.lifetime:
            alpha = int(255 * (1 - self.age / self.lifetime))
            color_with_alpha = (*self.color[:3], alpha)
            surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, color_with_alpha, (self.radius, self.radius), self.radius)
            screen.blit(surface, (int(self.x - self.radius), int(self.y - self.radius)))


class GameEngine:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.objects = []
        self.last_spawn_time = 0
        self.spawn_interval = 700
        self.bomb_probability = 0.12
        self.gravity = 0.35
        
    def spawn_single_object(self):
        x = random.randint(80, self.width - 80)
        y = self.height + 50
        
        vx = random.uniform(-3, 3)
        
        initial_y = y
        
        min_height_from_bottom = self.height * 0.5
        max_height_from_bottom = self.height
        
        min_y_at_peak = self.height - min_height_from_bottom
        max_y_at_peak = self.height - max_height_from_bottom
        
        min_flight_distance = initial_y - min_y_at_peak
        max_flight_distance = initial_y - max_y_at_peak
        
        vy_abs_min = math.sqrt(2 * self.gravity * min_flight_distance)
        vy_abs_max = math.sqrt(2 * self.gravity * max_flight_distance)
        
        vy = -random.uniform(vy_abs_min, vy_abs_max)
        
        if random.random() < self.bomb_probability:
            self.objects.append(Bomb(x, y, vx, vy, self.gravity))
        else:
            fruit_type = random.choice(list(Fruit.FRUIT_TYPES.keys()))
            self.objects.append(Fruit(x, y, vx, vy, fruit_type, self.gravity))
        
    def spawn_object(self):
        count = random.randint(1, 3)
        for _ in range(count):
            self.spawn_single_object()
            
    def update(self, current_time):
        if current_time - self.last_spawn_time > self.spawn_interval:
            self.spawn_object()
            self.last_spawn_time = current_time
            
        for obj in self.objects[:]:
            obj.update()
            
            if obj.is_off_screen(self.width, self.height):
                self.objects.remove(obj)
                
        self.cleanup_exploded_bombs()
        
    def cleanup_exploded_bombs(self):
        for obj in self.objects[:]:
            if isinstance(obj, Bomb) and obj.is_explosion_complete():
                self.objects.remove(obj)
                
    def draw(self):
        for obj in self.objects:
            obj.draw(self.screen)
            
    def get_active_objects(self):
        active = []
        for obj in self.objects:
            if isinstance(obj, Fruit) and not obj.is_sliced:
                active.append(obj)
            elif isinstance(obj, Bomb) and not obj.is_exploded:
                active.append(obj)
        return active
        
    def reset(self):
        self.objects = []
        self.last_spawn_time = 0
