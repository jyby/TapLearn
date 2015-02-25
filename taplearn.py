"""TapLearn

Once finished, <<<TapLearn>>> should be a generic example of pedagogical application with a touch interface, to be used to study the effect of various features on both persistence and learning. In its most basic version, the application downloads a sequence of predicates from a server, present them to the learner in a random order, each to be validated or refuted by the learner, gives feedback to the user and submits the user's answers to a central server for later studies. The features envisioned include the addition of animations, colors, sounds, spaced memorization techniques. The studies envisioned include the effect of those features on <<<persistence>>> (how frequently and how long the learner uses the application) and <<<learning>>> (how fast the learner progresses in his/her learning).
"""

VERSION = 0

import pygame
import random
import sys
try:
    import android
except ImportError:
    android = None

# Appearance
FPS = 30 # Number of frames per second
WIDTH = 480
HEIGHT = 800
backgroundColorWhenWaiting = (255, 255, 255, 255)
backgroundColorWhenCorrect = (0, 255, 0, 255)
backgroundColorWhenIncorrect = (255, 0, 0, 255)
textColorForQuestion = (10, 10, 10)
textColorForCorrectLabel = (10, 210, 10)
textColorForIncorrectLabel = (210, 10, 10)

# Difficulty
TIME_REWARD = 30
TIME_PENALTY = 60

# Questions
MIN_NUMBER = 5
MAX_NUMBER = 11
def Operation(x,y):
    return x*y
operationLabel = "*"

def newQuestion():
    """Returns a new question as a pair (predicate, correctness, comment)."""
    x = random.randint(MIN_NUMBER,MAX_NUMBER)
    y = random.randint(MIN_NUMBER,MAX_NUMBER)
    correctResult = Operation(x,y)
    proposedResult = noisyOperation(x,y)
    question = str(x)+" "+operationLabel+" "+str(y)+" = "+str(proposedResult)+" ?"
    comment = str(x)+" "+operationLabel+" "+str(y)+" = "+str(correctResult)
    return (question,proposedResult==correctResult,comment)

def noisyOperation(x, y):
    """Computes the operation correctly with probability 1/2,
    and with some minor error otherwise."""
    introducesAnError = random.choice([True,False])
    if not introducesAnError:
        return Operation(x,y)
    else:
        error = random.choice([-1,1])
        return random.choice([Operation((x+error),y),Operation(x,(y+error)),Operation(x,y+error)])

    
