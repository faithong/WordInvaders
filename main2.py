import math
import random

import pygame
from pygame import mixer

# Intialize the pygame
pygame.init()

# create the screen
screen = pygame.display.set_mode((800, 600))

# Background
background = pygame.image.load('background.png')

# Sound
mixer.music.load("background.wav")
mixer.music.play(-1)

# Caption and Icon
pygame.display.set_caption("Word Invader")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('player.png')
playerX = 370
playerY = 480
playerX_change = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 4

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, 736))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(4)
    enemyY_change.append(40)

# Bullet

# Ready - You can't see the bullet on the screen
# Fire - The bullet is currently moving

bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 10
bullet_state = "ready"

# Sentence text
sentence_text = pygame.font.Font('freesansbold.ttf', 20)
prepY = 0

# Game Over
over_font = pygame.font.Font('freesansbold.ttf', 64)

# Hit count
hit_count = 0

# display main page
first_Page = pygame.font.Font('freesansbold.ttf', 65)
description_font = pygame.font.Font('freesansbold.ttf', 15)

#button for first screen/page   
playFont = pygame.font.Font('freesansbold.ttf', 20)

# draw text to screen
def draw_text(surface, text, size, x, y, color):
    font = pygame.font.Font(pygame.font.match_font('freesansbold.ttf'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# display main page/screen
def main_page():
    # RGB = Red, Green, Blue
    screen.fill((0, 0, 0))
    # Background Image
    screen.blit(background, (0, 0))

    # display title
    title = first_Page.render("Word Invader", True, (255, 255, 255))
    screen.blit(title, (185, 185))

    # display description
    description = description_font.render("A game designed to help high school students prepare for the College Board’s SAT", True, (255, 255, 255))
    screen.blit(description, (100, 260))
    description2 = description_font.render("Reading Section by playing a modified version of Space Invaders (1978) to", True, (255, 255, 255))
    screen.blit(description2, (125, 280))
    description3 = description_font.render("practice their knowledge of common vocabulary words in said test.", True, (255, 255, 255))
    screen.blit(description3, (140, 300))
    
    # display CTA (call to action)
    draw_text(screen, "press [ENTER] to begin", 25, 390, 365, (220, 220, 220))

showMainScreen = True
while showMainScreen:
    
    main_page()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                showMainScreen = False

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY - bulletY, 2)))
    if distance < 27:
        return True
    else:
        return False


# Display sentence
def prep_sentence(prepY):
    sentence = sentence_text.render("A transportation [ planner's, ] job may include counting traffic.", True, (255, 255, 255))
    screen.blit(sentence, (85, prepY))

# Game Loop
running = True
while running: # main game loop

    # RGB = Red, Green, Blue
    screen.fill((0, 0, 0))

    # Background Image
    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  

        # if keystroke is pressed check whether its right or left
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -5
            if event.key == pygame.K_RIGHT:
                playerX_change = 5
            if event.key == pygame.K_SPACE:
                if bullet_state is "ready":
                    bulletSound = mixer.Sound("laser.wav")
                    bulletSound.play()
                    # Get the current x cordinate of the spaceship
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0
    
    # 5 = 5 + -0.1 -> 5 = 5 - 0.1
    # 5 = 5 + 0.1
    playerX += playerX_change
    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:
        playerX = 736

    # Enemy Movement
    for i in range(num_of_enemies):

        prep_sentence(25)

        # Game Over
        if hit_count >= 3:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            prepY = 0
            game_over_text()
            break

        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0:
            enemyX_change[i] = 4
            enemyY[i] += enemyY_change[i]
        elif enemyX[i] >= 736:
            enemyX_change[i] = -4
            enemyY[i] += enemyY_change[i]

        # Collision
        collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
        if collision:
            explosionSound = mixer.Sound("explosion.wav")
            explosionSound.play()
            bulletY = 480
            bullet_state = "ready"
            hit_count += 1
            enemyY[i] = 1000

        enemy(enemyX[i], enemyY[i], i)

    # Bullet Movement
    if bulletY <= 0:
        bulletY = 480
        bullet_state = "ready"

    if bullet_state is "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bulletY_change

    player(playerX, playerY)
    pygame.display.update()
