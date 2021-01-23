from abc import abstractmethod  # импортируем библиотеки
import csv
import pygame
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QTableWidgetItem
from PyQt5 import uic
import sqlite3

DISPLAY_SIZE = (1200, 900)  # размеры окна
JUMP_POWER = 5
GRAVITY = 0.35


class App:
    """Основной класс игры, в котором содержится игровой цикл"""

    def __init__(self, display_size):
        self.state = None

        pygame.init()
        self._screen = pygame.display.set_mode(display_size)
        self._display_size = display_size

        self._running = True
        self._clock = pygame.time.Clock()

    def set_state(self, state):
        self.state = state
        self.state.set_app(self)
        self.state.setup()

    def get_screen(self):
        return self._screen

    def get_display_size(self):
        return self._display_size

    def run(self):  # игровой цикл
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                self.state.process_event(event)

            dt = self._clock.tick()
            self.state.loop(dt)
            pygame.display.flip()
        self.state.destroy()


class AppState:

    def __init__(self):
        self._app = None

    def set_app(self, app):
        self._app = app

    def get_app(self):
        return self._app

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def process_event(self, event):
        pass

    @abstractmethod
    def loop(self, dt):
        pass

    @abstractmethod
    def destroy(self):
        pass


class WindowResults(QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi('data/database_results.ui', self)
        self._init_ui()

    def _init_ui(self):
        self.setGeometry(500, 500, 577, 300)
        self.setWindowTitle('Просмотр результатов')

        self.con = sqlite3.connect("data/fire_and_water_db.db")
        cur = self.con.cursor()
        result_header = cur.execute('PRAGMA table_info(results)').fetchall()
        result_header1 = list()
        result_header1.append(result_header[0][1])
        result_header1.append(result_header[1][1])
        result_header1.append(result_header[2][1])
        result_header1.append(result_header[3][1])
        result_header1.append(result_header[4][1])
        result = cur.execute(f"SELECT * FROM results").fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(result_header1)
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))


class WindowFinish(QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi('data/database_finish.ui', self)
        self._init_ui()

    def _init_ui(self):
        self.setGeometry(500, 500, 577, 300)
        self.setWindowTitle('Внесение данных в БД')

        self.pushButton.clicked.connect(self._btn_clicked)

        self.level = None
        self.time = None
        self.gems = None

    def set_information(self, level, time, gems):
        self.level = level
        self.time = time
        self.gems = gems

    def _btn_clicked(self):
        self.con = sqlite3.connect("data/fire_and_water_db.db")
        cur = self.con.cursor()

        cur.execute(f"INSERT INTO results(name, level, time, gems) "
                    f"VALUES('{self.lineEdit.text()}', {self.level}, '{self.time} сек', {self.gems})").fetchall()
        result_header = cur.execute('PRAGMA table_info(results)').fetchall()
        result_header1 = list()
        result_header1.append(result_header[0][1])
        result_header1.append(result_header[1][1])
        result_header1.append(result_header[2][1])
        result_header1.append(result_header[3][1])
        result_header1.append(result_header[4][1])
        result = cur.execute(f"SELECT * FROM results").fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(result_header1)
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))


class MenuState(AppState):
    """Класс главного меню"""

    def __init__(self):
        super().__init__()

        all_sprites.empty()
        main_group.empty()

        self._bg_img = imgs['background']
        self._text = ['Привет!',
                      'Ты попал в игру "огонь и вода"',
                      'Правила игры: управлять девочкой можно клавишами A, W, D; ',
                      'мальчиком можно управлять стрелками.',
                      'Если смешать огонь и воду или огонь/воду с зелёной жидкостью, ',
                      'то Вы проиграете.',
                      'В игре есть 2 уровня, чтбы начать нажмите на одну из кнопок. Удачи!']

    def setup(self):
        self._bg_img = pygame.transform.scale(self._bg_img, self.get_app().get_display_size())

    def process_event(self, event):  # обрабатываем события
        if event.type == pygame.MOUSEBUTTONDOWN and 440 > event.pos[0] > 240 and 750 > event.pos[1] > 650:
            self.get_app().set_state(Level1())  # "открываем" первый уровень
        if event.type == pygame.MOUSEBUTTONDOWN and 980 > event.pos[0] > 780 and 750 > event.pos[1] > 650:
            self.get_app().set_state(Level2())  # "открываем" второй уровень
        if event.type == pygame.MOUSEBUTTONDOWN and 700 > event.pos[0] > 500 and 750 > event.pos[1] > 650:
            app = QApplication(sys.argv)  # "открываем" окно с результатами игроков

            window = WindowResults()
            window.show()

            app.exec()

    def loop(self, dt):  # происходит загрзука, отрисовка всех элементов, находящихся в меню
        screen = self.get_app().get_screen()
        screen.fill((0, 0, 0))
        screen.blit(self._bg_img, (0, 0))
        font = pygame.font.Font(None, 35)

        for i, line in enumerate(self._text):
            if i > 1:
                font = pygame.font.Font(None, 30)
                line_img = font.render(line, True, (123, 104, 238))
                screen.blit(line_img, (0, i * line_img.get_rect().height * 1.4))
                continue
            line_img = font.render(line, True, (123, 104, 238))
            screen.blit(line_img, (0, i * line_img.get_rect().height * 1.1))

        pygame.draw.rect(screen, (123, 104, 238), (240, 650, 200, 100))
        pygame.draw.rect(screen, (123, 104, 238), (780, 650, 200, 100))
        pygame.draw.rect(screen, (123, 104, 238), (500, 650, 200, 100))
        font = pygame.font.Font(None, 50)
        screen.blit(font.render('1 уровень', True, (100, 255, 100)), (255, 675))
        screen.blit(font.render('2 уровень', True, (100, 255, 100)), (795, 675))
        font = pygame.font.Font(None, 25)
        screen.blit(font.render('Посмотреть результаты', True, (100, 255, 100)), (501, 690))

    def destroy(self):
        pass


