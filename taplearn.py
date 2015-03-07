"""
TapLearn v1.0

By the end of the first phase of its development, <<<TapLearn>>> should be a generic example of pedagogical application with a touch interface, to be used to study the effect of various features on both persistence and learning. In its most basic version, the application downloads a sequence of predicates from a server, present them to the learner in a random order, each to be validated or refuted by the learner, gives feedback to the user and submits the user's answers to a central server for later studies. The features envisioned include the addition of animations, colors, sounds, spaced memorization techniques. The studies envisioned include the effect of those features on <<<persistence>>> (how frequently and how long the learner uses the application) and <<<learning>>> (how fast the learner progresses in his/her learning).

by Jeremy "Le JyBy" Barbay.



Simplified BSD License:

Copyright 2015 Jeremy Barbay. 

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY Jeremy Barbay ''AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Jeremy Barbay OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of Jeremy Barbay.
"""

VERSION = 2

import pygame
try:
    import android
except ImportError:
    android = None
import random
import sys

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
textColorForMenuEntry = (10, 210, 10)
textColorForDisabledMenuEntry = (210, 255, 210)

# Difficulty
TIME_REWARD = 30
TIME_PENALTY = HEIGHT

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

class Game:
    def __init__(self):
        self.time_remaining = HEIGHT
        self.time_remaining = HEIGHT
        self.number_of_correct_answers = 0
        self.number_of_incorrect_answers = 0
        self.number_of_questions_asked = 1
        self.list_of_mistakes = []
        (self.question, self.correctness, self.comment) = newQuestion()

    def stats(self):
        gameStats = ""
        gameStats += "Nb of questions asked: "+str(self.number_of_questions_asked)+"\n"
        gameStats += "Nb of questions not answered: "+str(self.number_of_questions_asked-self.number_of_incorrect_answers-self.number_of_correct_answers)+"\n"
        gameStats += "Nb of correct answers: "+str(self.number_of_correct_answers)+"\n"
        gameStats += "Nb of incorrect answers: "+str(self.number_of_incorrect_answers)+"\n"
        if len(self.list_of_mistakes)>0:
            gameStats += "Predicates to review: \n"
            for predicate,comment in self.list_of_mistakes:
                gameStats += "When asked '"+predicate+"', you should answer '"+comment+"'.\n"        
        return gameStats

def learnerAcceptsAnswer(ev,pygame):
    (x,y) = pygame.mouse.get_pos()
    return (
        (ev.type == pygame.MOUSEBUTTONDOWN and x > WIDTH/2)
        or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_RIGHT)    )
    
def learnerRefusesAnswer(ev,pygame):
    (x,y) = pygame.mouse.get_pos()
    return (
        (ev.type == pygame.MOUSEBUTTONDOWN and x <= WIDTH/2)
        or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_LEFT)    )



def gameLoop(screen,game):
    # Graphic preparation
    color = backgroundColorWhenWaiting
    font = pygame.font.Font(None, 64)
    LEGENDfont = pygame.font.Font(None, 72)

    def learnerIsCorrect():
        game.time_remaining += TIME_REWARD
        
    def learnerIsInCorrect(): 
        game.time_remaining -= TIME_PENALTY
        game.list_of_mistakes.append((game.question,game.comment))
       
    while game.time_remaining > 0:

        ev = pygame.event.wait()
        # Android-specific:
        if android:
            if android.check_pause():
                android.wait_for_resume()

        (x,y) = pygame.mouse.get_pos()
        # Draw the screen based on the timer.
        if ev.type == TIMEREVENT:
            game.time_remaining -= 1
            screen.fill(color)

            # DRAW True and False indicators on bottom of screen.
            iconThumbsUpDown = pygame.image.load('Buttons/icons-thumbDownUp-Width480.png').convert()
            buttonThumbsUpDown = iconThumbsUpDown.get_rect()
            buttonThumbsUpDown.bottom = HEIGHT
            buttonThumbsUpDown.centerx = screen.get_rect().centerx
            screen.blit(iconThumbsUpDown, buttonThumbsUpDown)

            # Scroll Question getting down
            POSITION = max(20,HEIGHT-game.time_remaining)
            text = font.render(game.question, 1, textColorForQuestion)
            textpos = text.get_rect()
            textpos.centerx = screen.get_rect().centerx
            textpos.centery = POSITION
            screen.blit(text, textpos)

            # Blit everything to the screen
            screen.blit(screen, (0, 0))
            pygame.display.flip()

            
        # When the touchscreen or a key is pressed, process the answer
        # take left side as true and right side as false.
        elif learnerAcceptsAnswer(ev,pygame):
            if game.correctness:
                game.number_of_correct_answers += 1
                color = backgroundColorWhenCorrect
                learnerIsCorrect()
            else:
                game.number_of_incorrect_answers += 1
                color = backgroundColorWhenIncorrect
                learnerIsInCorrect()
            (game.question, game.correctness, game.comment) = newQuestion()
            game.number_of_questions_asked += 1
        elif learnerRefusesAnswer(ev,pygame):
            if not game.correctness:
                color = backgroundColorWhenCorrect
                game.number_of_correct_answers += 1
                learnerIsCorrect()
            else:
                color = backgroundColorWhenIncorrect
                game.number_of_incorrect_answers += 1
                learnerIsInCorrect()
            (game.question, game.correctness, game.comment) = newQuestion()
            game.number_of_questions_asked += 1
            
        # When it's released, change back the color of the background 
        elif ev.type == pygame.MOUSEBUTTONUP or ev.type == pygame.KEYUP:
            color = backgroundColorWhenWaiting

        # When the learner hits back, ESCAPE is sent. Handle it and end
        # the game.
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            break
    if(game.time_remaining <=0):
        print(game.stats())
        game = None
    return game
    

