#!/usr/bin/python
import os,sys,pygame,random

# Name of application
appname='hangman'

# Build word pool
wordPool = 'ant baboon badger bat bear beaver camel cat clam cobra cougar coyote crow deer dog donkey duck eagle ferret fox frog goat goose hawk lion lizard llama mole monkey moose mouse mule newt otter owl panda parrot pigeon python rabbit ram rat raven rhino salmon seal shark sheep skunk sloth snake spider stork swan tiger toad trout turkey turtle weasel whale wolf wombat zebra'.split()

# Decalre game variables
incorrectLetters = ''
correctLetters = ''
gameOver = False
won = False

# Reset game variables
def reset():
	incorrectLetters = ''
	correctLetters = ''
	gameOver = False
	won = False
	secretWord = getRandomWord(wordPool)

# Get a random word from pool
def getRandomWord(wordPool):
	wordIndex = random.randint(0, len(wordPool) - 1)
	return wordPool[wordIndex]

# Display the hangman
def overlayHangman():
	incorrectLetterCount =  len(incorrectLetters)
	if incorrectLetterCount > 0:
		head = pygame.draw.circle(window, (0,0,0), (208,200), 14, 0)
	if incorrectLetterCount > 1:
		body = pygame.draw.line(window, (0,0,0), (208,214), (208,260), 8)
	if incorrectLetterCount > 2:
		arm1 = pygame.draw.line(window, (0,0,0), (188,250), (208,220), 8)
	if incorrectLetterCount > 3:
		arm2 = pygame.draw.line(window, (0,0,0), (228,250), (208,220), 8)
	if incorrectLetterCount > 4:
		leg1 = pygame.draw.line(window, (0,0,0), (183,300), (208,260), 8)
	if incorrectLetterCount > 5:
		leg1 = pygame.draw.line(window, (0,0,0), (233,300), (208,260), 8)

# Draw screen
def drawScreen(gameOver=False):
	# Prepare word to display
	blanks = '_' * len(secretWord)

	# Replace blanks with correctly guessed letters
	for i in range(len(secretWord)):
		if secretWord[i] in correctLetters:
			blanks = blanks[:i] + secretWord[i] + blanks[i+1:]
		elif gameOver and (won == False):
			blanks = secretWord

	# Fill background
	background = pygame.image.load(assets_dir+'bg.png')

	# Define fonts
	font = pygame.font.Font(assets_dir+'MIDDST.TTF', 56)
	font2 = pygame.font.Font(None, 24)

	# Display title	
	context = "Won" if won else "Lost"
	titleText = 'You '+context.title()+'!' if gameOver else appname.title()
	title = font.render(titleText, 1, (0, 0, 0))
	titlepos = title.get_rect().move(0,25)
	titlepos.centerx = background.get_rect().centerx
	background.blit(title, titlepos)

	# Display text on right hand side
	side1Text = 'Do you wish to play again? (y/n)' if gameOver else 'Pick a letter, try to guess the word...'
	side1 = font2.render(side1Text, 1, (255, 255, 255))
	side1pos = side1.get_rect().move(320,180)
	background.blit(side1, side1pos)

	side2color = (255,255,255) if (gameOver==False or won==True) else (255,0,0)
	side2 = font2.render(' '.join(blanks), 1, side2color)
	side2pos = side2.get_rect().move(320,220)
	background.blit(side2, side2pos)

	side3 = font2.render(incorrectLetters, 1, (0, 0, 0))
	side3pos = side3.get_rect().move(320,260)
	background.blit(side3, side3pos)

	# Blit everything to the window
	window.blit(background, (0, 0))

	# Apply hangman overlay objects
	overlayHangman()

	# Update display
	pygame.display.update()


# PyGame Config
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.init()

hangman_dir = os.path.dirname(os.path.realpath(__file__))+'/'
assets_dir = hangman_dir+'assets/'

i_icon = assets_dir+"icon.png"
icon = pygame.image.load(i_icon)
pygame.display.set_caption(appname.title(), i_icon)
pygame.display.set_icon(icon)

# Initialise the screen
window = pygame.display.set_mode((640, 480))

# Initialise our sounds
try:
	pygame.mixer.music.load(os.path.join(assets_dir, 'ambience.ogg'))
	correct = pygame.mixer.Sound(os.path.join(assets_dir,'phew.ogg'))
	incorrect = pygame.mixer.Sound(os.path.join(assets_dir,'rope-tighten.ogg'))
	dead = pygame.mixer.Sound(os.path.join(assets_dir,'dead.ogg'))
	alive = pygame.mixer.Sound(os.path.join(assets_dir,'yeehaw.ogg'))
except:
	raise UserWarning, "could not load or play soundfiles in 'data' folder :-("

pygame.mixer.music.play(-1)

secretWord = getRandomWord(wordPool)
drawScreen()

# Main loop
while True:
	# Check for pygame event
	for event in pygame.event.get():

		# Quit window event
		if event.type == pygame.QUIT: 
			sys.exit(0)

		# Keydown event
		elif event.type == pygame.KEYDOWN:
			# Get character from key id
			keyPressed = chr(event.key)

			# Game Over logic
			if gameOver:
				# Reset and play again
				if keyPressed == 'y':
					incorrectLetters = ''
					correctLetters = ''
					gameOver = False
					won = False
					secretWord = getRandomWord(wordPool)
					drawScreen()
				# Quit
				elif keyPressed == 'n':
					sys.exit(0) 

			# In game logic
			elif keyPressed in 'abcdefghijklmnopqrstuvwxyz':

				# Correct guess
				if keyPressed in secretWord:
					# Make sure this is a unique and new character
					if keyPressed not in correctLetters:
						correctLetters = correctLetters + keyPressed					
						foundAllLetters = True						
						for i in range(len(secretWord)):
							if secretWord[i] not in correctLetters:
								foundAllLetters = False
								break
					# Win logic
					if foundAllLetters:
						gameOver = True
						won = True
						alive.play()
					else:
						correct.play()

				# Incorrect guess
				elif keyPressed not in incorrectLetters:					
					incorrectLetters = incorrectLetters + keyPressed

					# Check if player has guessed too many times and lost
					if len(incorrectLetters) == 6:
						gameOver = True
						won = False
						dead.play()
					else:
						incorrect.play()

				# Draw contextual screen
				if gameOver:
					drawScreen(True)
				else:
					drawScreen()