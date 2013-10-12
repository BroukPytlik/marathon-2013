#Hra o tom, jak odporny kralik skladal hudbu

import pygame, tmx, glob
from CamControl import CamControl,Moves 
from multiprocessing import Process, Pipe

def worker(conn):
    control = CamControl(conn);
    control.run();

"Create pipe"
parent_conn, child_conn = Pipe()
"create process"
p = Process(target=worker, args=(child_conn,))
"start it"
p.start()

class Tardis(pygame.sprite.Sprite):
    image = pygame.image.load('Enemy/Tardis/1.png')
    def __init__(self, location, *groups):
        super(Tardis, self).__init__(*groups)
        self.some_counting = 0
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.sound = pygame.mixer.Sound('cat.wav')
        
        self.imageSt = []
        
        for i in [0,1,2]:
            self.imageSt.append(pygame.image.load('Enemy/Tardis/'+str(i+1)+'.png'))
            
            
class Trumpet(pygame.sprite.Sprite):
    image = pygame.image.load('Enemy/Trubka/standing/1.png')
    def __init__(self, location, *groups):
        super(Trumpet, self).__init__(*groups)
        self.some_counting = 0
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.sound = pygame.mixer.Sound('cat.wav')
        
        self.imageSt = []
        self.imagePl = []
        
        for i in [0,1,2]:
            self.imageSt.append(pygame.image.load('Enemy/Trubka/standing/'+str(i+1)+'.png'))
            self.imagePl.append(pygame.image.load('Enemy/Trubka/playing/'+str(i+1)+'.png'))
        
    
    def update(self, dt, game):
        if self.rect.colliderect(game.player.rect.move(96,0)):
            if game.player.fighting == True:
                self.some_counting = 40 #time of the effect
        
        if self.some_counting > 1:
            self.some_counting -=1
            self.cooldown = 1
            self.sound.play()
            self.image = self.imagePl[game.ani_state]
        else:
            self.image = self.imageSt[game.ani_state]
    
        

class Enemy(pygame.sprite.Sprite):
    def __init__(self, location, *groups):
        super(Enemy, self).__init__(*groups)
        self.some_counting = 0
        
        self.image_walk_l = []
        self.image_walk_r = []
        
        self.image_sing_l = []
        self.image_sing_r = []
        
        for i in [0,1,2]:
            self.image_walk_l.append(pygame.image.load('Enemy/Cthulhu/Lwalking/'+str(i+1)+'.png'))
            self.image_walk_r.append(pygame.image.load('Enemy/Cthulhu/Rwalking/'+str(i+1)+'.png'))
            
            self.image_sing_l.append(pygame.image.load('Enemy/Cthulhu/Lsinging/'+str(i+1)+'.png'))
            self.image_sing_r.append(pygame.image.load('Enemy/Cthulhu/Rsinging/'+str(i+1)+'.png'))

        self.sound = pygame.mixer.Sound('zelena-vec.wav')
        self.sound.play()
        self.image = self.image_walk_l[0]
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        # movement in the X direction; postive is right, negative is left
        self.direction = 1
        
    def update(self, dt, game):
        if self.rect.colliderect(game.player.rect.move(96,0)):
            if game.player.fighting == True:
                self.some_counting = 40 #time of the effect
        
        # move the enemy by 100 pixels per second in the movement direction
        self.rect.x += self.direction * 150 * dt
        
        if self.some_counting > 1:
            self.some_counting -=1
            self.cooldown = 1
            self.sound.play()
            if self.direction > 0:
                self.image = self.image_sing_r[game.ani_state]
            else:
                self.image = self.image_sing_l[game.ani_state]
        else:
            if self.direction > 0:
                self.image = self.image_walk_r[game.ani_state]
            else:
                self.image = self.image_walk_l[game.ani_state]
        
        
        
     
        
        # check all reverse triggers in the map to see whether this enemy has
        # touched one
        for cell in game.tilemap.layers['triggers'].collide(self.rect, 'reverse'):
            # reverse movement direction; make sure to move the enemy out of the
            # collision so it doesn't collide again immediately next update
            if self.direction > 0:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            break

        # check for collision with the player; on collision mark the flag on the
        # player to indicate game over (a health level could be decremented here
        # instead)
        # if self.rect.colliderect(game.player.rect):
        #    game.player.is_dead = True