def menuLoop(screen,game):
    mode = "waiting"
    tapPressed = None

    while mode == "waiting":

        ev = pygame.event.wait()
        # Android-specific:
        if android:
            if android.check_pause():
                android.wait_for_resume()

        screen.fill(backgroundColorWhenWaiting)

        # WRITE on Menu  screen.
        font = pygame.font.Font(None, 64)

        cursor_y = 0

        if tapPressed:
            logoTap = pygame.image.load('Logos/logo-TapWithFingerPressed-Width480.png').convert()
        else:
            logoTap = pygame.image.load('Logos/logo-TapWithFinger-Width480.png').convert()
        button_logoTap = logoTap.get_rect()
        button_logoTap.top = cursor_y
        button_logoTap.left = 0
        screen.blit(logoTap, button_logoTap)
        cursor_y += button_logoTap.height
        
        logoLearn = pygame.image.load('Logos/logo-Learn-Width480.png').convert()
        button_logoLearn = logoLearn.get_rect()
        button_logoLearn.top = cursor_y
        button_logoLearn.left = 0
        screen.blit(logoLearn, button_logoLearn)
        cursor_y += button_logoLearn.height

        icon_new_game = pygame.image.load('Buttons/icon-Start-Width480.png').convert()
        button_new_game = icon_new_game.get_rect()
        button_new_game.centerx = screen.get_rect().centerx  
        button_new_game.top = cursor_y
        screen.blit(icon_new_game, button_new_game)
        text_new_game = font.render("NEW", 1, textColorForMenuEntry)
        rect_new_game =  text_new_game.get_rect()
        rect_new_game.left = button_new_game.centerx
        rect_new_game.centery = button_new_game.centery
        screen.blit(text_new_game, rect_new_game)
        cursor_y += button_new_game.height

        icon_resume = pygame.image.load('Buttons/icon-Pause-Width480.png').convert()
        button_resume = icon_resume.get_rect()
        button_resume.centerx = screen.get_rect().centerx  
        button_resume.top = cursor_y
        screen.blit(icon_resume, button_resume)
        if(game):
            text_resume = font.render("RESUME", 1, textColorForMenuEntry)
        else:
            text_resume = font.render("RESUME", 1, textColorForDisabledMenuEntry)
        rect_resume =  text_resume.get_rect()
        rect_resume.left = button_resume.centerx
        rect_resume.centery = button_resume.centery
        screen.blit(text_resume, rect_resume)
        cursor_y += button_resume.height

        icon_quit = pygame.image.load('Buttons/icon-Exit-Width480.png').convert()
        button_quit = icon_quit.get_rect()
        button_quit.centerx = screen.get_rect().centerx  
        button_quit.top = cursor_y
        screen.blit(icon_quit, button_quit)
        text_quit = font.render("QUIT", 1, textColorForMenuEntry)
        rect_quit =  text_quit.get_rect()
        rect_quit.left = button_quit.centerx
        rect_quit.centery = button_quit.centery
        screen.blit(text_quit, rect_quit)
        cursor_y += button_quit.height            

        logoSignature = pygame.image.load('Logos/signature-byJyBy-tiny.png').convert()
        button_logoSignature = logoSignature.get_rect()
        button_logoSignature.bottom = HEIGHT
        button_logoSignature.right = WIDTH
        screen.blit(logoSignature, button_logoSignature)
        cursor_y += button_logoSignature.height



        # Blit everything to the screen
        screen.blit(screen, (0, 0))
        pygame.display.flip()
            
        if (ev.type == pygame.MOUSEBUTTONDOWN and  button_logoTap.collidepoint(pygame.mouse.get_pos())) or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_DOWN):
            tapPressed = 1
        elif (ev.type == pygame.MOUSEBUTTONUP) or (ev.type == pygame.KEYUP):
            tapPressed = None
        elif (ev.type == pygame.MOUSEBUTTONDOWN and  button_logoSignature.collidepoint(pygame.mouse.get_pos())):
            print("By Jeremy 'Le JyBy' Barbay")
        elif (ev.type == pygame.MOUSEBUTTONDOWN and  button_new_game.collidepoint(pygame.mouse.get_pos())) or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_RIGHT):
            game = Game();
            mode = "play"
        elif (game and (ev.type == pygame.MOUSEBUTTONDOWN and  button_resume.collidepoint(pygame.mouse.get_pos()))):
            mode = "play"
        elif (game and (ev.type == pygame.MOUSEBUTTONDOWN and  button_logoLearn.collidepoint(pygame.mouse.get_pos()))):
            print(str(game.stats()))
        elif ((ev.type == pygame.MOUSEBUTTONDOWN and  button_quit.collidepoint(pygame.mouse.get_pos())) or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE)):
            mode = "exit"
    return mode, game
            
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
    game = None
    while mode=="play":
        mode,game = menuLoop(screen,game)
        if mode != "exit":
            game = gameLoop(screen,game)

    print("GAME (is) OVER")

        
# This isn't run on Android.
# This to execute in Linux.
if __name__ == "__main__":
    main()
