#!/usr/bin/python
import os,sys,pygame,random, shelve, getpass
from pygame.locals import *

# Name of application
app_name='hangman'

# Reset game variables
def reset():
	global incorrect_letters, correct_letters, game_over, won, secret_word, frame_count, milliseconds, modal, modal_context, target
	incorrect_letters = correct_letters = modal_context = ''
	game_over = won = modal = target = False
	secret_word = get_random_word()
	#print secret_word
	frame_count = milliseconds = 0

# Get a random word from wordlist file
def get_random_word():
	return random.choice(list(open(assets_dir+"wordlist.txt"))).strip()

# Display the hangman
def overlay_hangman():
	incorrect_letter_count =  len(incorrect_letters)
	if incorrect_letter_count > 0:
		head = pygame.draw.circle(window, (0,0,0), (208,200), 14, 0)
	if incorrect_letter_count > 1:
		body = pygame.draw.line(window, (0,0,0), (208,214), (208,260), 8)
	if incorrect_letter_count > 2:
		arm1 = pygame.draw.line(window, (0,0,0), (188,250), (208,220), 8)
	if incorrect_letter_count > 3:
		arm2 = pygame.draw.line(window, (0,0,0), (228,250), (208,220), 8)
	if incorrect_letter_count > 4:
		leg1 = pygame.draw.line(window, (0,0,0), (183,300), (208,260), 8)
	if incorrect_letter_count > 5:
		leg1 = pygame.draw.line(window, (0,0,0), (233,300), (208,260), 8)

# Display the modal
def overlay_modal():
	modal_window = pygame.draw.rect(window, (0,0,0), (10,10,620,460), 0)

	# Add modal title
	blit_text(modal_context.title(), (255, 255, 255), (0, 25), window, middst, True)

	if modal_context == 'submit_score':
		# Add sub-title
		blit_text("Type your name...", (255, 0, 0), (0, 95), window, font2, True)
		# Add text entry for name
		current_user_edit = current_user_temp + blinking_cursor
		blit_text(current_user_edit, (255, 0, 0), (0, 220), window, monospace, True)
		# Add footer
		blit_text("Press Enter to submit your score.  Press esc to skip and close.", (60, 60, 60), (0, 430), window, font2, True)

	if modal_context == 'scoreboards':
		score_pos_y = 150
		if (len(hi_scores.keys()) > 0):
			# If we only have a single score
			if (len(hi_scores.keys()) == 1):
				# Add sub-title
				blit_text(str(hi_scores.keys()[0])+" letter words", (255, 0, 0), (0, 95), window, font2, True)
				# Get scores based on word length
				single_score = hi_scores[hi_scores.keys()[0]][0]
				blit_text('01. ' + single_score[0] + ' - ' + single_score[1], (255, 255, 255), (50, score_pos_y), window, font2, True)
			# ... else we have multiple scores
			else:
				# Add sub-title
				blit_text(str(scoreboard_to_show_key)+" letter words", (255, 0, 0), (0, 95), window, font2, True)
				# Get scores based on word length
				for i, score in enumerate(scoreboard_to_show):			
					blit_text("{0:02}".format(i+1) + '. ' + score[0] + ' - ' + score[1], (255, 255, 255), (50, score_pos_y), window, font2, True)
					score_pos_y += 25				
		else:
			blit_text("It's looking pretty empty in here!", (255, 0, 0), (0, 95), window, font2, True)
		# Add footer
		blit_text("Use the mouse wheel to cycle scoreboards.  Press esc to close.", (60, 60, 60), (0, 430), window, font2, True)

def blink():
	global blinking_cursor
	blinking_cursor = '_' if blinking_cursor == ' ' else ' '

# Blit text to the screen
def blit_text(text, color, position, surface, font, centered=None):
	text_to_blit = font.render(text, 1, color)
	text_to_blit_position = text_to_blit.get_rect().move(position)
	if centered == True:
		text_to_blit_position.centerx = surface.get_rect().centerx
	surface.blit(text_to_blit, text_to_blit_position)

