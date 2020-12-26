from abc import abstractmethod
import pygame


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
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.get_app().set_state(GameState())

    def loop(self, dt):
        screen = self.get_app().get_screen()
        screen.fill((0, 0, 0))
        screen.blit(self._bg_img, (0, 0))
        font = pygame.font.Font(None, 30)
        for i, line in enumerate(self._text):
            line_img = font.render(line, True, pygame.Color('magenta'))
            screen.blit(line_img, (0, i * line_img.get_rect().height * 1.1))

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


def load_image(image_path, colorkey=None):
    result = pygame.image.load(image_path)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = result.get_at((0, 0))
        result.set_colorkey(colorkey)
    else:
        result.convert_alpha()
    return result


if __name__ == '__main__':

    app = App((640, 480))

    imgs = {'background': load_image('data/background.jpg'),
            }

    menu_state = MenuState('background', 'Привет!\nТы попал в игру!')
    app.set_state(menu_state)
    app.run()
