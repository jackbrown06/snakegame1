#Make sure to run: "pip install pygame" before running

import pygame
import random
import sys

SCREEN_WIDTH = 1000
SCREEN_LENGTH = 1000
BUTTON_WIDTH, BUTTON_HEIGHT = 300, 50
SPACE_BETWEEN = 40
SNAKE_BLOCK = 50
SNAKE_SPEED = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (204, 35, 35)
BLUE = (4, 36, 252)
NUM_OBSTACLES = 10
obstacles = []

pygame.init()

small_pixel = pygame.font.Font("PressStart2P.ttf", 15)
pixel = pygame.font.Font("PressStart2P.ttf", 20)
large_pixel = pygame.font.Font("PressStart2P.ttf", 40)

bg = pygame.image.load("grass.png")

head_image = pygame.image.load("snake_head.png")
head_image = pygame.transform.scale(head_image, (SNAKE_BLOCK, SNAKE_BLOCK))

food_image = pygame.image.load("apple.png")
food_image = pygame.transform.scale(food_image, (SNAKE_BLOCK, SNAKE_BLOCK))

obstacle_image = pygame.image.load("obstacle.png")
obstacle_image = pygame.transform.scale(obstacle_image, (SNAKE_BLOCK, SNAKE_BLOCK))

tail_image = pygame.image.load("tail.png")
tail_image = pygame.transform.scale(tail_image, (SNAKE_BLOCK, SNAKE_BLOCK))

eat_sound = pygame.mixer.Sound("eating.wav")
eat_sound.set_volume(0.05)

death_sound = pygame.mixer.Sound("death.wav")
death_sound.set_volume(0.05)

win_sound = pygame.mixer.Sound("win.wav")
win_sound.set_volume(0.05)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_LENGTH))
pygame.display.set_caption('Snake')

fps = pygame.time.Clock()
score = 0
running = True

def main():
    while True:
        mode = title_screen()
        if mode is None:
            pygame.quit()
            sys.exit()
        if not game_loop(mode):
            pygame.quit()
            sys.exit()
    
