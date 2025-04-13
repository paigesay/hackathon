import pygame
import sys
from sys import exit
import os
import random

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

# For debugging - use colored rectangles instead of images if assets can't be loaded
def create_debug_surfaces():
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    note_surfaces = []
    
    for color in colors:
        # Create smaller notes that fit in the lanes
        surface = pygame.Surface((LANE_WIDTH - 20, LANE_WIDTH - 20), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (surface.get_width()//2, surface.get_height()//2), surface.get_width()//2)
        note_surfaces.append(surface)
    
    # Create starry backgrounds for pulsing effect
    bg1 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg1.fill((30, 30, 60))  # Dark blue
    # Add some stars
    for _ in range(100):
        x = pygame.Rect(
            pygame.random.randint(0, SCREEN_WIDTH-1),
            pygame.random.randint(0, SCREEN_HEIGHT-1),
            2, 2)
        pygame.draw.rect(bg1, (255, 255, 255), x)
    
    bg2 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg2.fill((60, 30, 60))  # Dark purple
    # Add some stars
    for _ in range(100):
        x = pygame.Rect(
            pygame.random.randint(0, SCREEN_WIDTH-1),
            pygame.random.randint(0, SCREEN_HEIGHT-1),
            2, 2)
        pygame.draw.rect(bg2, (255, 255, 255), x)
    
    return note_surfaces, bg1, bg2

def load_assets():
    # Check if assets directory exists
    if not os.path.isdir("assets"):
        return create_debug_surfaces()
    
    try:
        # For each lane
        note_images = []
        note_files = ["planet1.png", "planet2.png", "planet3.png", "planet4.png"]
        
        for file in note_files:
            path = os.path.join("assets", file)
            if os.path.isfile(path):
                # Load the image
                original_img = pygame.image.load(path).convert_alpha()
                
                # Calculate the desired size to fit in the lane
                # Make it 20 pixels smaller than the lane width to have some margin
                desired_width = LANE_WIDTH - 20
                
                # Keep aspect ratio
                aspect_ratio = original_img.get_height() / original_img.get_width()
                desired_height = int(desired_width * aspect_ratio)
                
                # Resize the image to fit the lane
                resized_img = pygame.transform.scale(original_img, (desired_width, desired_height))
                note_images.append(resized_img)
            else:
                # Create a colored rectangle instead
                surface = pygame.Surface((LANE_WIDTH - 20, LANE_WIDTH - 20), pygame.SRCALPHA)
                pygame.draw.circle(surface, (random.randint(150, 255), 
                                           random.randint(150, 255), 
                                           random.randint(150, 255)), 
                                  (surface.get_width()//2, surface.get_height()//2), 
                                  surface.get_width()//2)
                note_images.append(surface)
        
        # Background images for switching effect
        bg1_path = os.path.join("assets", "background1.png")
        bg2_path = os.path.join("assets", "background2.png")
        
        if os.path.isfile(bg1_path) and os.path.isfile(bg2_path):
            bg1 = pygame.image.load(bg1_path).convert_alpha()
            bg2 = pygame.image.load(bg2_path).convert_alpha()
        else:
            return create_debug_surfaces()
        
        return note_images, bg1, bg2
    
    except Exception:
        return create_debug_surfaces()

# Creating Notes Class
class Note:
    def __init__(self, lane, start_y, note_images, lane_width):
        # These lanes are based off which img used
        self.lane = lane
        self.img = note_images[lane]
        self.height = self.img.get_height()
        
        # X-coordinate to center the note in its lane
        self.x = lane * lane_width + lane_width // 2 - self.img.get_width() // 2
        self.y = start_y  # starting y position
        self.speed = 2  # Slower speed for the planets
        self.active = True  # Is this note still active (not hit or missed)
    
    def update(self):
        if self.active:
            self.y += self.speed
            
            # If note goes off screen, consider it missed
            if self.y > SCREEN_HEIGHT:
                self.reset()
        
    def draw(self):
        if self.active:
            screen.blit(self.img, (self.x, self.y))
    
    def is_in_hit_zone(self, hit_zone_y, hit_zone_height):
        return self.active and hit_zone_y <= self.y + self.height // 2 <= hit_zone_y + hit_zone_height
    
    def hit(self):
        self.active = False  # Deactivate the note instead of immediately resetting
    
    def reset(self):
        # Reset note to top of screen at a random position
        self.y = random.randint(-300, -50)
        self.active = True
    
    def get_bottom(self):
        return self.y + self.height
    
    def overlaps_with(self, other_note):
        # Check if this note overlaps with another note in the same lane
        if self.lane != other_note.lane or not self.active or not other_note.active:
            return False
        
        # Check vertical overlap - add a buffer of 100 pixels
        return (self.y <= other_note.get_bottom() + 100 and 
                other_note.y <= self.get_bottom() + 100)

# Generate a continuous stream of notes avoiding overlaps
def generate_notes(note_images, lane_width, num_notes=12):
    notes = []
    lane_positions = [0, 0, 0, 0]  # Track the last y position used in each lane
    
    for i in range(num_notes):
        # Choose a lane
        lane = random.randint(0, NUM_LANES - 1)
        
        # Make sure we're placing the new note far enough from the previous one in this lane
        min_start_y = lane_positions[lane] - 300  # At least 300 pixels separation
        start_y = min(min_start_y, -50 - (i * 150))  # Ensure upward movement
        
        # Update the last position for this lane
        lane_positions[lane] = start_y
        
        # Create the note
        notes.append(Note(lane=lane, start_y=start_y, note_images=note_images, lane_width=lane_width))
    
    return notes

# Exiting game
def quit_game():
    pygame.quit()
    sys.exit()
            
def main():
    # Loading Assets
    note_images, bg1, bg2 = load_assets()
    
    # Store original sizes for scaling
    bg1_orig_width, bg1_orig_height = bg1.get_width(), bg1.get_height()
    bg2_orig_width, bg2_orig_height = bg2.get_width(), bg2.get_height()
    
    # Lane width for proper positioning
    lane_width = SCREEN_WIDTH // NUM_LANES
    
    # Create falling notes with no overlaps
    notes = generate_notes(note_images, lane_width, 8)  # Fewer notes to reduce overlap chance
    
    # Background switching variables
    switch_interval = 2000  # milliseconds between switches (slower for glow effect)
    last_switch_time = 0
    current_background = bg1
    current_orig_width = bg1_orig_width
    current_orig_height = bg1_orig_height
    
    # For pulsing/glowing effect
    pulse_speed = 0.001  # Speed of the pulse effect
    pulse_min_scale = 1.0  # Minimum scale factor
    pulse_max_scale = 1.05  # Maximum scale factor (5% larger)
    pulse_factor = pulse_min_scale  # Current scale factor
    pulse_growing = True  # Whether we're growing or shrinking
    
    # Creating Hit Zones for Notes
    hit_zone_y = SCREEN_HEIGHT - 100
    hit_zone_height = 30
    
    # Lane highlighting
    lane_highlights = [0, 0, 0, 0]  # 0 = no highlight, countdown timer when > 0
    highlight_duration = 10  # frames to show the highlight
    
    # Score tracking
    score = 0
    
    # For respawning notes after a delay
    inactive_notes = []  # Notes that have been hit
    reset_timer = 0
    
    # Main game loop
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            # Hit detection on key press
            if event.type == pygame.KEYDOWN:
                # Lane 1 - D key
                if event.key == pygame.K_d:
                    lane_highlights[0] = highlight_duration
                    for note in notes:
                        if note.lane == 0 and note.is_in_hit_zone(hit_zone_y, hit_zone_height):
                            note.hit()
                            inactive_notes.append(note)
                            score += 100
                # Lane 2 - F key
                elif event.key == pygame.K_f:
                    lane_highlights[1] = highlight_duration
                    for note in notes:
                        if note.lane == 1 and note.is_in_hit_zone(hit_zone_y, hit_zone_height):
                            note.hit()
                            inactive_notes.append(note)
                            score += 100
                # Lane 3 - J key
                elif event.key == pygame.K_j:
                    lane_highlights[2] = highlight_duration
                    for note in notes:
                        if note.lane == 2 and note.is_in_hit_zone(hit_zone_y, hit_zone_height):
                            note.hit()
                            inactive_notes.append(note)
                            score += 100
                # Lane 4 - K key
                elif event.key == pygame.K_k:
                    lane_highlights[3] = highlight_duration
                    for note in notes:
                        if note.lane == 3 and note.is_in_hit_zone(hit_zone_y, hit_zone_height):
                            note.hit()
                            inactive_notes.append(note)
                            score += 100
                # Alternative controls using number keys
                elif event.key == pygame.K_1:
                    lane_highlights[0] = highlight_duration
                    for note in notes:
                        if note.lane == 0 and note.is_in_hit_zone(hit_zone_y, hit_zone_height):
                            note.hit()
                            inactive_notes.append(note)
                            score += 100
                elif event.key == pygame.K_2:
                    lane_highlights[1] = highlight_duration
                    for note in notes:
                        if note.lane == 1 and note.is_in_hit_zone(hit_zone_y, hit_zone_height):
                            note.hit()
                            inactive_notes.append(note)
                            score += 100
                elif event.key == pygame.K_3:
                    lane_highlights[2] = highlight_duration
                    for note in notes:
                        if note.lane == 2 and note.is_in_hit_zone(hit_zone_y, hit_zone_height):
                            note.hit()
                            inactive_notes.append(note)
                            score += 100
                elif event.key == pygame.K_4:
                    lane_highlights[3] = highlight_duration
                    for note in notes:
                        if note.lane == 3 and note.is_in_hit_zone(hit_zone_y, hit_zone_height):
                            note.hit()
                            inactive_notes.append(note)
                            score += 100
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()
                    sys.exit()
        
        # Clear the screen first
        screen.fill((0, 0, 0))
        
        # Update game state
        current_time = pygame.time.get_ticks()
        
        # Switch background based on time
        if current_time - last_switch_time >= switch_interval:
            last_switch_time = current_time
            if current_background == bg1:
                current_background = bg2
                current_orig_width = bg2_orig_width
                current_orig_height = bg2_orig_height
            else:
                current_background = bg1
                current_orig_width = bg1_orig_width
                current_orig_height = bg1_orig_height
        
        # Update pulse factor for glowing effect
        if pulse_growing:
            pulse_factor += pulse_speed * clock.get_time()  # Time-based pulsing
            if pulse_factor >= pulse_max_scale:
                pulse_factor = pulse_max_scale
                pulse_growing = False
        else:
            pulse_factor -= pulse_speed * clock.get_time()
            if pulse_factor <= pulse_min_scale:
                pulse_factor = pulse_min_scale
                pulse_growing = True
        
        # Calculate new size for pulsing effect
        new_width = int(current_orig_width * pulse_factor)
        new_height = int(current_orig_height * pulse_factor)
        
        # Scale the background
        scaled_bg = pygame.transform.scale(current_background, (new_width, new_height))
        
        # Calculate position to keep centered
        bg_x = (SCREEN_WIDTH - new_width) // 2
        bg_y = (SCREEN_HEIGHT - new_height) // 2
                
        # Update notes
        for note in notes:
            note.update()
            
        # Check for overlapping notes and adjust their positions
        for i, note in enumerate(notes):
            if not note.active:
                continue
                
            for j, other_note in enumerate(notes):
                if i != j and other_note.active and note.overlaps_with(other_note):
                    # Move the second note further up to avoid overlap
                    other_note.y = note.y - other_note.height - 150
        
        # Reset notes that have been hit after a delay
        reset_timer += 1
        if reset_timer >= 60:  # Reset every 60 frames (about a second)
            reset_timer = 0
            for note in inactive_notes:
                note.reset()
                
                # Make sure the reset note doesn't overlap with others in its lane
                for other_note in notes:
                    if note != other_note and note.overlaps_with(other_note):
                        # Move it further up
                        note.y = other_note.y - note.height - 150
                        
            inactive_notes = []
            
        # Draw everything
        screen.blit(scaled_bg, (bg_x, bg_y))
        
        # Draw lane dividers
        for i in range(1, NUM_LANES):
            x = i * LANE_WIDTH
            pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, SCREEN_HEIGHT), 2)
        
        # Draw hit zones with highlighting
        for i in range(NUM_LANES):
            x = i * LANE_WIDTH
            
            # Draw highlight if active
            if lane_highlights[i] > 0:
                # Create semi-transparent highlight that covers the whole lane
                highlight_surface = pygame.Surface((LANE_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                highlight_color = (255, 255, 255, 50)  # White with 20% alpha
                highlight_surface.fill(highlight_color)
                screen.blit(highlight_surface, (x, 0))
                
                # Create more visible highlight at the hit zone
                hit_zone_highlight = pygame.Surface((LANE_WIDTH, hit_zone_height), pygame.SRCALPHA)
                hit_zone_color = (255, 255, 255, 100)  # White with 40% alpha
                hit_zone_highlight.fill(hit_zone_color)
                screen.blit(hit_zone_highlight, (x, hit_zone_y))
                
                # Decrease the highlight counter
                lane_highlights[i] -= 1
            
            # Always draw the hit zone outline
            pygame.draw.rect(screen, (255, 0, 0), 
                           (x, hit_zone_y, LANE_WIDTH, hit_zone_height), 2)
        
        # Draw notes
        for note in notes:
            note.draw()
        
        # Draw score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # Draw key hints at the bottom
        hint_font = pygame.font.SysFont(None, 24)
        keys = ["D", "F", "J", "K"]
        for i, key in enumerate(keys):
            key_text = hint_font.render(key, True, (255, 255, 255))
            key_x = i * LANE_WIDTH + LANE_WIDTH // 2 - key_text.get_width() // 2
            screen.blit(key_text, (key_x, SCREEN_HEIGHT - 30))
            
        pygame.display.update()
        clock.tick(60)
    
def menu():
    # Fill screen with a color to test rendering
    screen.fill((30, 0, 60))
    
    # Add some stars to the menu background
    for _ in range(100):
        x = random.randint(0, SCREEN_WIDTH-1)
        y = random.randint(0, SCREEN_HEIGHT-1)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
    
    # Draw title
    title_font = pygame.font.SysFont(None, 80)
    title_text = title_font.render("AstroBeats", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
    screen.blit(title_text, title_rect)
    
    # Draw instructions
    font = pygame.font.SysFont(None, 36)
    text = font.render("Click or Press Space to Start", True, (200, 200, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(text, text_rect)
    
    # Draw controls info
    controls_font = pygame.font.SysFont(None, 24)
    controls_text = controls_font.render("Controls: D, F, J, K or 1, 2, 3, 4", True, (180, 180, 255))
    controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
    screen.blit(controls_text, controls_rect)
    
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Trigger the game start on a discrete mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
            # Also allow keyboard to start
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    
    # Start the main game
    main()

# Start with the menu
if __name__ == "__main__":
    menu()