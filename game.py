import pygame
import sys
import math
from logic import GameLogic, BallState, Color

class BallGame:
    """Основной класс игры с визуальным интерфейсом"""
    
    def __init__(self, width=1000, height=700):
        pygame.init()
        
        # Настройки экрана
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Игра с шариками - Цветовое смешивание")
        
        # Создаем игровую логику
        self.game_logic = GameLogic(width, height - 100)  # Оставляем место для UI
        
        # Настройки отрисовки
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # UI элементы
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        
        # Настройки игры
        self.initial_balls = 8  # Стартовое количество шариков
        self.is_dragging = False
        self.dragged_ball = None
        
        # Цвета UI
        self.bg_color = (255, 255, 255)  # Белый фон
        self.delete_zone_color = (255, 100, 100, 100)  # Красная зона удаления
        self.inventory_color = (100, 255, 100, 100)  # Зеленая зона инвентаря
        self.ui_bg_color = (240, 240, 240)
        self.text_color = (50, 50, 50)
        
        # Инициализация игры
        self.initialize_game()
    
    def initialize_game(self):
        """Инициализация игры с начальными шариками"""
        # Очищаем существующие шарики
        self.game_logic.clear_all_balls()
        
        # Добавляем начальные шарики
        for i in range(self.initial_balls):
            x = self.width // 2 + (i - self.initial_balls // 2) * 60
            y = 150 + (i % 3) * 80
            self.game_logic.add_ball(x, y, radius=random.uniform(18, 25))
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Перезапуск игры
                    self.initialize_game()
                elif event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    # Добавить новый шарик
                    x = random.uniform(100, self.width - 100)
                    y = random.uniform(100, 200)
                    self.game_logic.add_ball(x, y)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    self.handle_mouse_down(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Левая кнопка мыши
                    self.handle_mouse_up(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    self.handle_mouse_drag(event.pos)
        
        return True
    
    def handle_mouse_down(self, pos):
        """Обработка нажатия мыши"""
        mouse_x, mouse_y = pos
        
        # Проверяем, попал ли клик по шарику
        if self.game_logic.start_drag(mouse_x, mouse_y):
            self.is_dragging = True
            self.dragged_ball = self.game_logic.dragged_ball
    
    def handle_mouse_up(self, pos):
        """Обработка отпускания мыши"""
        if self.is_dragging:
            mouse_x, mouse_y = pos
            self.game_logic.end_drag(mouse_x, mouse_y)
            self.is_dragging = False
            self.dragged_ball = None
    
    def handle_mouse_drag(self, pos):
        """Обработка перетаскивания мыши"""
        if self.is_dragging:
            mouse_x, mouse_y = pos
            self.game_logic.drag_ball(mouse_x, mouse_y)
    
    def draw_ball(self, ball):
        """Отрисовка шарика"""
        x, y = int(ball.x), int(ball.y)
        radius = int(ball.radius)
        color = (ball.color.r, ball.color.g, ball.color.b)
        
        # Рисуем тень
        shadow_offset = 3
        pygame.draw.circle(self.screen, (100, 100, 100, 50), 
                         (x + shadow_offset, y + shadow_offset), radius)
        
        # Рисуем основной шарик
        pygame.draw.circle(self.screen, color, (x, y), radius)
        
        # Рисуем обводку
        pygame.draw.circle(self.screen, (0, 0, 0), (x, y), radius, 2)
        
        # Если шарик перетаскивается, добавляем эффект
        if ball.state == BallState.BEING_DRAGGED:
            # Пульсирующий эффект
            pulse_radius = int(radius * (1.2 + 0.1 * math.sin(pygame.time.get_ticks() * 0.01)))
            pygame.draw.circle(self.screen, (255, 255, 255, 100), (x, y), pulse_radius, 3)
    
    def draw_ui(self):
        """Отрисовка пользовательского интерфейса"""
        ui_height = 100
        ui_y = self.height - ui_height
        
        # Фон UI
        pygame.draw.rect(self.screen, self.ui_bg_color, (0, ui_y, self.width, ui_height))
        pygame.draw.line(self.screen, (200, 200, 200), (0, ui_y), (self.width, ui_y), 2)
        
        # Зона удаления (красная полоса внизу)
        delete_zone = self.game_logic.get_delete_zone_info()
        delete_rect = pygame.Rect(0, delete_zone['y'], delete_zone['width'], delete_zone['height'])
        pygame.draw.rect(self.screen, (255, 100, 100, 150), delete_rect)
        pygame.draw.rect(self.screen, (200, 50, 50), delete_rect, 3)
        
        # Текст зоны удаления
        delete_text = self.font.render("ЗОНА УДАЛЕНИЯ", True, (255, 255, 255))
        text_rect = delete_text.get_rect(center=(self.width // 2, delete_zone['y'] + delete_zone['height'] // 2))
        self.screen.blit(delete_text, text_rect)
        
        # Инвентарь (правый верхний угол)
        inventory_x = self.width - 80
        inventory_y = 20
        inventory_radius = 30
        
        pygame.draw.circle(self.screen, (100, 255, 100, 150), (inventory_x, inventory_y), inventory_radius)
        pygame.draw.circle(self.screen, (50, 200, 50), (inventory_x, inventory_y), inventory_radius, 3)
        
        # Текст инвентаря
        inv_text = self.font.render("ИНВЕНТАРЬ", True, (0, 100, 0))
        inv_rect = inv_text.get_rect(center=(inventory_x, inventory_y + 40))
        self.screen.blit(inv_text, inv_rect)
        
        # Информация о шариках в инвентаре
        inventory_info = self.game_logic.get_inventory_info()
        inv_count_text = self.font.render(f"Шариков: {len(inventory_info)}", True, self.text_color)
        self.screen.blit(inv_count_text, (inventory_x - 50, inventory_y + 60))
        
        # Информация о шариках в игре
        balls_info = self.game_logic.get_balls_info()
        game_balls_text = self.font.render(f"В игре: {len(balls_info)}", True, self.text_color)
        self.screen.blit(game_balls_text, (20, ui_y + 20))
        
        # Управление
        controls_text = [
            "УПРАВЛЕНИЕ:",
            "ЛКМ - захватить/отпустить шарик",
            "R - перезапуск",
            "ПРОБЕЛ - добавить шарик",
            "ESC - выход"
        ]
        
        for i, text in enumerate(controls_text):
            color = self.text_color if i == 0 else (100, 100, 100)
            font = self.big_font if i == 0 else self.font
            rendered_text = font.render(text, True, color)
            self.screen.blit(rendered_text, (20, ui_y + 40 + i * 20))
    
    def draw_inventory_balls(self):
        """Отрисовка шариков в инвентаре"""
        inventory_info = self.game_logic.get_inventory_info()
        inventory_x = self.width - 80
        inventory_y = 20
        
        for i, ball_info in enumerate(inventory_info):
            # Размещаем шарики в ряд под инвентарем
            ball_x = inventory_x - 60 + (i % 4) * 30
            ball_y = inventory_y + 80 + (i // 4) * 40
            
            color = ball_info['color']
            radius = int(ball_info['radius'] * 0.7)  # Уменьшенные шарики в инвентаре
            
            pygame.draw.circle(self.screen, color, (ball_x, ball_y), radius)
            pygame.draw.circle(self.screen, (0, 0, 0), (ball_x, ball_y), radius, 1)
            
            # Показываем качество шарика
            quality = ball_info['quality']
            quality_color = (0, 255, 0) if quality > 0.7 else (255, 255, 0) if quality > 0.4 else (255, 0, 0)
            pygame.draw.circle(self.screen, quality_color, (ball_x, ball_y), 3)
    
    def run(self):
        """Основной игровой цикл"""
        running = True
        
        while running:
            # Обработка событий
            running = self.handle_events()
            
            # Обновление логики игры
            self.game_logic.update(1.0 / self.fps)
            
            # Отрисовка
            self.screen.fill(self.bg_color)
            
            # Рисуем шарики
            for ball in self.game_logic.balls:
                self.draw_ball(ball)
            
            # Рисуем UI
            self.draw_ui()
            self.draw_inventory_balls()
            
            # Обновление экрана
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    import random
    game = BallGame()
    game.run()