def gameLoop(screen):
    # Graphic preparation
    color = backgroundColorWhenWaiting
    font = pygame.font.Font(None, 64)
    LEGENDfont = pygame.font.Font(None, 72)

    # Choose a first question:
    (question, correctness, comment) = newQuestion()
    visibility_of_comment = False

    # Initialize the game:
    time_remaining = HEIGHT
    number_of_correct_answers = 0
    number_of_incorrect_answers = 0
    number_of_questions_asked = 1
    list_of_mistakes = []
    while time_remaining > 0:

        ev = pygame.event.wait()
        # Android-specific:
        if android:
            if android.check_pause():
                android.wait_for_resume()

        (x,y) = pygame.mouse.get_pos()
        # Draw the screen based on the timer.
        if ev.type == TIMEREVENT:
            time_remaining -= 1
            screen.fill(color)
            # WRITE True and False on bottom of screen.
            TRUEtext = LEGENDfont.render("TRUE", 1, textColorForCorrectLabel)
            TRUEpos = TRUEtext.get_rect()
            FALSEtext = LEGENDfont.render("FALSE", 1, textColorForIncorrectLabel)
            FALSEpos = TRUEtext.get_rect()
            TRUEpos.centerx = screen.get_rect().centerx + 100 
            TRUEpos.centery = HEIGHT - 20
            FALSEpos.centerx = screen.get_rect().centerx - 100 
            FALSEpos.centery = HEIGHT - 20
            screen.blit(TRUEtext, TRUEpos)
            screen.blit(FALSEtext, FALSEpos)

            # Scroll Question getting down
            POSITION = max(20,HEIGHT-time_remaining)
            text = font.render(question, 1, textColorForQuestion)
            textpos = text.get_rect()
            textpos.centerx = screen.get_rect().centerx
            textpos.centery = POSITION
            screen.blit(text, textpos)

            # See logo
            # screen.blit(logo,textpos)

            # Blit everything to the screen
            screen.blit(screen, (0, 0))
            pygame.display.flip()

            
        # When the touchscreen or a key is pressed, process the answer
        # take left side as true and right side as false.
        elif (ev.type == pygame.MOUSEBUTTONDOWN and x>  WIDTH/2) or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_RIGHT):
            print("Left Click")
            if correctness:
                print("Correct Answer!")
                number_of_correct_answers += 1
                color = backgroundColorWhenCorrect
                time_remaining += TIME_REWARD
            else:
                print("INCORRECT Answer!")
                color = backgroundColorWhenIncorrect
                number_of_incorrect_answers += 1
                time_remaining -= TIME_PENALTY
                list_of_mistakes.append((question,comment))
            (question, correctness, comment) = newQuestion()
            number_of_questions_asked += 1
        elif (ev.type == pygame.MOUSEBUTTONDOWN and x<=WIDTH/2)  or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_LEFT):
            print("Right Click")
            if not correctness:
                print("Correct Answer!")
                color = backgroundColorWhenCorrect
                number_of_correct_answers += 1
                time_remaining += TIME_REWARD
            else:
                print("INCORRECT Answer!")
                color = backgroundColorWhenIncorrect
                number_of_incorrect_answers += 1
                time_remaining -= TIME_PENALTY
                list_of_mistakes.append((question,comment))
            (question, correctness, comment) = newQuestion()
            number_of_questions_asked += 1
            
        # When it's released, change back the color of the background 
        elif ev.type == pygame.MOUSEBUTTONUP or ev.type == pygame.KEYUP:
            color = backgroundColorWhenWaiting

        # When the user hits back, ESCAPE is sent. Handle it and end
        # the game.
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            break
    print("Nb of questions asked: "+str(number_of_questions_asked))
    print("Nb of questions not answered: "+str(number_of_questions_asked-number_of_incorrect_answers-number_of_correct_answers))
    print("Nb of correct answers: "+str(number_of_correct_answers))
    print("Nb of incorrect answers: "+str(number_of_incorrect_answers))
    print("Predicates to review: ")
    for predicate,comment in list_of_mistakes:
        print("When asked '"+predicate+"', you should answer '"+comment+"'.")


def menuLoop(screen):
    mode = "waiting"

    while mode == "waiting":

        ev = pygame.event.wait()
        # Android-specific:
        if android:
            if android.check_pause():
                android.wait_for_resume()

        screen.fill(backgroundColorWhenWaiting)

        # WRITE NEW GAME and RESUME GAME on center of screen.
        font = pygame.font.Font(None, 64)

        text = font.render("NEW GAME", 1, textColorForCorrectLabel)
        pos = text.get_rect()
        pos.centerx = screen.get_rect().centerx  
        pos.centery = screen.get_rect().centery-100        
        screen.blit(text, pos)

        # text = font.render("RESUME GAME", 1, textColorForCorrectLabel)
        # pos = text.get_rect()
        # pos.centerx = screen.get_rect().centerx  
        # pos.centery = screen.get_rect().centery+100        
        # screen.blit(text, pos)

        # Blit everything to the screen
        screen.blit(screen, (0, 0))
        pygame.display.flip()
            
        # When the touchscreen or a key is pressed,
        # start the game
        if (ev.type == pygame.MOUSEBUTTONDOWN) or (ev.type == pygame.KEYDOWN and ev.key != pygame.K_ESCAPE):
            mode = "play"
        # When the user hits back, ESCAPE is sent. Handle it and end
        # the game.
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            mode = "exit"
    return mode
            
# Main program 
TIMEREVENT = pygame.USEREVENT    
def main():
    """Main function of the game, directly called by Android."""

    # PyGame initialisation
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('TapLearn: Prototype '+str(VERSION))
    pygame.time.set_timer(TIMEREVENT, 1000 / FPS)

    # PyGame Android initialisation
    if android:
        android.init()

    # SETUP for both Linux and Android:
    if android:
        android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
        print("UNDER ANDROID: Type 'BACK' to escape")
    print("UNDER LINUX: Type 'escape' to escape")

    mode="play"
    while mode=="play":
        mode = menuLoop(screen)
        if mode != "exit":
            gameLoop(screen)

    print("GAME (is) OVER")

        
# This isn't run on Android.
# This to execute in Linux.
if __name__ == "__main__":
    main()
