import math
import pygame.font
import pymunk
import pymunk.pygame_util
import pygame as pg

pg.init()

# Tworzenie okna
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Billard")

# przestrzeń dla pymunk (fizyka)
space = pymunk.Space()
static_body = space.static_body
draw_options = pymunk.pygame_util.DrawOptions(screen)

# zegar od odświeżania
clock = pg.time.Clock()
FPS = 120

# zmienne gry
can_shot = True
force = 0
rad = 18
hole_rad = 30
power_up = False
x_impulse = 0
y_impulse = 0
hole_balls = []

# kolor tła okna
BG = (50, 50, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# czcionki
font = pygame.font.SysFont("Lato", 100)
small_font = pygame.font.SysFont("Lato", 40)

# ładowanie obrazków
table_image = pg.image.load("assets/sprites/tlo1280X800.png").convert_alpha()
whiteBall_image = pg.image.load("assets/sprites/new_balls/16.png").convert_alpha()
bat_image = pg.image.load("assets/sprites/new_balls/bat.png").convert_alpha()

ball_images = []
for i in range(1, 17):
    ball_image = pg.image.load(f"assets/sprites/new_balls/{i}.png").convert_alpha()
    ball_images.append(ball_image)
print(len(ball_images))


def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

# tworzenie kólki
def create_ball(radius, pos):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.mass = 10
    shape.elasticity = 0.9

    # tarcie
    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot.max_bias = 0
    pivot.max_force = 500

    space.add(body, shape, pivot)
    return shape

# tworzenie ścian
def create_wall(poly_dims):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = (0, 0)
    shape = pymunk.Poly(body, poly_dims)
    shape.elasticity = 0.9

    space.add(body, shape)

class Bat():
    def __init__(self, pos):
        self.original_image = bat_image
        self.angle = 0
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def draw(self, surface):
        self.image = pg.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image,
                     (self.rect.centerx - self.image.get_width() / 2,
                     self.rect.centery - self.image.get_height() / 2)
                     )
        #pg.draw.rect(surface, (255, 0, 0), self.rect)

    def update(self, angle):
        self.angle = angle


# ustawienie kól na start
balls = []
rows = 5

for col in range(5):
    for row in range(rows):
        pos = (950 - (col * (rad * 2 + 1)), 325 + (row * (rad * 2 + 1)) + (col * rad))
        new_ball = create_ball(rad, pos)
        balls.append(new_ball)
    rows -= 1

pos = (400, SCREEN_HEIGHT / 2)
white_ball = create_ball(rad, pos)
balls.append(white_ball)

holes = [
    (117, 130),
    (641, 130),
    (1165, 130),
    (117, 655),
    (641, 655),
    (1165, 655)
]

walls = [
    [(157, 135), (175, 151), (605, 151), (614, 135)],
    [(672, 135), (681, 151), (1113, 151), (1128, 135)],
    [(157, 655), (175, 636), (605, 636), (614, 655)],
    [(672, 655), (681, 636), (1113, 636), (1128, 655)],

    [(121, 620), (140, 600), (140, 188), (121, 167)],
    [(1165, 620), (1147, 600), (1147, 188), (1164, 167)]
]

for i in walls:
    create_wall((i))

bat = Bat(balls[-1].body.position)

playing = True

# główna pętla
while playing:

    clock.tick(FPS)
    space.step(1 / FPS)

    screen.fill(BG)

    # rysowanie
    screen.blit(table_image, (0, 0))

    if len(balls) == 1:
        draw_text("YOU WIN!", font, WHITE, SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 - 150)

    for i, ball in enumerate(balls):
        for hole in holes:
            ball_x_distance = abs(ball.body.position[0] - hole[0])
            ball_y_distance = abs(ball.body.position[1] - hole[1])
            ball_hole_distance = math.sqrt((ball_x_distance ** 2) + (ball_y_distance ** 2))
            if ball_hole_distance <= hole_rad:
                if i == len(balls) - 1:
                    ball.body.position = (400, SCREEN_HEIGHT / 2)
                    ball.body.velocity = (0, 0)
                else:
                    space.remove(ball.body)
                    balls.remove(ball)
                    hole_balls.append(ball_images[i])
                    ball_images.pop(i)

    for i, ball in enumerate(balls):
        screen.blit(ball_images[i],
                    (ball.body.position[0] - ball.radius, ball.body.position[1] - ball.radius))

    can_shot = True
    for ball in balls:
        if ball.body.velocity[0] != 0 or ball.body.velocity[1] != 0:
            can_shot = False

    if can_shot and not power_up:
        mouse_pos = pg.mouse.get_pos()
        bat.rect.center = balls[-1].body.position
        x_distance = balls[-1].body.position[0] - mouse_pos[0]
        y_distance = -(balls[-1].body.position[1] - mouse_pos[1])
        bat_angle = math.degrees(math.atan2(y_distance, x_distance))
        bat.update(bat_angle)
        bat.draw(screen)

    if power_up and force <= 35000:
        force += 100
        mouse_pos = pg.mouse.get_pos()
        ax, ay = (bat.rect.centerx, bat.rect.centery)
        bx, by = (mouse_pos[0], mouse_pos[1])
        dx, dy = (bx - ax, by - ay)
        stepx, stepy = (dx / 25., dy / 25.)
        bat.rect.center = (bat.rect.centerx - stepx, bat.rect.centery - stepy)
        x_distance = bat.rect.centerx - mouse_pos[0]
        y_distance = -(bat.rect.centery - mouse_pos[1])
        bat_angle = math.degrees(math.atan2(y_distance, x_distance))
        bat.update(bat_angle)
        bat.draw(screen)

    elif not power_up and can_shot:
        bat.rect.center = balls[-1].body.position
        bat.draw(screen)
        x_impulse = math.cos(math.radians(bat_angle))
        y_impulse = math.sin(math.radians(bat_angle))
        balls[-1].body.apply_impulse_at_local_point((-force * x_impulse, force * y_impulse), (0, 0))
        force = 0

    for i, ball in enumerate(hole_balls):
        screen.blit(ball, (10 + (i * 50), 10))

    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN and can_shot:
            power_up = True

        if event.type == pg.MOUSEBUTTONUP and can_shot:
            bat.rect.center = balls[-1].body.position
            power_up = False

        if event.type == pg.QUIT:
            playing = False
    if force <= 35000:
        draw_text(f"Power: {force}", small_font, BLACK, SCREEN_WIDTH / 2 - 125, 0)
    if force > 35000:
        draw_text(f"Power: {force} is MAX", small_font, BLACK, SCREEN_WIDTH / 2 - 125, 0)
    pg.display.update()

pg.quit()