class LevelCompleted(AppState):
    """Состояние, отображаемое при удачном завершении игры"""

    def __init__(self, red_gem_amount, blue_gem_amount, time, level):
        super().__init__()

        all_sprites.empty()
        main_group.empty()

        self._bg_img = imgs['background2']
        self._time = time
        self._red_gem_amount = red_gem_amount
        self._blue_gem_amount = blue_gem_amount
        self._level = level
        self._text = f'Поздравляем, вы прошли уровень {self._level}!' \
                     f'\nВаше время: {self._time} сек\nСобранные алмазы:\n\n\nИграть заново?'.split('\n')

    def setup(self):
        self._bg_img = pygame.transform.scale(self._bg_img, self.get_app().get_display_size())
        screen = self.get_app().get_screen()
        screen.fill((0, 0, 0))
        screen.blit(self._bg_img, (0, 0))
        font = pygame.font.Font(None, 70)
        for i, line in enumerate(self._text):
            if i > 1:
                font = pygame.font.Font(None, 70)
                line_img = font.render(line, True, (255, 255, 255))
                screen.blit(line_img, (0, i * line_img.get_rect().height * 1.4))
                continue
            line_img = font.render(line, True, (255, 255, 255))
            screen.blit(line_img, (0, i * line_img.get_rect().height * 1.1))

        gem_coords = [15, 200]
        for _ in range(3):
            if self._red_gem_amount > 0:
                self._red_gem_amount -= 1
                gem = pygame.image.load('data/red_gem.png')
                screen.blit(gem, gem_coords)
            else:
                gem = pygame.image.load('data/grey_gem.png')
                screen.blit(gem, gem_coords)
            gem_coords[0] += 60

        gem_coords = [15, 250]
        for _ in range(3):
            if self._blue_gem_amount > 0:
                self._blue_gem_amount -= 1
                gem = pygame.image.load('data/blue_gem.png')
                screen.blit(gem, gem_coords)
            else:
                gem = pygame.image.load('data/grey_gem.png')
                screen.blit(gem, gem_coords)
            gem_coords[0] += 60

        pygame.draw.rect(screen, (123, 104, 238), (25, 450, 350, 200))
        pygame.draw.rect(screen, (123, 104, 238), (425, 450, 350, 200))
        pygame.draw.rect(screen, (123, 104, 238), (825, 450, 350, 200))
        pygame.draw.rect(screen, (123, 104, 238), (425, 680, 350, 200))

        font = pygame.font.Font(None, 100)
        screen.blit(font.render('1 уровень', True, (100, 255, 100)), (30, 500))
        screen.blit(font.render('Меню', True, (100, 255, 100)), (500, 500))
        screen.blit(font.render('2 уровень', True, (100, 255, 100)), (830, 500))
        font = pygame.font.Font(None, 70)
        screen.blit(font.render('Внести', True, (100, 255, 100)), (515, 680))
        screen.blit(font.render('результаты в', True, (100, 255, 100)), (450, 730))
        screen.blit(font.render('базу данных', True, (100, 255, 100)), (450, 780))

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and 375 > event.pos[0] > 25 and 650 > event.pos[1] > 450:  # 1 уровень
            self.get_app().set_state(Level1())
        if event.type == pygame.MOUSEBUTTONDOWN and 775 > event.pos[0] > 425 and 650 > event.pos[1] > 450:  # Меню
            self.get_app().set_state(MenuState())
        if event.type == pygame.MOUSEBUTTONDOWN and 1175 > event.pos[0] > 825 and 650 > event.pos[1] > 450:  # 2 уровень
            self.get_app().set_state(Level2())
        if event.type == pygame.MOUSEBUTTONDOWN and 775 > event.pos[0] > 425 and 880 > event.pos[1] > 680:  # внесение
            app = QApplication(sys.argv)  # данных в БД

            window = WindowFinish()
            window.set_information(int(self._level), str(self._time), self._red_gem_amount + self._blue_gem_amount)
            window.show()

            app.exec()

    def loop(self, dt):
        pass


