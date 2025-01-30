import pygame
from enemy import Enemy
from tower import BasicTower, SniperTower, MoneyTower


class Level:
    def __init__(self, game):
        self.game = game
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        # Определение волн врагов с разными характеристиками
        self.waves = [
            # Первая волна: быстрые, но слабые враги
            [{'path': self.game.settings.enemy_path, 'speed': 3, 'health': 50,
              'image_path': 'assets/enemies/fast_enemy.png', 'reward': 10}] * 10,

            # Вторая волна: медленные, но сильные враги
            [{'path': self.game.settings.enemy_path, 'speed': 1, 'health': 200,
              'image_path': 'assets/enemies/strong_enemy.png', 'reward': 30}] * 5,

            # Третья волна: смешанная волна
            [{'path': self.game.settings.enemy_path, 'speed': 2, 'health': 100,
              'image_path': 'assets/enemies/basic_enemy.png', 'reward': 20}] * 8,
        ]

        self.current_wave = 0  # Текущая волна
        self.spawned_enemies = 0  # Количество уже созданных врагов в текущей волне
        self.spawn_delay = 1000  # Задержка между появлением врагов (в миллисекундах)
        self.last_spawn_time = pygame.time.get_ticks()  # Время последнего появления врага
        self.all_waves_complete = False  # Флаг завершения всех волн
        self.font = pygame.font.SysFont("Arial", 24)  # Шрифт для отображения текста
        self.enemy_spawn_sound = pygame.mixer.Sound('assets/sounds/enemy_hit.wav')  # Звук появления врага
        self.start_next_wave()  # Запуск первой волны

    def start_next_wave(self):
        """
        Запуск следующей волны врагов.
        """
        if self.current_wave < len(self.waves):
            self.spawned_enemies = 0
            self.spawn_next_enemy()

    def spawn_next_enemy(self):
        """
        Создание следующего врага в текущей волне.
        """
        if self.spawned_enemies < len(self.waves[self.current_wave]):
            enemy_info = self.waves[self.current_wave][self.spawned_enemies]
            new_enemy = Enemy(**enemy_info, game=self.game)
            self.enemies.add(new_enemy)
            self.spawned_enemies += 1
            self.enemy_spawn_sound.play()

    def attempt_place_tower(self, mouse_pos, tower_type):
        """
        Попытка разместить башню на карте.

        :param mouse_pos: Позиция мыши.
        :param tower_type: Тип башни (basic, sniper, money).
        """
        tower_classes = {
            'basic': BasicTower,
            'sniper': SniperTower,
            'money': MoneyTower,
        }
        if tower_type in tower_classes and self.game.settings.starting_money >= self.game.settings.tower_cost:
            grid_pos = self.game.grid.get_grid_position(mouse_pos)
            if self.game.grid.is_spot_available(grid_pos):
                self.game.settings.starting_money -= self.game.settings.tower_cost
                new_tower = tower_classes[tower_type](grid_pos, self.game)
                self.towers.add(new_tower)
                print("Tower placed.")
            else:
                print("Invalid position for tower.")
        else:
            print("Not enough money or unknown tower type.")

    def update(self):
        """
        Обновление состояния уровня.
        """
        current_time = pygame.time.get_ticks()

        # Создание новых врагов, если текущая волна не завершена
        if self.current_wave < len(self.waves) and self.spawned_enemies < len(self.waves[self.current_wave]):
            if current_time - self.last_spawn_time > self.spawn_delay:
                enemy_info = self.waves[self.current_wave][self.spawned_enemies].copy()
                enemy_info['game'] = self.game
                new_enemy = Enemy(**enemy_info)
                self.enemies.add(new_enemy)
                self.spawned_enemies += 1
                self.last_spawn_time = current_time
                self.enemy_spawn_sound.play()

        # Обработка столкновений пуль с врагами
        collisions = pygame.sprite.groupcollide(self.bullets, self.enemies, True, False)
        for bullet in collisions:
            for enemy in collisions[bullet]:
                enemy.take_damage(bullet.damage)

        # Обновление состояния врагов, башен и пуль
        self.enemies.update()
        for tower in self.towers:
            tower.update(self.enemies, current_time, self.bullets)
        self.bullets.update()

        # Переход к следующей волне, если все враги уничтожены
        if len(self.enemies) == 0 and self.current_wave < len(self.waves) - 1:
            self.current_wave += 1
            self.start_next_wave()
        elif len(self.enemies) == 0 and self.current_wave == len(self.waves) - 1:
            self.all_waves_complete = True

    def draw_path(self, screen):
        """
        Отрисовка пути врагов и позиций для башен.

        :param screen: Экран, на котором отрисовывается путь.
        """
        pygame.draw.lines(screen, (0, 128, 0), False, self.game.settings.enemy_path, 5)
        for pos in self.game.settings.tower_positions:
            pygame.draw.circle(screen, (128, 0, 0), pos, 10)

    def draw(self, screen):
        """
        Отрисовка всех элементов уровня.

        :param screen: Экран, на котором отрисовываются элементы.
        """
        self.draw_path(screen)
        self.enemies.draw(screen)
        self.towers.draw(screen)
        self.bullets.draw(screen)
        mouse_pos = pygame.mouse.get_pos()
        for tower in self.towers:
            tower.draw(screen)
            if tower.is_hovered(mouse_pos):
                tower_stats_text = self.font.render(f"Damage: {tower.damage}, Range: {tower.tower_range}", True,
                                                    (255, 255, 255))
                screen.blit(tower_stats_text, (tower.rect.x, tower.rect.y - 20))
