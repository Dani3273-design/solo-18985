import pygame
import sys
import os

class UI:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.init_fonts()
        
    def init_fonts(self):
        mac_font_paths = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/HelveticaNeue.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
        ]
        
        for font_path in mac_font_paths:
            if os.path.exists(font_path):
                try:
                    self.font_large = pygame.font.Font(font_path, 72)
                    self.font_medium = pygame.font.Font(font_path, 36)
                    self.font_small = pygame.font.Font(font_path, 24)
                    return
                except:
                    continue
        
        font_names = [
            'PingFang SC', 'Heiti SC', 'STHeiti',
            'Microsoft YaHei', 'SimHei', 'SimSun',
            'Arial Unicode MS', 'Noto Sans CJK SC'
        ]
        
        for font_name in font_names:
            try:
                test_font = pygame.font.SysFont(font_name, 24)
                test_render = test_font.render('中', True, (255, 255, 255))
                if test_render.get_width() > 5:
                    self.font_large = pygame.font.SysFont(font_name, 72)
                    self.font_medium = pygame.font.SysFont(font_name, 36)
                    self.font_small = pygame.font.SysFont(font_name, 24)
                    return
            except:
                continue
        
        try:
            all_fonts = pygame.font.get_fonts()
            for font_name in all_fonts:
                if any(cjk in font_name.lower() for cjk in ['cjk', 'chinese', 'japanese', 'korean', 'hei', 'song', 'kai', 'fang']):
                    try:
                        test_font = pygame.font.SysFont(font_name, 24)
                        test_render = test_font.render('中', True, (255, 255, 255))
                        if test_render.get_width() > 5:
                            self.font_large = pygame.font.SysFont(font_name, 72)
                            self.font_medium = pygame.font.SysFont(font_name, 36)
                            self.font_small = pygame.font.SysFont(font_name, 24)
                            return
                    except:
                        continue
        except:
            pass
        
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
    def draw_start_screen(self):
        self.screen.fill((30, 30, 50))
        
        title = self.font_large.render("切水果游戏", True, (255, 100, 100))
        title_rect = title.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title, title_rect)
        
        instructions = [
            "游戏说明：",
            "1. 按住鼠标滑动可以切水果",
            "2. 切到水果得分，切到一个得1分",
            "3. 一次切到多个水果，有多少算多少（最多3分）",
            "4. 切到炸弹，游戏结束！",
            "5. 游戏时间30秒，时间结束游戏也结束",
            "6. 水果包括：苹果、香蕉、菠萝"
        ]
        
        y_offset = 180
        for inst in instructions:
            text = self.font_small.render(inst, True, (200, 200, 200))
            self.screen.blit(text, (100, y_offset))
            y_offset += 40
            
        button_text = "开始游戏"
        button_color = (100, 200, 100)
        button_hover = (150, 255, 150)
        
        button_rect = pygame.Rect(self.width // 2 - 100, 480, 200, 60)
        
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            current_color = button_hover
        else:
            current_color = button_color
            
        pygame.draw.rect(self.screen, current_color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (50, 150, 50), button_rect, 3, border_radius=10)
        
        text_surface = self.font_medium.render(button_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return button_rect
        
    def draw_game_ui(self, score, time_left, cut_count, missed_count):
        score_text = f"得分: {score}"
        score_surface = self.font_medium.render(score_text, True, (255, 255, 255))
        self.screen.blit(score_surface, (20, 20))
        
        time_text = f"时间: {int(time_left)}秒"
        time_surface = self.font_medium.render(time_text, True, (255, 255, 255))
        time_rect = time_surface.get_rect(center=(self.width // 2, 40))
        self.screen.blit(time_surface, time_rect)
        
        if time_left <= 10:
            warning_text = self.font_medium.render(time_text, True, (255, 100, 100))
            self.screen.blit(warning_text, time_rect)
            
    def draw_game_over_screen(self, score, cut_count, missed_count, total_time):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("游戏结束", True, (255, 100, 100))
        title_rect = title.get_rect(center=(self.width // 2, 120))
        self.screen.blit(title, title_rect)
        
        results = [
            f"最终得分: {score}",
            f"切到水果: {cut_count} 个",
            f"没切到水果: {missed_count} 个",
            f"总用时: {total_time:.1f} 秒"
        ]
        
        y_offset = 220
        for result in results:
            text = self.font_medium.render(result, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 60
            
        button_text = "再来一局"
        button_color = (100, 200, 100)
        button_hover = (150, 255, 150)
        
        button_rect = pygame.Rect(self.width // 2 - 100, 480, 200, 60)
        
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            current_color = button_hover
        else:
            current_color = button_color
            
        pygame.draw.rect(self.screen, current_color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (50, 150, 50), button_rect, 3, border_radius=10)
        
        text_surface = self.font_medium.render(button_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return button_rect