class LevelFailed(AppState):
    """Состояние, отображаемое при неудачном завершении игры"""

    def __init__(self, level):
        super().__init__()

        all_sprites.empty()
        main_group.empty()

        self._bg_img = imgs['background2']
        self._level = level
        self._text = f'К сожалению, вы не прошли уровень {self._level}\nСыграть заново?\n\n\n'.split('\n')

    def setup(self):
        self._bg_img = pygame.transform.scale(self._bg_img, self.get_app().get_display_size())
        screen = self.get_app().get_screen()
        screen.fill((0, 0, 0))
        screen.blit(self._bg_img, (0, 0))
        font = pygame.font.Font(None, 70)
        for i, line in enumerate(self._text):
            if i > 1:
                font = pygame.font.Font(None, 70)
                line_img = font.render(line, True, (255, 255, 255))
                screen.blit(line_img, (0, i * line_img.get_rect().height * 1.4))
                continue
            line_img = font.render(line, True, (255, 255, 255))
            screen.blit(line_img, (0, i * line_img.get_rect().height * 1.1))

        pygame.draw.rect(screen, (123, 104, 238), (25, 200, 350, 200))
        pygame.draw.rect(screen, (123, 104, 238), (425, 200, 350, 200))
        pygame.draw.rect(screen, (123, 104, 238), (825, 200, 350, 200))

        font = pygame.font.Font(None, 100)
        screen.blit(font.render('1 уровень', True, (100, 255, 100)), (30, 250))
        screen.blit(font.render('Меню', True, (100, 255, 100)), (500, 250))
        screen.blit(font.render('2 уровень', True, (100, 255, 100)), (830, 250))

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and 375 > event.pos[0] > 25 and 400 > event.pos[1] > 200:  # 1 уровень
            self.get_app().set_state(Level1())
        if event.type == pygame.MOUSEBUTTONDOWN and 775 > event.pos[0] > 425 and 400 > event.pos[1] > 200:  # Меню
            self.get_app().set_state(MenuState())
        if event.type == pygame.MOUSEBUTTONDOWN and 1175 > event.pos[0] > 825 and 400 > event.pos[1] > 200:  # 2 уровень
            self.get_app().set_state(Level2())


class GameState(AppState):

    def __init__(self):
        super().__init__()

        self._start_ticks = pygame.time.get_ticks()
        self._seconds = 0
        self._font = pygame.font.Font(None, 50)

        self.red_gem_amount = 0
        self.blue_gem_amount = 0

        self.doors_opened = 0

    def setup(self):
        pass

    def process_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.get_app().set_state(MenuState())

    def loop(self, dt):
        self.doors_opened = 0
        screen = self.get_app().get_screen()

        tiles_group.draw(screen)

        all_sprites.update(pygame.key.get_pressed(), dt)
        all_sprites.draw(screen)

        main_group.update(pygame.key.get_pressed(), dt)
        main_group.draw(screen)

        self._seconds = (pygame.time.get_ticks() - self._start_ticks) // 1000
        pygame.draw.rect(screen, (32, 29, 14), (500, 0, 200, 50))
        screen.blit(self._font.render(f'0{str(self._seconds)}:00', True, (112, 102, 50)), (550, 10))

        for object in all_sprites:
            if object.get_type() == 'fire_door' and object.door_opened is True:
                self.doors_opened += 1
            elif object.get_type() == 'water_door' and object.door_opened is True:
                self.doors_opened += 1

    def add_gem(self, color):
        if color == 'red':
            self.red_gem_amount += 1
        else:
            self.blue_gem_amount += 1