# Draw screen
def draw_screen():
	# Prepare word to display
	blanks = '_' * len(secret_word)

	# Replace blanks with correctly guessed letters
	for i in range(len(secret_word)):
		if secret_word[i] in correct_letters:
			blanks = blanks[:i] + secret_word[i] + blanks[i+1:]
		elif game_over and (won == False):
			blanks = secret_word

	# Fill background
	background = pygame.image.load(assets_dir+'bg.png').convert()

	# Show Volume and Score buttons if mouse is in window
	if pygame.mouse.get_focused():
		global volume
		sound_icon = ('sound-off.png' if play_sounds else 'sound-on-over.png') if (target == 'sound_switch') else ('sound-on.png' if play_sounds else 'sound-off.png')
		volume = pygame.image.load(assets_dir+sound_icon).convert_alpha()
		background.blit(volume, (570,438))
		score_icon = 'score-over.png' if (target == 'scoreboards') else 'score.png'
		score = pygame.image.load(assets_dir+score_icon).convert_alpha()
		background.blit(score, (600,438))

	# Display title	
	context = "Won" if won else "Lost"
	title_text = 'You '+context+'!' if game_over else app_name.title()
	blit_text(title_text, (0, 0, 0), (0, 25), background, middst, True)

	# Display text on right hand side
	blit_text('Do you wish to play again? (y/n)' if game_over else 'Pick a letter, try to guess the word...', (255, 255, 255), (320,180), background, font2)
	blit_text(' '.join(blanks), (255,255,255) if (game_over==False or won==True) else (255,0,0), (320,220), background, font2)
	blit_text(incorrect_letters, (0, 0, 0), (320,260), background, font2)

	# Timer
	# Calculate total seconds
	total_seconds = frame_count // frame_rate
	minutes = total_seconds // 60
	# Use modulus (remainder) to get seconds
	seconds = total_seconds % 60

	# Use python string formatting to format in leading zeros
	global time_text
	time_text = "{0:02}:{1:02}:{2:02}".format(minutes,seconds, milliseconds)
	if (frame_count > 0):
		time = font2.render(time_text,True,(60,60,60))
		background.blit(time, (490,440))

	# Blit what we have so far to the window
	window.blit(background, (0, 0))

	# Apply hangman overlay objects
	overlay_hangman()

	# Show the modal if applicable
	if modal == True:
		overlay_modal()

	# Update display
	pygame.display.update()

# Returns any objects of interest, currently under the cursor
def get_mouse_target():
	mouse_pos = pygame.mouse.get_pos()
	if pygame.Rect(570,438,24,24).collidepoint(mouse_pos):
		return 'sound_switch'
	if pygame.Rect(600,438,24,24).collidepoint(mouse_pos):
		return 'scoreboards'
	return None

# Define database class
class Database:
	# Initialise on load
	def init(self):
		data = self.open()

		if data:
			sound_settings = data['sound_settings']
			hi_scores = data['hi_scores']
			current_user = data['current_user']
		else:
			hi_scores = {}
			sound_settings = True
			current_user = getpass.getuser()

			# First run save			
			data['sound_settings'] = sound_settings
			data['hi_scores'] = hi_scores
			data['current_user'] = current_user

		data.close()

		return {'sound_settings': sound_settings, 'hi_scores': hi_scores, 'current_user': current_user}

	# Open db
	def open(self):
		return shelve.open(hangman_dir+'data.db')

	# Write to db
	def save(self, hi_scores):
		data = self.open()

		# If the scoreboard for this word length exists, append to it, then sort, then delete surplus entries... otherwise create a new list for this scoreboard
		if len(secret_word) in hi_scores:
			hi_scores[len(secret_word)].append([time_text, current_user])
			hi_scores[len(secret_word)].sort()
			if len(hi_scores[len(secret_word)]) > 10:
				hi_scores[len(secret_word)].pop()
		else:
			hi_scores[len(secret_word)] = [[time_text, current_user]]

		# Update db
		data['hi_scores'] = hi_scores

		data.close()

		return hi_scores

	# Save new sound settings
	def switch_sound(self, play_sounds):
		play_sounds = not play_sounds
		if play_sounds: pygame.mixer.music.play(-1)
		else: 
			pygame.mixer.music.stop()
			start.stop()
			alive.stop()
			correct.stop()
			incorrect.stop()
			dead.stop()
		data = self.open()
		data['sound_settings'] = play_sounds
		data.close()
		return play_sounds

# PyGame Config
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.init()

hangman_dir = os.path.dirname(os.path.realpath(__file__))+'/'
assets_dir = hangman_dir+'assets/'

i_icon = assets_dir+"icon.png"
icon = pygame.image.load(i_icon)
pygame.display.set_caption(app_name.title(), i_icon)
pygame.display.set_icon(icon)

# Define fonts
middst = pygame.font.Font(assets_dir+'middst.ttf', 56)
font2 = pygame.font.Font(None, 24)
monospace = pygame.font.SysFont("monospace", 60)

# Clock init
clock=pygame.time.Clock()
frame_rate = 42

# Custom timer events init
pygame.time.set_timer(USEREVENT+1, 500)
blinking_cursor = ' '

# Initialise the screen
window = pygame.display.set_mode((640, 480), pygame.DOUBLEBUF)
modal_window_w = modal_window_h = 0

# Create/read local portable database
db = Database()
data = db.init()

# Sound settings
play_sounds = data['sound_settings']

# Hi-Scores
# Load any existing scores from db
hi_scores = data['hi_scores']
# Grab the first available scoreboard, which gets displayed when accessing the scores modal
if len(hi_scores.keys()) > 0:
	scoreboard_to_show_key = hi_scores.iterkeys().next()
	scoreboard_to_show = hi_scores[scoreboard_to_show_key]
else:
	scoreboard_to_show_key = None
	scoreboard_to_show = None

# Get current game user
current_user = data['current_user']
current_user_temp = current_user

