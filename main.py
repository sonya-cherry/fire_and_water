from abc import abstractmethod
import pygame

DISPLAY_SIZE = (1200, 900)


class App:

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

    def run(self):
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

    def __init__(self, background_image, text):
        super().__init__()
        self._bg_img = imgs[background_image]
        self._text = text.split('\n')

    def setup(self):
        self._bg_img = pygame.transform.scale(self._bg_img, self.get_app().get_display_size())

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and 260 > event.pos[0] > 110 and 450 > event.pos[1] > 350:  # 1 уровень
            self.get_app().set_state(Level1())
        if event.type == pygame.MOUSEBUTTONDOWN and 550 > event.pos[0] > 400 and 450 > event.pos[1] > 350:  # 2 уровень
            self.get_app().set_state(GameState())

    def loop(self, dt):
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


class GameState(AppState):

    def __init__(self):
        super().__init__()

    def setup(self):
        pass

    def process_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.get_app().set_state(MenuState('background', 'Ты вернулся в меню!\nУра!\n(Не уходи)'))

    def loop(self, dt):
        self.get_app().get_screen().fill((255, 128, 0))

    def destroy(self):
        pass


class Level1(AppState):

    def __init__(self):
        super().__init__()

    def loop(self, dt):
        screen = self.get_app().get_screen()
        level_x, level_y = generate_level(load_level('data/level1.txt'))
        tiles_group.draw(screen)

    def setup(self):
        pass

    def process_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.get_app().set_state(MenuState('background', 'Ты вернулся в меню!\nУра!\n(Не уходи)'))

    def destroy(self):
        pass


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__()
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            60 * pos_x, 30 * pos_y)


def load_image(image_path, colorkey=None):
    result = pygame.image.load(image_path)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = result.get_at((0, 0))
        result.set_colorkey(colorkey)
    else:
        result.convert_alpha()
    return result


def load_level(filename):
    filename = filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    return level_map


def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == ' ':
                tiles_group.add(Tile('empty', x, y))
            elif level[y][x] == '-':
                tiles_group.add(Tile('wall', x, y))
    return x, y


if __name__ == '__main__':

    app = App(DISPLAY_SIZE)

    imgs = {'background': load_image('data/fire_and_water.jpg'),
            'level1_platforms': load_image('data/level1_platforms.png')
            }
    tile_images = {
            'wall': load_image('data/light_tile.png'),
            'empty': load_image('data/dark_tile.png')}

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()

    menu_state = MenuState('background', 'Привет!'
                                         '\nТы попал в игру "огонь и вода"'
                                         '\nПравила игры: управлять девочкой можно клавишами A, W, D; '
                                         'мальчиком можно управлять стрелками. \n'
                                         'Если смешать огонь и воду, то Вы проиграете.\n'
                                         'В игре есть 2 уровня, чтбы начать нажмите на одну из кнопок. Удачи!')
    app.set_state(menu_state)
    app.run()
