import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space invaders")

#Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#Player ship
YELLOW_SPACE_player = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

#Background
BG = RED_LASER = pygame.image.load(os.path.join("assets", "background-black.png"))
#draw, move, collision, shoot, coldown, etc are called methods
class Laser:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)
	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	def move(self, vel):
		self.y += vel

	def off_screen(self, height):
		return not (self.y <= height and self.y >= 0) #if it's off the screen I get true and if it's not I get False

	def collision(self, obj):
		return collide(self, obj)

class Ship:
	COOLDOWN = 30 #it's half a second because the FPS is 60
	def __init__(self, x, y, health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	def draw(self, window):
		window.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self, vel, obj): #vel-how fast we're going to move the lasers; obj-when we move these lasers we wanna check for collision with all of this objects
		#the idea of this method is to check if each laser has hit the player, this is gonna be used for the player and the enemy, but inside the player it will implement a new method called move_lasers, rather than checking if we hit the player, we'll check if we hit any enemies, that's why we need 2 separate move_lasers methods- one for checking if all of the lasers shot by the enemies hit the player and one for checking if all the lasers hit by the player have hit the enemies  
		#we're gonna move the lasers by this velocity
		#we call the cooldown which goes through its functions and we'll gonna increment the cooldown based on what we've defined there(if we can shoot or not) and then we'll move down the screen by the velocity, we'll check if it's off the screen(we'll remove it) and if not but it's collided with one of our objects(we'll remove it) each laser that we've shot that exists currently in out list 
		self.cooldown() #increment the cooldown_counter when we move the lasers(every time we move the lasers we're gonna call this once a frame, which means that we'll increment the cooldown_counter when we move the lasers so we can track if we can send another laser or not)
		for laser in self.lasers: #then loop through all the lasers and check if 
			laser.move(vel) #we'll move it by the velocity
			if laser.off_screen(HEIGHT): #if it's off the screen we'll remove it
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 100 #health decreases
				self.lasers.remove(laser) #we need to delete the laser

	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0: #else if
			self.cool_down_counter += 1

	def shoot(self):
		if self.cool_down_counter == 0: #we're not in the process of counting up to a specific cooldown or keeping track of how long until the next shot
			laser = Laser(self.x, self.y, self.laser_img) #create a new laser at this current location
			self.lasers.append(laser) #ad it to the lasers list
			self.cool_down_counter = 1 #set the cooldown counter to start counting up

	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height() 

class Player(Ship):
	def __init__(self, x, y, health=100):
		super().__init__(x, y, health)
		self.ship_img = YELLOW_SPACE_player
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img) #"mask"(pixel perfect collision)
		self.max_health = health #every player starts with a maximumn health

	def move_lasers(self, vel, objs): #vel-how fast we're going to move the lasers; obj-when we move these lasers we wanna check for collision with all of this objects
		#we wanna check if the player's lasers have hit any enemies
		#we call the cooldown which goes through its functions and we'll gonna increment the cooldown based on what we've defined there(if we can shoot or not) and then we'll move down the screen by the velocity, we'll check if it's off the screen(we'll remove it) and if not but it's collided with one of our objects(we'll remove it) each laser that we've shot that exists currently in out list 
		self.cooldown() #increment the cooldown_counter when we move the lasers(every time we move the lasers we're gonna call this once a frame, which means that we'll increment the cooldown_counter when we move the lasers so we can track if we can send another laser or not)
		for laser in self.lasers: #then loop through all the lasers and check if 
			laser.move(vel) #we'll move it by the velocity
			if laser.off_screen(HEIGHT): #if it's off the screen we'll remove it
				self.lasers.remove(laser)
			else:
				for obj in objs: #if it's not off the screen for each object in the object list if the laser has collideed with that object, remove it, otherwise remove the laser after that happens as well(checks if the lasers collides with every single enemy)
					if laser.collision(obj):
						objs.remove(obj)
						self.lasers.remove(laser)

	def draw(self, window):
		super().draw(window) #we called the parents draw method woth super
		self.healthbar(window) #and then the healthbar with the window

	def healthbar(self, window):
		pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
		pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10)) #tells us what percentage health we're currently at, what percentage of health we should draw the green rectangle at

class Enemy(Ship):
	COLOR_MAP = { #making a dictionary for the colors of the ship
		"red": (RED_SPACE_SHIP, RED_LASER),
		"green": (GREEN_SPACE_SHIP, GREEN_LASER),
		"blue": (BLUE_SPACE_SHIP, BLUE_LASER)
	}
	def __init__(self, x, y, color, health=100): #"red","green","blue"
		super().__init__(x, y, health)
		self.ship_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		self.y += vel

	def shoot(self):
		if self.cool_down_counter == 0: #we're not in the process of counting up to a specific cooldown or keeping track of how long until the next shot
			laser = Laser(self.x-20, self.y, self.laser_img) #create a new laser at this current location, #we did self.c-20 to substract the x value of where you're gonna start shooting the bullet from to make the lasers shoot from the center of the enemy
			self.lasers.append(laser) #ad it to the lasers list
			self.cool_down_counter = 1 #set the cooldown counter to start counting up

