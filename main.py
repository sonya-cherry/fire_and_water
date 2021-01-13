from abc import abstractmethod  # импортируем библиотеки
import csv
import pygame

DISPLAY_SIZE = (1200, 900)  # размеры окна


class App:
    """Основной класс игры, в котором содержится игровой цикл"""

    def __init__(self, display_size):
        self._state = None

        pygame.init()
        self._screen = pygame.display.set_mode(display_size)
        self._display_size = display_size

        self._running = True
        self._clock = pygame.time.Clock()

    def set_state(self, state):
        self._state = state
        self._state.set_app(self)
        self._state.setup()

    def get_screen(self):
        return self._screen

    def get_display_size(self):
        return self._display_size

    def run(self):  # игровой цикл
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                self._state.process_event(event)

            dt = self._clock.tick()
            self._state.loop(dt)
            pygame.display.flip()
        self._state.destroy()


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


class MenuState(AppState):
    """Класс главного меню"""

    def __init__(self, background_image, text):
        super().__init__()

        all_sprites.empty()
        main_group.empty()

        self._bg_img = imgs[background_image]
        self._text = text.split('\n')

    def setup(self):
        self._bg_img = pygame.transform.scale(self._bg_img, self.get_app().get_display_size())

    def process_event(self, event):  # обрабатываем события
        if event.type == pygame.MOUSEBUTTONDOWN and 440 > event.pos[0] > 240 and 750 > event.pos[1] > 650:
            self.get_app().set_state(Level1())  # "открываем" первый уровень
        if event.type == pygame.MOUSEBUTTONDOWN and 980 > event.pos[0] > 780 and 750 > event.pos[1] > 650:
            self.get_app().set_state(Level2())  # "открываем" второй уровень

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
        font = pygame.font.Font(None, 50)
        screen.blit(font.render('1 уровень', True, (100, 255, 100)), (255, 675))
        screen.blit(font.render('2 уровень', True, (100, 255, 100)), (795, 675))

    def destroy(self):
        pass


class LevelCompleted(AppState):
    """Уровень, отображаемый при удачном завершении игры"""

    def __init__(self, background_image, red_gem_amount, blue_gem_amount, time, level):
        super().__init__()

        all_sprites.empty()

        self._bg_img = imgs[background_image]
        self._time = time
        self._red_gem_amount = red_gem_amount
        self._blue_gem_amount = blue_gem_amount
        self._level = level
        self._text = f'Поздравляем, вы прошли уровень {self._level}!' \
                     f'\nВаше время: {self._time} сек\nСобранные алмазы:\n\n\nИграть заново?'.split('\n')

    def setup(self):
        self._bg_img = pygame.transform.scale(self._bg_img, self.get_app().get_display_size())

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and 500 > event.pos[0] > 100 and 650 > event.pos[1] > 450:  # 1 уровень
            self.get_app().set_state(Level1())
        if event.type == pygame.MOUSEBUTTONDOWN and 1100 > event.pos[0] > 700 and 650 > event.pos[1] > 450:  # 2 уровень
            self.get_app().set_state(Level2())

    def loop(self, dt):
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

        pygame.draw.rect(screen, (123, 104, 238), (100, 450, 400, 200))
        pygame.draw.rect(screen, (123, 104, 238), (700, 450, 400, 200))

        font = pygame.font.Font(None, 100)
        screen.blit(font.render('1 уровень', True, (100, 255, 100)), (130, 500))
        screen.blit(font.render('2 уровень', True, (100, 255, 100)), (730, 500))


class GameState(AppState):

    def __init__(self):
        super().__init__()

    def setup(self):
        pass

    def process_event(self, event):
        pass

    def loop(self, dt):
        self.get_app().get_screen().fill((255, 128, 0))

    def destroy(self):
        pass