class Level1(GameState):
    """Класс первого уровня"""

    def __init__(self):
        super().__init__()
        generate_level(load_level('data/level1.txt'), load_sprties('data/sprites_level1.txt'))

        self._failed = False

    def loop(self, dt):
        super(Level1, self).loop(dt)

        if self.doors_opened == 2:
            app.set_state(LevelCompleted(self.red_gem_amount, self.blue_gem_amount, self._seconds, 1))
        if self._failed:
            app.set_state(LevelFailed(1))


class Level2(GameState):
    """Класс второго уровня"""

    def __init__(self):
        super().__init__()
        generate_level(load_level('data/level2.txt'), load_sprties('data/sprites_level2.txt'))
        self.level = 2

        self._failed = False

    def loop(self, dt):
        super(Level2, self).loop(dt)
        if self.doors_opened == 2:
            app.set_state(LevelCompleted(self.red_gem_amount, self.blue_gem_amount, self._seconds, 2))
        if self._failed:
            app.set_state(LevelFailed(2))


class Tile(pygame.sprite.Sprite):
    """Класс тайлов"""

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__()
        self.tile_type = tile_type
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(60 * pos_x, 30 * pos_y)
        self.mask = pygame.mask.from_surface(self.image)

        self.coords = (pos_x, pos_y)


class Object(pygame.sprite.Sprite):
    """Класс объектов"""

    def __init__(self, object_type, pos_x, pos_y):
        super().__init__()
        self._type = object_type
        self.image = object_images[self._type]
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)

    def intersection(self, type):
        pass

    def get_type(self):
        return self._type


class Gem(Object):
    """Класс алмазов"""

    def __init__(self, gem_type, pos_x, pos_y):
        super().__init__(gem_type, pos_x, pos_y)

    def intersection(self, type):
        if self._type == 'red_gem' and type == 'fire':
            app.state.add_gem('red')
            self.kill()
        elif self._type == 'blue_gem' and type == 'water':
            app.state.add_gem('blue')
            self.kill()


class Door(Object):
    """Класс дверей"""

    def __init__(self, door_type, pos_x, pos_y):
        super().__init__(door_type, pos_x, pos_y)
        self.door_opened = False

    def intersection(self, type):
        if (type == 'fire' and self._type == 'fire_door') or (type == 'water' and self._type == 'water_door'):
            self.image = object_images['open_door']
            self.door_opened = True

    def close(self, type):
        if type == 'fire' and self._type == 'fire_door':
            self.image = object_images['fire_door']
        elif type == 'water' and self._type == 'water_door':
            self.image = object_images['water_door']


class Puddle(Object):
    """Класс луж"""

    def __init__(self, puddle_type, pos_x, pos_y):
        super().__init__(puddle_type, pos_x, pos_y)

    def intersection(self, type):
        if self.get_type() == 'green_puddle':
            app.state._failed = True
        elif self.get_type() == 'blue_puddle' and type == 'fire':
            app.state._failed = True
        elif self.get_type() == 'red_puddle' and type == 'water':
            app.state._failed = True


class MainSrites(pygame.sprite.Sprite):
    """Класс главных спрайтов - огня и воды"""

    def __init__(self, type, pos_x, pos_y, *group):  # type должен быть равен либо 'fire', либо 'water'
        super().__init__(*group)
        self._type = type
        self._position = [pos_x, pos_y]
        self.image = main_sprites[self._type]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.onGround = True
        self.yvel = 0

    def update(self, keys, dt):
        for i in tiles_group:
            if pygame.sprite.collide_mask(i, self) and i.tile_type == 'wall' and i.coords[1] * 30 > self._position[1]:
                self.onGround = True
                self.yvel = 0
                break
        else:
            self.onGround = False

        flag = True
        if keys[pygame.K_UP] and self._type == 'fire':
            if self.onGround:
                self.yvel += -JUMP_POWER
        if keys[pygame.K_w] and self._type == 'water':
            if self.onGround:
                self.yvel += -JUMP_POWER
        if not self.onGround:
            self.yvel += GRAVITY
        self._position[1] += self.yvel
        if any([i for i in keys]):
            for i in tiles_group:
                if pygame.sprite.collide_mask(i, self) and i.tile_type == 'wall' and \
                        i.coords[1] * 30 < self._position[1] and \
                        ((keys[pygame.K_UP] and self._type == 'fire') or (keys[pygame.K_w] and self._type == 'water')):
                    self._position[1] += self.yvel
                    flag = False
        if keys[pygame.K_LEFT] and self._type == 'fire':
            self.image = main_sprites['fire_left']
            self.mask = pygame.mask.from_surface(self.image)
            self._position[0] -= 10 * dt / 100
        if keys[pygame.K_a] and self._type == 'water':
            self.image = main_sprites['water_left']
            self.mask = pygame.mask.from_surface(self.image)
            self._position[0] -= 10 * dt / 100
        if any([i for i in keys]):
            for i in tiles_group:
                if pygame.sprite.collide_mask(i, self) and i.tile_type == 'wall' and \
                        i.coords[0] * 30 < self._position[0] and i.coords[1] * 30 < self._position[1] and \
                        ((keys[pygame.K_LEFT] and self._type == 'fire') or (keys[pygame.K_a] and self._type == 'water')):
                    print(i.coords[0] * 30, self._position[0])
                    self._position[0] += 10 * dt / 100
                    flag = False
        if keys[pygame.K_RIGHT] and self._type == 'fire':
            self.image = main_sprites['fire_right']
            self.mask = pygame.mask.from_surface(self.image)
            self._position[0] += 10 * dt / 100
        if keys[pygame.K_d] and self._type == 'water':
            self.image = main_sprites['water_right']
            self.mask = pygame.mask.from_surface(self.image)
            self._position[0] += 10 * dt / 100
        if any([i for i in keys]):
            for i in tiles_group:
                if pygame.sprite.collide_mask(i, self) and i.tile_type == 'wall' and \
                        i.coords[0] * 30 > self._position[0] and \
                        ((keys[pygame.K_RIGHT] and self._type == 'fire') or (keys[pygame.K_d] and self._type == 'water')):
                    self._position[0] -= 10 * dt / 100
                    flag = False

        if not any([i for i in keys]):
            self.image = main_sprites[self._type]
            self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = self._position

        for object in all_sprites:
            if object.get_type() == 'water_door' or object.get_type() == 'fire_door':
                object.close(self._type)
            if pygame.sprite.collide_mask(self, object):
                object.intersection(self._type)


