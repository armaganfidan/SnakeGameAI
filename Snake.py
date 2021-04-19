import pygame
import random
import numpy as np
from enum import Enum
from collections import namedtuple
import os

pygame.init()

BLOCK = 40
WIDTH = 640
HEIGHT = 480
font = pygame.font.SysFont("monospace", 16)

SNAKE_HEAD = [pygame.transform.scale(pygame.image.load(os.path.join("Snake", "head_right.png")), (BLOCK, BLOCK)),
              pygame.transform.scale(pygame.image.load(os.path.join("Snake", "head_left.png")), (BLOCK, BLOCK)),
              pygame.transform.scale(pygame.image.load(os.path.join("Snake", "head_up.png")), (BLOCK, BLOCK)),
              pygame.transform.scale(pygame.image.load(os.path.join("Snake", "head_down.png")), (BLOCK, BLOCK))]

SNAKE_BODY = [pygame.transform.scale(pygame.image.load(os.path.join("Snake", "body_horizontal.png")), (BLOCK, BLOCK)),
              pygame.transform.scale(pygame.image.load(os.path.join("Snake", "body_vertical.png")), (BLOCK, BLOCK))]

SNAKE_TAIL = [pygame.transform.scale(pygame.image.load(os.path.join("Snake", "tail_left.png")), (BLOCK, BLOCK)),
              pygame.transform.scale(pygame.image.load(os.path.join("Snake", "tail_right.png")), (BLOCK, BLOCK)),
              pygame.transform.scale(pygame.image.load(os.path.join("Snake", "tail_up.png")), (BLOCK, BLOCK)),
              pygame.transform.scale(pygame.image.load(os.path.join("Snake", "tail_down.png")), (BLOCK, BLOCK))]

BODY_L = [pygame.transform.scale(pygame.image.load(os.path.join("Snake", "body_bl.png")), (BLOCK, BLOCK)),
          pygame.transform.scale(pygame.image.load(os.path.join("Snake", "body_br.png")), (BLOCK, BLOCK)),
          pygame.transform.scale(pygame.image.load(os.path.join("Snake", "body_tl.png")), (BLOCK, BLOCK)),
          pygame.transform.scale(pygame.image.load(os.path.join("Snake", "body_tr.png")), (BLOCK, BLOCK))]


BACKGROUND = pygame.transform.scale((pygame.image.load(os.path.join("Snake", "Background.jpg"))), (WIDTH, HEIGHT))


APPLE = pygame.transform.scale(pygame.image.load(os.path.join("Snake", "apple.png")), (BLOCK, BLOCK))


Point = namedtuple("Point", "x, y")

