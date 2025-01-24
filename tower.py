import pygame
from bullet import Bullet
import math

class Tower(pygame.sprite.Sprite):
    def __init__(self, position, game):
        super().__init__()
        self.position = pygame.math.Vector2(position)
        self.game = game

        self.image = None
        self.rect = None
        self.tower_range = 0
        self.damage = 0
        self.rate_of_fire = 0
        self.last_shot_time = pygame.time.get_ticks()
        self.level = 1  # Уровень башни
        self.original_image = self.image

    def upgrade_cost(self):
        # Стоимость улучшения: 50 * текущий уровень башни
        return 50 * self.level

    def upgrade(self):
        # Улучшение башни: увеличение урона и скорострельности на 20%
        if self.game.settings.starting_money >= self.upgrade_cost():
            self.game.settings.starting_money -= self.upgrade_cost()
            self.level += 1
            self.damage = int(self.damage * 1.2)  # Увеличение урона на 20%
            self.rate_of_fire = int(self.rate_of_fire * 0.8)  # Уменьшение задержки между выстрелами на 20%
            print(f"Tower upgraded to level {self.level}. Damage: {self.damage}, Rate of Fire: {self.rate_of_fire}ms")
        else:
            print("Not enough money to upgrade the tower.")

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.is_hovered(mouse_pos):
            level_text = self.game.font.render(f"Level: {self.level}", True, (255, 255, 255))
            upgrade_cost_text = self.game.font.render(f"Upgrade: ${self.upgrade_cost()}", True, (255, 255, 255))

            level_text_pos = (self.position.x, self.position.y + 20)
            upgrade_cost_pos = (self.position.x, self.position.y + 40)

            screen.blit(level_text, level_text_pos)
            screen.blit(upgrade_cost_text, upgrade_cost_pos)

    def update(self, enemies, current_time, bullets_group):
        if current_time - self.last_shot_time > self.rate_of_fire:
            target = self.find_target(enemies)
            if target:
                self.rotate_towards_target(target)
                self.shoot(target, bullets_group)
                self.last_shot_time = current_time

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def shoot(self, target, bullets_group):
        pass

    def rotate_towards_target(self, target):
        dx = target.position.x - self.position.x
        dy = target.position.y - self.position.y
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        angle_deg = -angle_deg - 90
        self.image = pygame.transform.rotate(self.original_image, angle_deg)
        self.rect = self.image.get_rect(center=self.position)

    def find_target(self, enemies):
        nearest_enemy = None
        min_distance = float('inf')
        for enemy in enemies:
            distance = self.position.distance_to(enemy.position)
            if distance < min_distance and distance <= self.tower_range:
                nearest_enemy = enemy
                min_distance = distance
        return nearest_enemy

class BasicTower(Tower):
    def __init__(self, position, game):
        super().__init__(position, game)
        self.image = pygame.image.load('assets/towers/basic_tower.png').convert_alpha()
        self.original_image = self.image
        self.rect = self.image.get_rect(center=self.position)
        self.tower_range = 150
        self.damage = 20
        self.rate_of_fire = 1000  # Задержка между выстрелами в миллисекундах

    def shoot(self, target, bullets_group):
        new_bullet = Bullet(self.position, target.position, self.damage, self.game)
        bullets_group.add(new_bullet)
        self.game.shoot_sound.play()

class SniperTower(Tower):
    def __init__(self, position, game):
        super().__init__(position, game)
        self.image = pygame.image.load('assets/towers/sniper_tower.png').convert_alpha()
        self.image = pygame.transform.rotate(self.image, 90)
        self.original_image = self.image
        self.rect = self.image.get_rect(center=self.position)
        self.tower_range = 300
        self.damage = 40
        self.rate_of_fire = 2000  # Задержка между выстрелами в миллисекундах

    def find_target(self, enemies):
        healthiest_enemy = None
        max_health = 0
        for enemy in enemies:
            if self.position.distance_to(enemy.position) <= self.tower_range and enemy.health > max_health:
                healthiest_enemy = enemy
                max_health = enemy.health
        return healthiest_enemy

    def shoot(self, target, bullets_group):
        new_bullet = Bullet(self.position, target.position, self.damage, self.game)
        bullets_group.add(new_bullet)
        self.game.shoot_sound.play()

class MoneyTower(Tower):
    def __init__(self, position, game):
        super().__init__(position, game)
        self.image = pygame.image.load('assets/towers/towerDefense_tile203.png').convert_alpha()
        self.original_image = self.image
        self.rect = self.image.get_rect(center=self.position)
        self.money_generation_rate = 50  # Количество денег, генерируемых каждые N секунд
        self.money_generation_interval = 5000  # Интервал генерации денег в миллисекундах (5 секунд)
        self.last_money_generation_time = pygame.time.get_ticks()

    def update(self, enemies, current_time, bullets_group):
        # Генерация денег
        if current_time - self.last_money_generation_time > self.money_generation_interval:
            self.game.settings.starting_money += self.money_generation_rate
            self.last_money_generation_time = current_time
            print(f"Money generated! Current money: {self.game.settings.starting_money}")