def load_image(image_path, colorkey=None):
    result = pygame.image.load(image_path)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = result.get_at((0, 0))
        result.set_colorkey(colorkey)
    else:
        result.convert_alpha()
    return result


def load_sprties(filename):
    # читаем спрайты уровня, представленные в виде csv-твблицы (тип_спрайта;координата_х;координата_у;)
    with open(filename, encoding="utf8") as sprites_file:
        reader = csv.reader(sprites_file,
                            delimiter=';', quotechar='"')
        return list(reader)


def load_level(filename):
    filename = filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    return level_map


def generate_level(level, sprites):
    x, y = None, None
    # создаем уровень по тайлам
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == ' ':
                tiles_group.add(Tile('empty', x, y))
            elif level[y][x] == '-':
                tiles_group.add(Tile('wall', x, y))

    # создаем спрайты уровня
    for line in sprites:
        if line[0] == 'water' or line[0] == 'fire':
            main_group.add(MainSrites(line[0], int(line[1]), int(line[2])))
        elif line[0] == 'red_gem' or line[0] == 'blue_gem':
            all_sprites.add(Gem(line[0], int(line[1]), int(line[2])))
        elif line[0] == 'fire_door' or line[0] == 'water_door':
            all_sprites.add(Door(line[0], int(line[1]), int(line[2])))
        elif line[0] == 'red_puddle' or line[0] == 'blue_puddle' or line[0] == 'green_puddle':
            all_sprites.add(Puddle(line[0], int(line[1]), int(line[2])))


if __name__ == '__main__':
    app = App(DISPLAY_SIZE)

    imgs = {'background': load_image('data/fire_and_water.jpg'),
            'background2': load_image('data/game_bg.png')}

    tile_images = {
        'wall': load_image('data/light_tile.png'),
        'empty': load_image('data/dark_tile.png')}

    object_images = {'blue_puddle': load_image('data/blue_puddle.png'),
                     'red_puddle': load_image('data/red_puddle.png'),
                     'green_puddle': load_image('data/green_puddle.png'),
                     'water_door': load_image('data/water_door.png'),
                     'fire_door': load_image('data/fire_door.png'),
                     'open_door': load_image('data/open_door.png'),
                     'blue_gem': load_image('data/blue_gem.png'),
                     'red_gem': load_image('data/red_gem.png'),
                     'grey_gem': load_image('data/grey_gem.png')}

    main_sprites = {'fire': load_image('data/fire_sprite.png'),
                    'water': load_image('data/water_sprite.png'),
                    'fire_right': load_image('data/fire_sprite_right.png'),
                    'fire_left': load_image('data/fire_sprite_left.png'),
                    'water_right': load_image('data/water_sprite_right.png'),
                    'water_left': load_image('data/water_sprite_left.png')}

    all_sprites = pygame.sprite.Group()
    main_group = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()

    menu_state = MenuState()
    app.set_state(menu_state)
    app.run()