# Initialise our sounds
try:
	pygame.mixer.music.load(os.path.join(assets_dir, 'ambience.ogg'))
	start = pygame.mixer.Sound(os.path.join(assets_dir,'gong.ogg'))
	correct = pygame.mixer.Sound(os.path.join(assets_dir,'phew.ogg'))
	incorrect = pygame.mixer.Sound(os.path.join(assets_dir,'rope-tighten.ogg'))
	dead = pygame.mixer.Sound(os.path.join(assets_dir,'dead.ogg'))
	alive = pygame.mixer.Sound(os.path.join(assets_dir,'yeehaw.ogg'))
except:
	raise UserWarning, "could not load or play soundfiles in 'data' folder :-("

# Play background music
if play_sounds:
	pygame.mixer.music.play(-1)

# Begin game
reset()

# Start background music
if play_sounds:
	start.play()

# Main loop
while True:

	# Only run the timer after the first guess in a live game
	if (((len(incorrect_letters) > 0) or (len(correct_letters) > 0)) and (game_over == False)):
		frame_count += 1
		# Given that our fps is not 100, we need to use some frame_rate that is not exactly divisible by 100, to get some millisecond approximation in our calculation
		milliseconds = int((frame_count * 2.380952381) % 100) 
		# Limit to 20 frames per second
		clock.tick(frame_rate)

	# Draw screen
	draw_screen()

	# Get current mouse target
	target = get_mouse_target()

	# Check for pygame event
	for event in pygame.event.get():

		# Quit window event
		if event.type == pygame.QUIT:
			sys.exit(0)

		if event.type == USEREVENT+1:
			blink()

		# Process mouse click events
		elif event.type == pygame.MOUSEBUTTONDOWN:

			# Left mouse button
			if event.button == 1:
				# Clicked sound switch button
				if target == 'sound_switch':
					play_sounds = db.switch_sound(play_sounds)
				# Clicked scoreboards button
				if target == 'scoreboards':
					modal = True
					modal_context = 'scoreboards'

			# Scroll down
			if (event.button == 4) and (modal == True) and (modal_context == 'scoreboards') and (len(hi_scores.keys()) > 0):
				scoreboard_to_show_key = (scoreboard_to_show_key-1) if (scoreboard_to_show_key-1) in hi_scores else hi_scores.keys().pop()
				scoreboard_to_show = hi_scores[scoreboard_to_show_key]

			# Scroll up
			if (event.button == 5) and (modal == True) and (modal_context == 'scoreboards') and (len(hi_scores.keys()) > 0):
				scoreboard_to_show_key = (scoreboard_to_show_key+1) if (scoreboard_to_show_key+1) in hi_scores else hi_scores.iterkeys().next()
				scoreboard_to_show = hi_scores[scoreboard_to_show_key]

		# Keydown event (making sure our key id is within character evaluation range)
		elif ((event.type == pygame.KEYDOWN) and (event.key <= 256)):
			# Get character from key id
			key_pressed = chr(event.key)

			if modal == True:
				if (event.key == pygame.K_RETURN) and (modal_context == 'submit_score'):
					# Save Hi-Scores
					current_user = current_user_temp
					hi_scores = db.save(hi_scores)
					scoreboard_to_show_key = hi_scores.iterkeys().next()
					scoreboard_to_show = hi_scores[scoreboard_to_show_key]
					modal = False
					modal_context = ''
				elif (event.key == pygame.K_BACKSPACE) and (modal_context == 'submit_score'):
					current_user_temp = current_user_temp[:-1]
				elif key_pressed in 'abcdefghijklmnopqrstuvwxyz0123456789':
					current_user_temp = current_user_temp + key_pressed
				elif event.key == pygame.K_ESCAPE:
					current_user_temp = current_user
					modal = False
					modal_context = ''

			# Game Over logic
			elif game_over:
				# Reset and play again
				if key_pressed == 'y':
					reset()
					if play_sounds:
						start.play()
				# Quit
				elif key_pressed == 'n':
					sys.exit(0) 

			# In game logic
			elif key_pressed in 'abcdefghijklmnopqrstuvwxyz':

				# Correct guess
				if key_pressed in secret_word:
					# Make sure this is a unique and new character
					if key_pressed not in correct_letters:
						correct_letters = correct_letters + key_pressed
						found_all_letters = True
						for i in range(len(secret_word)):
							if secret_word[i] not in correct_letters:
								found_all_letters = False
								break
						# Win logic
						if found_all_letters:
							game_over = True
							won = True
							if play_sounds:
								alive.play()
							modal = True
							modal_context = 'submit_score'
						elif play_sounds:
								correct.play()

				# Incorrect guess
				elif key_pressed not in incorrect_letters:
					incorrect_letters = incorrect_letters + key_pressed

					# Check if player has guessed too many times and lost
					if len(incorrect_letters) == 6:
						game_over = True
						won = False
						if play_sounds:
							dead.play()
					elif play_sounds:
						incorrect.play()