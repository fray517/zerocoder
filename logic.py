import math
import random
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum


class BallState(Enum):
    """Состояния шарика"""
    FREE = "free"  # Свободно движется по экрану
    IN_INVENTORY = "in_inventory"  # В инвентаре
    BEING_DRAGGED = "being_dragged"  # Перетаскивается мышкой


@dataclass
class Color:
    """Представление цвета шарика"""
    r: int
    g: int
    b: int
    
    def __post_init__(self):
        # Ограничиваем значения от 0 до 255
        self.r = max(0, min(255, self.r))
        self.g = max(0, min(255, self.g))
        self.b = max(0, min(255, self.b))
    
    def mix_with(self, other: 'Color') -> 'Color':
        """Математическое смешивание цветов через усреднение RGB-значений"""
        return Color(
            r=int((self.r + other.r) / 2),
            g=int((self.g + other.g) / 2),
            b=int((self.b + other.b) / 2)
        )
    
    def get_brightness(self) -> float:
        """Получить яркость цвета (0-1)"""
        return (self.r + self.g + self.b) / (3 * 255)
    
    def is_white(self) -> bool:
        """Проверка, является ли цвет белым"""
        return self.r > 200 and self.g > 200 and self.b > 200
    
    def get_saturation(self) -> float:
        """Получить насыщенность цвета (0-1)"""
        max_component = max(self.r, self.g, self.b)
        min_component = min(self.r, self.g, self.b)
        return (max_component - min_component) / 255 if max_component > 0 else 0
    
    def get_hue(self) -> float:
        """Получить оттенок цвета в градусах (0-360)"""
        r, g, b = self.r / 255.0, self.g / 255.0, self.b / 255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        if diff == 0:
            return 0  # Серый цвет
        
        if max_val == r:
            hue = 60 * ((g - b) / diff)
        elif max_val == g:
            hue = 60 * (2 + (b - r) / diff)
        else:  # max_val == b
            hue = 60 * (4 + (r - g) / diff)
        
        return (hue + 360) % 360


@dataclass
class Ball:
    """Класс шарика"""
    x: float
    y: float
    vx: float  # Скорость по X
    vy: float  # Скорость по Y
    radius: float
    color: Color
    state: BallState = BallState.FREE
    id: int = 0
    
    def __post_init__(self):
        if self.id == 0:
            self.id = random.randint(1000, 9999)