class Player(pygame.sprite.Sprite):
    fighting = False
    def __init__(self, location, *groups):
        super(Player, self).__init__(*groups)
        self.image = pygame.image.load('bunnyR.gif')
        
        r_w = 40 #real width
        r_h = 160 #real height
        self.w_o = (200-r_w)/2 #width offset
        self.h_o = (200-r_h)/2 #height offset
        
        self.rect = pygame.rect.Rect(location, (r_w, r_h))
        
        self.resting = False
        self.dy = 0
        self.is_dead = False
        self.direction = 0 #coz je levo
        
        
        #Animations: 
        #1,2
        self.ani_stand_r = glob.glob("Buneeh/Rstanding/*.png")
        self.ani_stand_l = glob.glob("Buneeh/Lstanding/*.png")
        self.ani_stand_r.sort()
        self.ani_stand_l.sort()
        
        #3,4
        self.ani_walk_r = glob.glob("Buneeh/Rwalking/*.png")
        self.ani_walk_l = glob.glob("Buneeh/Lwalking/*.png")
        self.ani_walk_r.sort()
        self.ani_walk_l.sort()
        
        #5,6
        self.ani_fight_r = glob.glob("Buneeh/Rfighting/*.png")
        self.ani_fight_l = glob.glob("Buneeh/Lfighting/*.png")
        self.ani_fight_r.sort()
        self.ani_fight_l.sort()
        
        #7,8
        self.ani_jump_r = glob.glob("Buneeh/Rjumping/*.png")
        self.ani_jump_l = glob.glob("Buneeh/Ljumping/*.png")
        self.ani_jump_r.sort()
        self.ani_jump_l.sort()
        
        #9,10
        self.ani_magic_r = glob.glob("Buneeh/Rmagic/*.png")
        self.ani_magic_l = glob.glob("Buneeh/Lmagic/*.png")
        self.ani_magic_r.sort()
        self.ani_magic_l.sort()
        

    def update(self, dt, game):
        last = self.rect.copy()

            
        #not doing anything     
        if self.resting:    
            if self.direction == 0:
                self.image = pygame.image.load(self.ani_stand_l[game.ani_state])
            else:
                self.image = pygame.image.load(self.ani_stand_r[game.ani_state])
        else:
            if self.direction == 0:
                self.image = pygame.image.load(self.ani_jump_l[game.ani_state])
            else:
                self.image = pygame.image.load(self.ani_jump_r[game.ani_state])    
           
        self.fighting = False
        #yes doing anything    
        key = pygame.key.get_pressed() 
        
        
        
        if key[pygame.K_LEFT]:
        #if game.reply == 'LEFT' or game.reply == 'UP RIGHT':
         #   if game.reply == 'UP RIGHT':
          #      self.dy = -1000"""
            self.rect.x -= 500 * dt
            self.direction = 0
            if self.resting:
                self.image = pygame.image.load(self.ani_walk_l[game.ani_state])
            
        if key[pygame.K_RIGHT]:
        #if game.reply == 'RIGHT' or game.reply == 'UP RIGHT':
         #   if game.reply == 'UP RIGHT':
          #      self.dy = -1000
            self.rect.x += 500 * dt
            self.direction = 1
            if self.resting:
                self.image = pygame.image.load(self.ani_walk_r[game.ani_state])
            
        if self.resting and key[pygame.K_SPACE]:
        #if self.resting and game.reply == 'UP':
            self.dy = -1000
            
        if key[pygame.K_LCTRL]:
        #if game.reply == 'ATTACK LEFT' or game.reply == 'ATTACK RIGHT':
            self.fighting = True
            if self.direction == 0:
                self.image = pygame.image.load(self.ani_fight_l[game.ani_state])
            else:
                self.image = pygame.image.load(self.ani_fight_r[game.ani_state])
                
        if key[pygame.K_LALT]:
        #if game.reply == 'SPELL':
            Trumpet((self.rect.x, self.rect.y), game.actions) #spawnovani chlapka s trumetou 
            if self.direction == 0:
                self.image = pygame.image.load(self.ani_magic_l[game.ani_state])
            else:
                self.image = pygame.image.load(self.ani_magic_r[game.ani_state])
            
        
            
        self.dy = min(700, self.dy + 60)
        self.rect.y += self.dy * dt

        new = self.rect
        
        last2 = last.move(self.w_o,self.h_o)
        new2 = new.move(self.w_o,self.h_o)
        
        self.resting = False
        for cell in game.tilemap.layers['triggers'].collide(new2, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last2.right <= cell.left and new2.right > cell.left:
                new.right = cell.left-self.w_o
                
            if 'r' in blockers and last2.left >= cell.right and new2.left < cell.right:
                new.left = cell.right-self.w_o
                
            if 't' in blockers and last2.bottom <= cell.top and new2.bottom > cell.top:
                self.resting = True
                new.bottom = cell.top-self.h_o
                self.dy = 0
            if 'b' in blockers and last2.top >= cell.bottom and new2.top < cell.bottom:
                new.top = cell.bottom-self.h_o
                self.dy = 0

        game.tilemap.set_focus(new.x+96, new.y+200)

class Game(object):
    reply = 0
    def main(self, screen):
        clock = pygame.time.Clock()

        background = pygame.image.load('background.png')

        self.tilemap = tmx.load('marathon.tmx', screen.get_size())
        
        self.ani_speed_init = 2
        self.some_counting_of_desired_delay_in_bunneeeehs_animation = 0
        self.ani_speed=self.ani_speed_init
        self.ani_max=2
        self.ani_state=0
        
        #actions layer
        self.actions = tmx.SpriteLayer()
        self.tilemap.layers.append(self.actions)
        for trumpet in self.tilemap.layers['triggers'].find('trumpet'):
            Trumpet((trumpet.px, trumpet.py), self.actions)

        self.sprites = tmx.SpriteLayer()
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tilemap.layers.append(self.sprites)
        
        # add a separate layer for enemies so we can find them more easily later
        self.enemies = tmx.SpriteLayer()
        self.tilemap.layers.append(self.enemies)
        # add an enemy for each "enemy" trigger in the map
        for enemy in self.tilemap.layers['triggers'].find('enemy'):
            Enemy((enemy.px, enemy.py), self.enemies)

        
            
       

        while 1:
            dt = clock.tick(30)
            
            self.some_counting_of_desired_delay_in_bunneeeehs_animation +=1
            if self.some_counting_of_desired_delay_in_bunneeeehs_animation > self.ani_speed_init:
                self.some_counting_of_desired_delay_in_bunneeeehs_animation = 0
                self.ani_state+=1
                if self.ani_state > self.ani_max:
                    self.ani_state=0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    parent_conn.send(("KEY",ord('q') )) #vypinani honzove veci
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    parent_conn.send(("KEY",ord('q') )) #vypinani honzove veci
                    return
                
            parent_conn.send(("GET",["MOVE"])) # honzovo    
            if parent_conn.poll():
                "Load it"
                recReply = parent_conn.recv()
                self.reply = recReply [0]
                #print self.reply

            self.tilemap.update(dt / 1000., self)
            screen.blit(background, (0, 0))
            self.tilemap.draw(screen)
            pygame.display.flip()

            if self.player.is_dead:
                print 'YOU DIED'
                return

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    Game().main(screen)

