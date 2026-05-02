import pygame
from collections import deque

class MouseController:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.is_dragging = False
        self.trail = deque(maxlen=20)
        self.trail_color = (255, 255, 255)
        self.trail_width = 3
        
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.is_dragging = True
                    self.trail.clear()
                    pos = pygame.mouse.get_pos()
                    self.trail.append(pos)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False
                    self.trail.clear()
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    pos = pygame.mouse.get_pos()
                    self.trail.append(pos)
                    
        return None
        
    def draw_trail(self):
        if len(self.trail) >= 2:
            for i in range(len(self.trail) - 1):
                alpha = int((i / len(self.trail)) * 255)
                color = (
                    min(255, self.trail_color[0]),
                    min(255, self.trail_color[1]),
                    min(255, self.trail_color[2]),
                )
                
                if len(self.trail) > 5:
                    width = max(1, self.trail_width * (i + 1) // len(self.trail))
                else:
                    width = self.trail_width
                    
                pygame.draw.line(
                    self.screen, 
                    color, 
                    self.trail[i], 
                    self.trail[i + 1], 
                    width
                )
                
    def get_current_segment(self):
        if len(self.trail) >= 2:
            return (self.trail[-2], self.trail[-1])
        return None
        
    def line_intersects_circle(self, p1, p2, circle_center, radius):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        fx = p1[0] - circle_center[0]
        fy = p1[1] - circle_center[1]
        
        a = dx * dx + dy * dy
        
        if a < 1e-6:
            dist_sq = fx * fx + fy * fy
            return dist_sq <= radius * radius
        
        b = 2 * (fx * dx + fy * dy)
        c = fx * fx + fy * fy - radius * radius
        
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return False
            
        discriminant = discriminant ** 0.5
        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)
        
        return (t1 >= 0 and t1 <= 1) or (t2 >= 0 and t2 <= 1)
        
    def check_collision(self, objects):
        if not self.is_dragging or len(self.trail) < 2:
            return []
            
        segment = self.get_current_segment()
        if not segment:
            return []
            
        collided = []
        for obj in objects:
            if obj.is_sliced or obj.is_exploded:
                continue
                
            if self.line_intersects_circle(
                segment[0], segment[1],
                (obj.x, obj.y),
                obj.radius
            ):
                collided.append(obj)
                
        return collided
        
    def reset(self):
        self.is_dragging = False
        self.trail.clear()
