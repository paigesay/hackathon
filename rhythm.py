import pygame
import sys
from sys import exit

pygame.init()

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AstroBeats")

# Accessible Game Variables
clock = pygame.time.Clock()
NUM_LANES = 4
LANE_WIDTH = SCREEN_WIDTH // NUM_LANES


def load_assets():
    # For each lane
    note_images = [
        pygame.image.load("assets/planet1.png").convert_alpha(),
        pygame.image.load("assets/planet2.png").convert_alpha(),
        pygame.image.load("assets/planet3.png").convert_alpha(),
        pygame.image.load("assets/planet4.png").convert_alpha()
    ]
    
    # Background images for switching effect
    bg1 = pygame.image.load("assets/background1.png").convert_alpha()
    bg2 = pygame.image.load("assets/background2.png").convert_alpha()
    
    return note_images, bg1, bg2

# Creating Notes Class
class Note:
    def __init__(self, lane, start_y):
    # These lanes are based off which img used
        self.lane = lane
        self.img = note_images[lane]
        
    #  X-coordinate to center the note in its lane
        self.x = lane * lane_width + lane_width // 2 - self.img.get_width() // 2
        self.y = start_y  # starting y position
        self.speed = 10
    
    def update(self):
        self.y += self.speed
        
    def draw(self):
        screen.blit(self.img, (self.x, self.y))
    
    def in_hit_zone(self, hit_zone_y, hit_zone_height):
        return hit_zone_y <= self.y <= hit_zone_y + hit_zone_height 

# Exiting game
def quit_game():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
def main():
    
    switch_interval = 500
    #Loading Assets
    note_images, bg1, bg2 = load_assets()

    # Create some notes for demonstration (one in each lane)
    notes = [
        Note(lane=0, start_y=-50, note_images=note_images, lane_width=lane_width),
        Note(lane=1, start_y=-100, note_images=note_images, lane_width=lane_width),
        Note(lane=2, start_y=-150, note_images=note_images, lane_width=lane_width),
        Note(lane=3, start_y=-200, note_images=note_images, lane_width=lane_width)
    ]
    
    # Creating Lanes 
    # Main game loop
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            # Hit detection on SPACE key press
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for note in notes:
                        if note.is_in_hit_zone(hit_zone_y, hit_zone_height):
                            print(f"Note in lane {note.lane} hit!")
                            # For testing, we simply move the note off-screen
                            note.y = SCREEN_HEIGHT + 100
                            
    current_time = pygame.time.get_ticks()
    if (current_time // switch_interval) % 2 == 0:
        current_background = bg1
    else:
        current_background = bg2

    # Draw background
    screen.blit(current_background, (0, 0))

# Draw the current background to the screen
    screen.blit(current_background, (SCREEN_HEIGHT, SCREEN_WIDTH))

# End of Creating Lanes 

# Creating Hit Zones for Notes
    hit_zone_y = SCREEN_HEIGHT - 100
    hit_zone_height = 20
    
    pygame.display.update()
    clock.tick(60)
    
    
def menu():
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # Trigger the game start on a discrete mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
    ## screen.fill((0, 0, 0))
    ## text_surface = font.render("Hello, AstroBeats!", True, (255, 255, 255))
    ## screen.blit(text_surface, (50, 50))
    
menu()