class GameLogic:
    """Основной класс логики игры"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.balls: List[Ball] = []
        self.inventory: List[Ball] = []
        self.dragged_ball: Optional[Ball] = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Зона удаления (внизу экрана)
        self.delete_zone_y = screen_height - 50
        self.delete_zone_height = 50
        
        # Физические константы
        self.friction = 0.98  # Трение
        self.bounce_damping = 0.8  # Затухание при отскоке
        self.gravity = 0.2  # Гравитация
        
        # Настройки для генерации случайных цветов
        self.min_color_value = 50   # Минимальное значение RGB компонента
        self.max_color_value = 255  # Максимальное значение RGB компонента
    
    def add_ball(self, x: float, y: float, radius: float = 20) -> Ball:
        """Добавить новый шарик в игру"""
        # Генерируем случайный цвет с хорошей яркостью
        color = self.generate_random_color(min_brightness=0.4, max_brightness=0.9)
        
        ball = Ball(
            x=x, y=y,
            vx=random.uniform(-3, 3),
            vy=random.uniform(-3, 3),
            radius=radius,
            color=color
        )
        
        self.balls.append(ball)
        return ball
    
    def generate_random_color(self, min_brightness: float = 0.3, max_brightness: float = 1.0) -> Color:
        """Генерировать случайный цвет с заданными характеристиками"""
        # Генерируем случайные RGB компоненты
        r = random.randint(self.min_color_value, self.max_color_value)
        g = random.randint(self.min_color_value, self.max_color_value)
        b = random.randint(self.min_color_value, self.max_color_value)
        
        color = Color(r, g, b)
        
        # Корректируем яркость если нужно
        current_brightness = color.get_brightness()
        if current_brightness < min_brightness or current_brightness > max_brightness:
            target_brightness = random.uniform(min_brightness, max_brightness)
            scale_factor = target_brightness / current_brightness
            
            new_r = int(color.r * scale_factor)
            new_g = int(color.g * scale_factor)
            new_b = int(color.b * scale_factor)
            
            color = Color(new_r, new_g, new_b)
        
        return color
    
    def update(self, dt: float = 1.0):
        """Обновление логики игры"""
        # Обновляем свободные шарики
        for ball in self.balls:
            if ball.state == BallState.FREE:
                self._update_ball_physics(ball, dt)
                self._check_collisions(ball)
                self._check_boundaries(ball)
        
        # Обновляем перетаскиваемый шарик
        if self.dragged_ball and self.dragged_ball.state == BallState.BEING_DRAGGED:
            # Позиция обновляется в методе drag_ball
            pass
    
    def _update_ball_physics(self, ball: Ball, dt: float):
        """Обновление физики шарика"""
        # Применяем гравитацию
        ball.vy += self.gravity * dt
        
        # Обновляем позицию
        ball.x += ball.vx * dt
        ball.y += ball.vy * dt
        
        # Применяем трение
        ball.vx *= self.friction
        ball.vy *= self.friction
    
    def _check_collisions(self, ball: Ball):
        """Проверка столкновений между шариками"""
        for other in self.balls:
            if other == ball or other.state != BallState.FREE:
                continue
            
            distance = math.sqrt((ball.x - other.x)**2 + (ball.y - other.y)**2)
            min_distance = ball.radius + other.radius
            
            if distance < min_distance and distance > 0:
                # Шарики касаются - смешиваем цвета
                self._mix_ball_colors(ball, other)
                
                # Разделяем шарики, чтобы они не застряли
                overlap = min_distance - distance
                separation_x = (ball.x - other.x) / distance * overlap * 0.5
                separation_y = (ball.y - other.y) / distance * overlap * 0.5
                
                ball.x += separation_x
                ball.y += separation_y
                other.x -= separation_x
                other.y -= separation_y
    
    def _mix_ball_colors(self, ball1: Ball, ball2: Ball):
        """Математическое смешивание цветов при касании шариков"""
        # Смешиваем цвета через усреднение RGB-значений
        mixed_color = ball1.color.mix_with(ball2.color)
        
        # Оба шарика получают одинаковый смешанный цвет
        ball1.color = mixed_color
        ball2.color = mixed_color
    
    def _check_boundaries(self, ball: Ball):
        """Проверка границ экрана"""
        # Отскок от стен
        if ball.x - ball.radius < 0:
            ball.x = ball.radius
            ball.vx = abs(ball.vx) * self.bounce_damping
        elif ball.x + ball.radius > self.screen_width:
            ball.x = self.screen_width - ball.radius
            ball.vx = -abs(ball.vx) * self.bounce_damping
        
        if ball.y - ball.radius < 0:
            ball.y = ball.radius
            ball.vy = abs(ball.vy) * self.bounce_damping
        elif ball.y + ball.radius > self.screen_height:
            ball.y = self.screen_height - ball.radius
            ball.vy = -abs(ball.vy) * self.bounce_damping
    
    def start_drag(self, mouse_x: float, mouse_y: float) -> bool:
        """Начать перетаскивание шарика мышкой"""
        for ball in reversed(self.balls):  # Берем верхний шарик
            if ball.state == BallState.FREE:
                distance = math.sqrt((ball.x - mouse_x)**2 + (ball.y - mouse_y)**2)
                if distance <= ball.radius:
                    self.dragged_ball = ball
                    ball.state = BallState.BEING_DRAGGED
                    self.drag_offset_x = ball.x - mouse_x
                    self.drag_offset_y = ball.y - mouse_y
                    return True
        return False
    
    def drag_ball(self, mouse_x: float, mouse_y: float):
        """Перетаскивание шарика мышкой"""
        if self.dragged_ball and self.dragged_ball.state == BallState.BEING_DRAGGED:
            self.dragged_ball.x = mouse_x + self.drag_offset_x
            self.dragged_ball.y = mouse_y + self.drag_offset_y
    
    def end_drag(self, mouse_x: float, mouse_y: float) -> bool:
        """Завершить перетаскивание шарика"""
        if not self.dragged_ball:
            return False
        
        ball = self.dragged_ball
        
        # Проверяем, попал ли шарик в зону удаления
        if self._is_in_delete_zone(mouse_x, mouse_y):
            self._delete_ball(ball)
            self.dragged_ball = None
            return True
        
        # Проверяем, попал ли шарик в инвентарь (например, в правый верхний угол)
        inventory_x = self.screen_width - 100
        inventory_y = 50
        inventory_radius = 30
        
        distance_to_inventory = math.sqrt((mouse_x - inventory_x)**2 + (mouse_y - inventory_y)**2)
        
        if distance_to_inventory <= inventory_radius:
            # Помещаем шарик в инвентарь
            self._add_to_inventory(ball)
            self.dragged_ball = None
            return True
        else:
            # Возвращаем шарик в игру
            ball.state = BallState.FREE
            # Добавляем небольшую скорость в направлении движения мыши
            ball.vx = (mouse_x - ball.x) * 0.1
            ball.vy = (mouse_y - ball.y) * 0.1
            self.dragged_ball = None
            return False
    
    def _is_in_delete_zone(self, x: float, y: float) -> bool:
        """Проверка, находится ли точка в зоне удаления"""
        return y >= self.delete_zone_y and y <= self.delete_zone_y + self.delete_zone_height
    
    def _add_to_inventory(self, ball: Ball):
        """Добавить шарик в инвентарь"""
        ball.state = BallState.IN_INVENTORY
        self.balls.remove(ball)
        self.inventory.append(ball)
    
    def _delete_ball(self, ball: Ball):
        """Удалить шарик из игры"""
        if ball in self.balls:
            self.balls.remove(ball)
        if ball in self.inventory:
            self.inventory.remove(ball)
    
    def eject_ball_from_inventory(self, inventory_index: int) -> bool:
        """Выплюнуть шарик из инвентаря обратно в игру"""
        if 0 <= inventory_index < len(self.inventory):
            ball = self.inventory.pop(inventory_index)
            ball.state = BallState.FREE
            
            # Размещаем шарик в случайном месте в верхней части экрана
            ball.x = random.uniform(50, self.screen_width - 50)
            ball.y = random.uniform(50, 150)
            
            # Добавляем случайную скорость
            ball.vx = random.uniform(-2, 2)
            ball.vy = random.uniform(-2, 2)
            
            self.balls.append(ball)
            return True
        return False
    
    def get_ball_quality_score(self, ball: Ball) -> float:
        """Получить оценку качества шарика (чем выше, тем лучше)"""
        brightness = ball.color.get_brightness()
        saturation = ball.color.get_saturation()
        
        # Белый цвет - плохой результат
        if ball.color.is_white():
            return 0.0
        
        # Серый цвет (низкая насыщенность) - плохой результат
        if saturation < 0.1:
            return 0.1
        
        # Оценка на основе яркости и насыщенности
        # Используем квадратичную зависимость для насыщенности (более яркие цвета ценятся выше)
        quality = brightness * (saturation ** 0.5)
        
        # Дополнительный бонус за сбалансированность цветов
        r, g, b = ball.color.r, ball.color.g, ball.color.b
        balance = 1.0 - abs(max(r, g, b) - min(r, g, b)) / 255.0
        quality *= (0.7 + 0.3 * balance)  # Баланс дает небольшой бонус
        
        return min(1.0, quality)
    
    def get_inventory_info(self) -> List[Dict]:
        """Получить информацию об инвентаре"""
        return [
            {
                'index': i,
                'color': (ball.color.r, ball.color.g, ball.color.b),
                'quality': self.get_ball_quality_score(ball),
                'radius': ball.radius
            }
            for i, ball in enumerate(self.inventory)
        ]
    
    def get_balls_info(self) -> List[Dict]:
        """Получить информацию о всех шариках в игре"""
        return [
            {
                'id': ball.id,
                'x': ball.x,
                'y': ball.y,
                'vx': ball.vx,
                'vy': ball.vy,
                'radius': ball.radius,
                'color': (ball.color.r, ball.color.g, ball.color.b),
                'state': ball.state.value,
                'quality': self.get_ball_quality_score(ball)
            }
            for ball in self.balls
        ]
    
    def clear_all_balls(self):
        """Очистить все шарики"""
        self.balls.clear()
        self.inventory.clear()
        self.dragged_ball = None
    
    def get_delete_zone_info(self) -> Dict:
        """Получить информацию о зоне удаления"""
        return {
            'y': self.delete_zone_y,
            'height': self.delete_zone_height,
            'width': self.screen_width
        }


# Пример использования
if __name__ == "__main__":
    # Создаем игру
    game = GameLogic(800, 600)
    
    # Демонстрация смешивания цветов
    print("=== Демонстрация математического смешивания цветов ===")
    
    # Создаем два шарика с разными цветами
    red_ball = Ball(100, 100, 0, 0, 20, Color(255, 0, 0))  # Красный
    blue_ball = Ball(200, 100, 0, 0, 20, Color(0, 0, 255))  # Синий
    
    print(f"Исходные цвета:")
    print(f"  Красный шарик: RGB({red_ball.color.r}, {red_ball.color.g}, {red_ball.color.b})")
    print(f"  Синий шарик: RGB({blue_ball.color.r}, {blue_ball.color.g}, {blue_ball.color.b})")
    
    # Смешиваем цвета
    mixed_color = red_ball.color.mix_with(blue_ball.color)
    print(f"Смешанный цвет: RGB({mixed_color.r}, {mixed_color.g}, {mixed_color.b})")
    print(f"Ожидаемый результат (среднее): RGB(127, 0, 127) - пурпурный")
    
    # Добавляем несколько шариков в игру
    print(f"\n=== Игровая симуляция ===")
    for i in range(5):
        game.add_ball(
            x=random.uniform(100, 700),
            y=random.uniform(100, 400),
            radius=random.uniform(15, 25)
        )
    
    # Симуляция игрового цикла
    for frame in range(100):
        game.update()
        
        # Выводим информацию о шариках каждые 20 кадров
        if frame % 20 == 0:
            balls_info = game.get_balls_info()
            print(f"Frame {frame}: {len(balls_info)} balls in game")
            
            for ball_info in balls_info:
                print(f"  Ball {ball_info['id']}: pos=({ball_info['x']:.1f}, {ball_info['y']:.1f}), "
                      f"color=({ball_info['color'][0]}, {ball_info['color'][1]}, {ball_info['color'][2]}), "
                      f"quality={ball_info['quality']:.2f}")
    
    print(f"\nInventory: {len(game.inventory)} balls")
    print(f"Delete zone: y={game.delete_zone_y}, height={game.delete_zone_height}")