def title_screen():
    endless_button_rect = pygame.Rect((SCREEN_WIDTH // 2 - BUTTON_WIDTH - SPACE_BETWEEN // 2, SCREEN_LENGTH // 2), (BUTTON_WIDTH, BUTTON_HEIGHT))
    score_button_rect = pygame.Rect((SCREEN_WIDTH // 2 + SPACE_BETWEEN // 2, SCREEN_LENGTH // 2), (BUTTON_WIDTH, BUTTON_HEIGHT))

    while True:
        screen.fill(BLACK)
        render_centered_text("SNAKE", large_pixel, WHITE, screen, (SCREEN_WIDTH // 2, SCREEN_LENGTH // 3))

        render_centered_text("By: Jack Brown", pixel, WHITE, screen, (SCREEN_WIDTH // 2, SCREEN_LENGTH // 2.5))
        
        pygame.draw.rect(screen, WHITE, endless_button_rect, width=1)
        render_centered_text("Endless Mode (E)", small_pixel, WHITE, screen, endless_button_rect.center)
        
        pygame.draw.rect(screen, WHITE, score_button_rect, width=1)
        render_centered_text("Go for 30 (S)", pixel, WHITE, screen, score_button_rect.center)

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if endless_button_rect.collidepoint(event.pos):
                    return "endless"
                elif score_button_rect.collidepoint(event.pos):
                    return "score"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    return "score"
                elif event.key == pygame.K_e:
                    return "endless"

def init_game():
    global snake, snake_direction, food_position, score, obstacles

    choose_start_direction()
    
    head_position = (SCREEN_WIDTH // 2, SCREEN_LENGTH // 2)
    
    if snake_direction == "RIGHT":
        body_segment = (head_position[0] - SNAKE_BLOCK, head_position[1])
    elif snake_direction == "LEFT":
        body_segment = (head_position[0] + SNAKE_BLOCK, head_position[1])
    elif snake_direction == "UP":
        body_segment = (head_position[0], head_position[1] + SNAKE_BLOCK)
    elif snake_direction == "DOWN":
        body_segment = (head_position[0], head_position[1] - SNAKE_BLOCK)
    
    snake = [head_position, body_segment]
    
    food_position = generate_food()

    obstacles = []
    generate_obstacles()

    score = 0

def game_loop(mode):
    global running
    init_game()
    running = True
    while running:
        handle_input()
        update_snake()
        check_collisions()
  
        if mode == "score" and score >= 30:
            display_win_message()
            return
        
        draw_game()
        fps.tick(SNAKE_SPEED)

def choose_start_direction():
    global snake_direction
    waiting = True
    while waiting:
        screen.fill(BLACK)
        render_centered_text("Press an arrow key to choose a start direction.", pixel, WHITE, screen, (SCREEN_WIDTH // 2, SCREEN_LENGTH // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    snake_direction = "LEFT"
                    waiting = False
                elif event.key == pygame.K_RIGHT:
                    snake_direction = "RIGHT"
                    waiting = False
                elif event.key == pygame.K_UP:
                    snake_direction = "UP"
                    waiting = False
                elif event.key == pygame.K_DOWN:
                    snake_direction = "DOWN"
                    waiting = False

def handle_input():
    global running, snake_direction
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and snake_direction != "RIGHT":
                snake_direction = "LEFT"
            elif event.key == pygame.K_RIGHT and snake_direction != "LEFT":
                snake_direction = "RIGHT"
            elif event.key == pygame.K_UP and snake_direction != "DOWN":
                snake_direction = "UP"
            elif event.key == pygame.K_DOWN and snake_direction != "UP":
                snake_direction = "DOWN"

def update_snake():
    global food_position, score
    x, y = snake[0]
    if snake_direction == "LEFT":
        x -= SNAKE_BLOCK
    elif snake_direction == "RIGHT":
        x += SNAKE_BLOCK
    elif snake_direction == "DOWN":
        y += SNAKE_BLOCK
    elif snake_direction == "UP":
        y -= SNAKE_BLOCK
    new_head = (x, y)
    snake.insert(0, new_head)
    if new_head == food_position:
        score += 1
        food_position = generate_food()
        eat_sound.play()
    else:
        snake.pop()

def generate_food():
    while True:
        x = random.randint(0, (SCREEN_WIDTH // SNAKE_BLOCK) - 1) * SNAKE_BLOCK
        y = random.randint(0, (SCREEN_LENGTH // SNAKE_BLOCK) - 1) * SNAKE_BLOCK
        food_position = (x, y)
        if food_position not in snake and food_position not in obstacles:
            return food_position

def generate_obstacles():
    for _ in range(NUM_OBSTACLES):
        while True:
            x = random.randint(0, (SCREEN_WIDTH // SNAKE_BLOCK) - 1) * SNAKE_BLOCK
            y = random.randint(0, (SCREEN_LENGTH // SNAKE_BLOCK) - 1) * SNAKE_BLOCK
            obstacle_position = (x, y)
            if obstacle_position not in snake and obstacle_position != food_position:
                obstacles.append(obstacle_position)
                break

def check_collisions():
    head_x, head_y = snake[0]
    if head_x < 0 or head_x + SNAKE_BLOCK > SCREEN_WIDTH or head_y < 0 or head_y + SNAKE_BLOCK > SCREEN_LENGTH:
        game_over()
    for segment in snake[1:]:
        if head_x == segment[0] and head_y == segment[1]:
            game_over()
    if (head_x, head_y) in obstacles:
        game_over()
            
def get_rotated_head():
    if snake_direction == "RIGHT":
        return pygame.transform.rotate(head_image, -90)
    elif snake_direction == "DOWN":
        return pygame.transform.rotate(head_image, 180)
    elif snake_direction == "LEFT":
        return pygame.transform.rotate(head_image, 90)
    else:
        return head_image

def get_rotated_tail(tail_x, tail_y, second_last_segment):
    if tail_x < second_last_segment[0]:
        return pygame.transform.rotate(tail_image, -90)
    elif tail_x > second_last_segment[0]:
        return pygame.transform.rotate(tail_image, 90)
    elif tail_y < second_last_segment[1]:
        return pygame.transform.rotate(tail_image, 180)
    elif tail_y > second_last_segment[1]:
        return tail_image

def draw_game():
    screen.blit(bg, (0,0))

    rotated_head = get_rotated_head()
    
    head_x, head_y = snake[0]
    screen.blit(rotated_head, (head_x, head_y))
    
    for segment in snake[1:-1]:
        pygame.draw.rect(screen, BLUE, [segment[0], segment[1], SNAKE_BLOCK, SNAKE_BLOCK])

    tail_x, tail_y = snake[-1]
    second_last_segment = snake[-2]

    rotated_tail = get_rotated_tail(tail_x, tail_y, second_last_segment)
    
    screen.blit(rotated_tail, (tail_x, tail_y))
        
    screen.blit(food_image, food_position)

    for obstacle in obstacles:
        screen.blit(obstacle_image, (obstacle[0], obstacle[1]))
    
    display_score()
    pygame.display.update()

def display_score():
    render_centered_text(f"Score: {score}", pixel, WHITE, screen, (SCREEN_WIDTH // 2, 20))

def draw_black_matte(x, y, width, height, color, opacity):
    transparent_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    transparent_surface.fill((*color, opacity))
    screen.blit(transparent_surface, (x, y))

def render_centered_text(text, font, color, screen, position):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)

def display_win_message():
    draw_black_matte(0, 0, SCREEN_WIDTH, SCREEN_LENGTH, BLACK, 150)
    
    quit_button_rect = pygame.Rect((SCREEN_WIDTH // 2 - BUTTON_WIDTH - SPACE_BETWEEN // 2, SCREEN_LENGTH // 2), (BUTTON_WIDTH, BUTTON_HEIGHT))
    restart_button_rect = pygame.Rect((SCREEN_WIDTH // 2 + SPACE_BETWEEN // 2, SCREEN_LENGTH // 2), (BUTTON_WIDTH, BUTTON_HEIGHT))

    win_sound.play()
    
    render_centered_text("You Win!", large_pixel, WHITE, screen, (SCREEN_WIDTH // 2, SCREEN_LENGTH // 3))
    
    pygame.draw.rect(screen, WHITE, quit_button_rect)
    render_centered_text("Quit (Q)", pixel, BLACK, screen, quit_button_rect.center)

    pygame.draw.rect(screen, WHITE, restart_button_rect)
    render_centered_text("Play Again (R)", pixel, BLACK, screen, restart_button_rect.center)
    
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    main()
                elif quit_button_rect.collidepoint(event.pos):
                    pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()

def game_over():
    global running
    
    draw_black_matte(0, 0, SCREEN_WIDTH, SCREEN_LENGTH, BLACK, 150)
    
    quit_button_rect = pygame.Rect((SCREEN_WIDTH // 2 - BUTTON_WIDTH - SPACE_BETWEEN // 2, SCREEN_LENGTH // 2), (BUTTON_WIDTH, BUTTON_HEIGHT))
    restart_button_rect = pygame.Rect((SCREEN_WIDTH // 2 + SPACE_BETWEEN // 2, SCREEN_LENGTH // 2), (BUTTON_WIDTH, BUTTON_HEIGHT))
    
    render_centered_text("Game Over!", large_pixel, RED, screen, (SCREEN_WIDTH // 2, SCREEN_LENGTH // 3))
    
    pygame.draw.rect(screen, BLACK, quit_button_rect)
    render_centered_text("Quit (Q)", pixel, WHITE, screen, quit_button_rect.center)

    pygame.draw.rect(screen, BLACK, restart_button_rect)
    render_centered_text("Restart (R)", pixel, WHITE, screen, restart_button_rect.center)

    if not pygame.mixer.get_busy():
        death_sound.play()
    
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if quit_button_rect.collidepoint(event.pos):
                    running = False
                    return
                elif restart_button_rect.collidepoint(event.pos):
                    main()
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                    return
                elif event.key == pygame.K_q:
                    running = False
                    return
main()