def collide(obj1, obj2): #offset tells us the distance between the top left corner of both of these objects(how far away object2 is from object1)
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None #(if they're not overlaping it will return None, if they are it will return a polar tuple- (x, y))

def main():
	run = True
	FPS = 60
	level = 0
	lives = 5
	main_font = pygame.font.SysFont("comicsans", 50)#the main font
	lost_font = pygame.font.SysFont("comicsans", 60)#the font for when we lose the game

	enemies = [] #store where our enemies are
	wave_lenght = 5 #every time we get to the next level we generate new enemies that start moving down the screen
	enemy_vel = 1 #the enemies will start moving down slowly based on a certain velocity

	player_vel = 5 #velocity
	laser_vel = 5

	player = Player(300, 630)

	clock = pygame.time.Clock()

	lost = False #we initialise it as false, so when we lose it becomes True
	lost_count = 0

	def redraw_window():#refresh images
	    WIN.blit(BG, (0,0))#take on of the images and draws it to the window at the top left corner of the screen
	    #draw text
	    lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
	    level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

	    WIN.blit(lives_label, (10, 10))
	    WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

	    for enemy in enemies:
	    	enemy.draw(WIN) #it works because enemies inherits from Ships, that has a draw method

	    player.draw(WIN)

	    if lost:
	    	lost_label =  lost_font.render("You lost!!", 1, (255,255,25))
	    	WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))#to make the text perfectly centered

	    pygame.display.update()

	while run:
		clock.tick(FPS)
		redraw_window()

		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		if lost: #if we have lost
			if lost_count > FPS * 3: #show the frame for 3 seconds
				run = False #quit the game after 3 seconds of showing "You lost!"
			else:
				continue #if we're still waiting to hit 3 seconds continue, which means it doesn't do any of the following instructions, it goes back to the beginning of the while run loop

		if len(enemies) == 0:
			level += 1 #get to the next level because we beat the enemies
			wave_lenght += 5 #we add 5 more enemies when we get to the next level
			for i in range(wave_lenght): #we spawn new enemies and append them to the enemy list and start moving them down
				#pick positions for them so they don't come down at the same time, so we want them to look like they come at different times
				enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(["red", "blue", "green"])) #they are positioned at different heights so that's why they won't come at the same time
				enemies.append(enemy)#add them to the enemy list

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()

		keys = pygame.key.get_pressed()#checking if we're pressing a key(if yes, we'll move in a certain direction, if not, we won't)
		if keys[pygame.K_a] and player.x - player_vel > 0: #left
			player.x -= player_vel #moves player_vel value px(in our case, 5px) to the left
		if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
			player.x += player_vel #moves player_vel px to the right
		if keys[pygame.K_w] and player.y - player_vel > 0: #up
			player.y -= player_vel
		if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: #down
			player.y += player_vel
		if keys[pygame.K_SPACE]: #if we hit the spacebar we'll call shoot which will create a new laser object
			player.shoot()

		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player) #move it by laser_vel and check if it's hit the player

			#making the enemies shoot, pick some probability that the enemies are gonna shoot
			if random.randrange(0, 2*60) == 1: #we want every second the enemy to have a probability of 50% of shooting- 2*60, cause we have 60 frames per seconds
				enemy.shoot()

			if collide(enemy, player):
				player.health -= 10
				enemies.remove(enemy)
			elif enemy.y + enemy.get_height() > HEIGHT:
				lives -=1
				enemies.remove(enemy)#remove the object(which is enemy) from the enemies list

		player.move_lasers(-laser_vel, enemies) #the entire list of enemies, it'll check if the laser has collided with any of the enemies
		#we need to make the velocity negatuve to make the lasers shoot upwards


def main_menu(): #this is the main menu, what shows before playing the game
	#we don't need the clock because we're not moving anything around
	title_font = pygame.font.SysFont("comicsans", 70)
	run = True
	while run:
		WIN.blit(BG, (0, 0))
		title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
		WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT: #if we press the X button we're gonna quit the game, it ends the game
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN: #if we press any of the mouse buttons enter the main loop and start playing the game, it will always bring me back to the main_menu function because since we call main() without setting run = False, when main() exits, when main)is done we go back into main_menu and wait until we hit the X button to stop playing the game
				main()
	pygame.quit()


main_menu()