SPEED = 20
RED = (255, 0, 0)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class SnakeGame:
    def __init__(self):
        self.display = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.a = 0
        self.b = 0
        self.backgroundcolors = 48
        pygame.mixer.music.load(r"professor-layton-and-the-last-time-travel-ost-the-professors-trunk-minicar-hq-version.mp3")
        pygame.mixer.music.play(-1)
        self.reset()


    def reset(self):
        self.direction = Direction.RIGHT

        self.head = Point(WIDTH/2, HEIGHT/2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK, self.head.y),
                      Point(self.head.x - 2 * BLOCK, self.head.y),
                      Point(self.head.x - 3 * BLOCK, self.head.y)]
        self.hit = 0
        self.food = None
        self.place_food()
        self.frame = 0


    def place_food(self):
        x = random.randint(0, (WIDTH - BLOCK) // BLOCK) * BLOCK
        y = random.randint(0, (HEIGHT - BLOCK) // BLOCK) * BLOCK
        self.food = Point(x, y)
        if self.food in self.snake:
            self.place_food()

    def play(self, action):
        self.frame += 1
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.move(action)
        self.snake.insert(0, self.head)
        reward = 0

        game_over = False
        if self.finish() or self.frame > 100*len(self.snake):
            reward -= 10
            game_over = True
            return reward, game_over, self.hit


        if self.head == self.food:
            self.hit += 1
            reward += 15
            self.place_food()
            eating_sound = pygame.mixer.Sound("minecraft-eating-sound-effect-[AudioTrimmer.com].mp3")
            eating_sound.play()
        else:
            self.snake.pop()

        self.update(self.direction)
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.hit


    def finish(self, pt=None):

        if pt is None:
            pt = self.head

        if pt.x > WIDTH - BLOCK or pt.x < 0 or pt.y > HEIGHT - BLOCK or pt.y < 0:
            return True

        if self.head in self.snake[1:]:
            return True

        return False


    def update(self, direction):

        self.display.fill((self.backgroundcolors - self.hit, self.backgroundcolors - self.hit, self.backgroundcolors - self.hit))
        self.display.blit(BACKGROUND, (0,0))



        for index, i in enumerate(self.snake):

            if direction == Direction.LEFT:
                if i == self.head:
                    self.display.blit(SNAKE_HEAD[1], (self.head.x, self.head.y))

            elif direction == Direction.RIGHT:
                if i == self.head:
                    self.display.blit(SNAKE_HEAD[0], (self.head.x, self.head.y))

            elif direction == Direction.UP:
                if i == self.head:
                    self.display.blit(SNAKE_HEAD[2], (self.head.x, self.head.y))

            else:
                if i == self.head:
                    self.display.blit(SNAKE_HEAD[3], (self.head.x, self.head.y))

            if i != self.head and i != self.snake[-1]:
                previus_block = self.snake[index + 1].x - i.x, self.snake[index + 1].y - i.y
                next_block = self.snake[index - 1].x - i.x, self.snake[index - 1].y - i.y

                previus_block = Point(previus_block[0], previus_block[1])
                next_block = Point(next_block[0], next_block[1])

                if next_block.x == -BLOCK and previus_block.y == -BLOCK or next_block.y == -BLOCK and previus_block.x == -BLOCK:
                    self.display.blit(BODY_L[2], (i.x, i.y))
                elif next_block.x == -BLOCK and previus_block.y == BLOCK or next_block.y == BLOCK and previus_block.x == -BLOCK:
                    self.display.blit(BODY_L[0], (i.x, i.y))
                elif next_block.x == BLOCK and previus_block.y == -BLOCK or next_block.y == -BLOCK and previus_block.x == BLOCK:
                    self.display.blit(BODY_L[3], (i.x, i.y))
                elif next_block.x == BLOCK and previus_block.y == BLOCK or next_block.y == BLOCK and previus_block.x == BLOCK:
                    self.display.blit(BODY_L[1], (i.x, i.y))


                elif next_block.x - previus_block.x < 0:
                    self.display.blit(SNAKE_BODY[0], (i.x, i.y))
                elif next_block.x - previus_block.x > 0:
                    self.display.blit(SNAKE_BODY[0], (i.x, i.y))
                elif next_block.y - previus_block.y < 0:
                    self.display.blit(SNAKE_BODY[1], (i.x, i.y))
                elif next_block.y - previus_block.y > 0:
                    self.display.blit(SNAKE_BODY[1], (i.x, i.y))



            if i == self.snake[-1]:
                previus_block = self.snake[index - 1].x - i.x, self.snake[index-1].y - i.y
                previus_block = Point(previus_block[0], previus_block[1])


                if previus_block.x == BLOCK:
                    self.display.blit(SNAKE_TAIL[0], (i.x, i.y))
                elif previus_block.x == -BLOCK:
                    self.display.blit(SNAKE_TAIL[1], (i.x, i.y))
                elif previus_block.y == BLOCK:
                    self.display.blit(SNAKE_TAIL[2], (i.x, i.y))
                elif previus_block.y == -BLOCK:
                    self.display.blit(SNAKE_TAIL[3], (i.x, i.y))

        self.display.blit(APPLE, (self.food.x, self.food.y))

        text = font.render("Score: " + str(self.hit), True, (0,0,0))

        self.display.blit(text, [WIDTH/2-50, 0])
        pygame.display.flip()


    def move(self, action):

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx+1) % 4
            new_dir = clock_wise[next_idx]
        else:
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK
        elif self.direction == Direction.LEFT:
            x -= BLOCK
        elif self.direction == Direction.DOWN:
            y += BLOCK
        elif self.direction == Direction.UP:
            y -= BLOCK

        self.head = Point(x, y)




