#!/usr/bin/env python3
"""
Игра с шариками - Цветовое смешивание
Запуск основного игрового интерфейса
"""

from game import BallGame

if __name__ == "__main__":
    print("Запуск игры с шариками...")
    print("Управление:")
    print("- ЛКМ: захватить/отпустить шарик")
    print("- R: перезапуск игры")
    print("- ПРОБЕЛ: добавить новый шарик")
    print("- ESC: выход из игры")
    print("- Перетащите шарик в красную зону для удаления")
    print("- Перетащите шарик в зеленую зону для помещения в инвентарь")
    print()
    
    try:
        game = BallGame()
        game.run()
    except KeyboardInterrupt:
        print("\nИгра завершена пользователем")
    except Exception as e:
        print(f"Ошибка при запуске игры: {e}")
        print("Убедитесь, что установлен pygame: pip install pygame")