class Level1(AppState):
    """Класс первого уровня"""

    def __init__(self):
        super().__init__()
        self._start_ticks = pygame.time.get_ticks()
        self._seconds = 0
        self._font = pygame.font.Font(None, 50)
        level_x, level_y = generate_level(load_level('data/level1.txt'), load_sprties('data/sprites_level1.txt'))

    def loop(self, dt):
        screen = self.get_app().get_screen()

        tiles_group.draw(screen)

        all_sprites.update(pygame.key.get_pressed(), dt)
        all_sprites.draw(screen)

        main_group.update(pygame.key.get_pressed(), dt)
        main_group.draw(screen)

        self._seconds = (pygame.time.get_ticks() - self._start_ticks) // 1000
        pygame.draw.rect(screen, (32, 29, 14), (500, 0, 200, 50))
        screen.blit(self._font.render(f'0{str(self._seconds)}:00', True, (112, 102, 50)), (550, 10))

    def setup(self):
        pass

    def process_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.get_app().set_state(MenuState('background', 'Ты вернулся в меню'))

    def destroy(self):
        pass


class Level2(AppState):
    """Класс второго уровня"""

    def __init__(self):
        super().__init__()
        self._start_ticks = pygame.time.get_ticks()
        self._seconds = 0
        self._font = pygame.font.Font(None, 50)
        level_x, level_y = generate_level(load_level('data/level2.txt'), load_sprties('data/sprites_level2.txt'))

    def loop(self, dt):
        screen = self.get_app().get_screen()

        tiles_group.draw(screen)

        all_sprites.update(pygame.key.get_pressed(), dt)
        all_sprites.draw(screen)

        main_group.update(pygame.key.get_pressed(), dt)
        main_group.draw(screen)

        self._seconds = (pygame.time.get_ticks() - self._start_ticks) // 1000
        pygame.draw.rect(screen, (32, 29, 14), (500, 0, 200, 50))
        screen.blit(self._font.render(f'0{str(self._seconds)}:00', True, (112, 102, 50)), (550, 10))

    def setup(self):
        pass

    def process_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.get_app().set_state(MenuState('background', 'Ты вернулся в меню'))

    def destroy(self):
        pass


class Tile(pygame.sprite.Sprite):
    """Класс тайлов"""

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__()
        self.tile_type = tile_type
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(60 * pos_x, 30 * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Object(pygame.sprite.Sprite):
    """Класс объектов (луж и дверей)"""

    def __init__(self, object_type, pos_x, pos_y):
        super().__init__()
        self._type = object_type
        self.image = object_images[self._type]
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Gem(Object):
    """Класс алмазов"""

    def __init__(self, object_type, pos_x, pos_y):
        super().__init__(object_type, pos_x, pos_y)


class MainSrites(pygame.sprite.Sprite):
    """Класс главных спрайтов - огня и воды"""

    def __init__(self, type, pos_x, pos_y, *group):  # type должен быть равен либо 'fire', либо 'water'
        super().__init__(*group)
        self._type = type
        self._position = [pos_x, pos_y]
        self.image = main_sprites[self._type]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, keys, dt):
        if keys[pygame.K_UP] and self._type == 'fire':
            self._position[1] -= 10 * dt / 100
        if keys[pygame.K_LEFT] and self._type == 'fire':
            self.image = main_sprites['fire_left']
            self._position[0] -= 10 * dt / 100
        elif keys[pygame.K_RIGHT] and self._type == 'fire':
            self.image = main_sprites['fire_right']
            self._position[0] += 10 * dt / 100
        if keys[pygame.K_w] and self._type == 'water':
            self._position[1] -= 10 * dt / 100
        if keys[pygame.K_a] and self._type == 'water':
            self.image = main_sprites['water_left']
            self._position[0] -= 10 * dt / 100
        elif keys[pygame.K_d] and self._type == 'water':
            self.image = main_sprites['water_right']
            self._position[0] += 10 * dt / 100
        if not any([i for i in keys]):
            self.image = main_sprites[self._type]
        self.rect.x, self.rect.y = self._position


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
        else:
            all_sprites.add(Object(line[0], int(line[1]), int(line[2])))

    return x, y


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

    menu_state = MenuState('background', 'Привет!'
                                         '\nТы попал в игру "огонь и вода"'
                                         '\nПравила игры: управлять девочкой можно клавишами A, W, D; '
                                         'мальчиком можно управлять стрелками. \n'
                                         'Если смешать огонь и воду или огонь/воду с зелёной жидкостью, '
                                         'то Вы проиграете.\n'
                                         'В игре есть 2 уровня, чтбы начать нажмите на одну из кнопок. Удачи!')
    app.set_state(menu_state)
    app.run()
