import pygame
from pygame.math import Vector2


class Enemy(pygame.sprite.Sprite):
    def __init__(self, path, speed=2, health=10, image_path=None, game=None, reward=10):
        """
        Инициализация врага.

        :param path: Путь, по которому движется враг.
        :param speed: Скорость врага.
        :param health: Здоровье врага.
        :param image_path: Путь к изображению врага.
        :param game: Ссылка на главный объект игры.
        :param reward: Награда за уничтожение врага.
        """
        super().__init__()
        self.image = pygame.Surface((30, 40))
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.game = game
        self.path = path
        self.path_index = 0
        self.speed = speed
        self.health = health
        self.position = Vector2(path[0])
        self.rect.center = self.position
        self.reward = reward  # Награда за уничтожение врага

    def take_damage(self, amount):
        """
        Нанесение урона врагу.

        :param amount: Количество урона.
        """
        self.health -= amount
        if self.health <= 0:
            self.game.settings.starting_money += self.reward  # Начисление денег при уничтожении
            self.kill()

    def update(self):
        """
        Обновление состояния врага.
        """
        if self.path_index < len(self.path) - 1:
            start_point = Vector2(self.path[self.path_index])
            end_point = Vector2(self.path[self.path_index + 1])
            direction = (end_point - start_point).normalize()

            self.position += direction * self.speed
            self.rect.center = self.position

            if self.position.distance_to(end_point) < self.speed:
                self.path_index += 1

            if self.path_index >= len(self.path) - 1:
                self.game.game_over()
                self.kill()
