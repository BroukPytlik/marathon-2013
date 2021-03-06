#Hra o tom, jak odporny kralik skladal hudbu

import pygame, tmx,time
from CamControl import CamControl#,#Moves 
from multiprocessing import Process, Pipe
from spell import Spell
#from timer import Timer



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
            
    def update(self, dt, game):
        self.image = self.imageSt[game.ani_state]
            
            
class Object(pygame.sprite.Sprite):
    image = None
    playing = 0
    def __init__(self,type, location, *groups):
        super(Object, self).__init__(*groups)
        
        self.image = pygame.image.load('Enemy/'+type+'/standing/1.png')
        
        self.some_counting = 0
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.sound = pygame.mixer.Sound('Enemy/'+type+'/sound.wav')
        
        self.imageSt = []
        self.imagePl = []
        
        for i in [0,1,2]:
            self.imageSt.append(pygame.image.load('Enemy/'+type+'/standing/'+str(i+1)+'.png'))
            self.imagePl.append(pygame.image.load('Enemy/'+type+'/playing/'+str(i+1)+'.png'))
        
    
    def update(self, dt, game):
        if self.playing > 0:
            self.playing -=1
            self.image = self.imagePl[game.ani_state]
        else:
            self.image = self.imageSt[game.ani_state]
            
            if self.rect.colliderect(game.player.rect.move(96,0)):
                if game.player.fighting == True:
                    self.sound.play()
                    self.playing = int(self.sound.get_length()*30)



class Trumpet(Object):
    def __init__(self, location, *groups):
        super(Trumpet, self).__init__("Trubka",location,*groups)
        
class Drum(Object):
    def __init__(self, location, *groups):
        super(Drum, self).__init__("Drum",location,*groups)


class Microphone(Object):
    def __init__(self, location, *groups):
        super(Microphone, self).__init__("Mikro",location,*groups)

class Guitar(Object):
    def __init__(self, location, *groups):
        super(Guitar, self).__init__("Guitar",location,*groups) 
       
class Kitty(pygame.sprite.Sprite):
    image = pygame.image.load('Enemy/Kitty/1.png')
    def __init__(self, location, *groups):
        super(Kitty, self).__init__(*groups)
        self.some_counting = 0
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.sound = pygame.mixer.Sound('Enemy/Kitty/sound.wav').play()
        
        self.imageSt = []
        
        for i in [0,1,2]:
            self.imageSt.append(pygame.image.load('Enemy/Kitty/'+str(i+1)+'.png'))
        
    def update(self, dt, game):
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

        self.sound = pygame.mixer.Sound('Enemy/Cthulhu/sound.wav')
        self.image = self.image_walk_l[0]
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        # movement in the X direction; postive is right, negative is left
        self.direction = 1
        
    def update(self, dt, game):
        if self.rect.colliderect(game.player.rect.move(96,0)):
            if game.player.fighting == True and self.some_counting == 0:
                self.sound.play()
                self.some_counting = int(self.sound.get_length()*30) #time of the effect
        
        # move the enemy by 100 pixels per second in the movement direction
        self.rect.x += self.direction * 150 * dt
        
        if self.some_counting > 0:
            self.some_counting -=1
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
        
        self.caruje = False
        
        self.ani_magic_r = []
        self.ani_magic_l = []
        self.ani_jump_r = []
        self.ani_jump_l = []
        self.ani_fight_r = []
        self.ani_fight_l = []
        self.ani_walk_r = []
        self.ani_walk_l = []
        self.ani_stand_r = []
        self.ani_stand_l = []
        
        for i in [0,1,2]:
            self.ani_stand_r.append(pygame.image.load('Buneeh/Rstanding/'+str(i+1)+'.png'))
            self.ani_stand_l.append(pygame.image.load('Buneeh/Lstanding/'+str(i+1)+'.png'))
            self.ani_walk_r.append(pygame.image.load('Buneeh/Rwalking/'+str(i+1)+'.png'))
            self.ani_walk_l.append(pygame.image.load('Buneeh/Lwalking/'+str(i+1)+'.png'))
            self.ani_fight_r.append(pygame.image.load('Buneeh/Rfighting/'+str(i+1)+'.png'))
            self.ani_fight_l.append(pygame.image.load('Buneeh/Lfighting/'+str(i+1)+'.png'))
            self.ani_jump_r.append(pygame.image.load('Buneeh/Rjumping/'+str(i+1)+'.png'))
            self.ani_jump_l.append(pygame.image.load('Buneeh/Ljumping/'+str(i+1)+'.png'))
            self.ani_magic_r.append(pygame.image.load('Buneeh/Rmagic/'+str(i+1)+'.png'))
            self.ani_magic_l.append(pygame.image.load('Buneeh/Lmagic/'+str(i+1)+'.png'))
        
        

    def update(self, dt, game):
        last = self.rect.copy()

            
        #not doing anything     
        if self.resting:    
            if self.direction == 0:
                self.image = self.ani_stand_l[game.ani_state]
            else:
                self.image = self.ani_stand_r[game.ani_state]
        else:
            if self.direction == 0:
                self.image = self.ani_jump_l[game.ani_state]
            else:
                self.image = self.ani_jump_r[game.ani_state]  
           
        self.fighting = False
        #yes doing anything    
        key = pygame.key.get_pressed() 
        
        if not self.caruje: #because he shouldnt be doint anything while doing magic
            if key[pygame.K_LEFT] or game.reply == 'LEFT' or game.reply == 'UP LEFT':
                if self.resting and game.reply == 'UP LEFT':
                    self.dy = -1000
                self.rect.x -= 500 * dt
                self.direction = 0
                if self.resting:
                    self.image = self.ani_walk_l[game.ani_state]
                
            if key[pygame.K_RIGHT] or game.reply == 'RIGHT' or game.reply == 'UP RIGHT':
                if self.resting and game.reply == 'UP RIGHT':
                    self.dy = -1000
                self.rect.x += 500 * dt
                self.direction = 1
                if self.resting:
                    self.image = self.ani_walk_r[game.ani_state]
                
            if self.resting and (key[pygame.K_SPACE] or  game.reply == 'UP'):
                self.dy = -1000
                
            if key[pygame.K_LCTRL] or game.reply == 'ATTACK LEFT' or game.reply == 'ATTACK RIGHT':
                self.fighting = True
                if self.direction == 0:
                    self.image = self.ani_fight_l[game.ani_state]
                else:
                    self.image = self.ani_fight_r[game.ani_state]
                    
            if key[pygame.K_LALT] or game.reply == 'SPELL':
                self.caruje = True
                #spustime mariuv vec
                game.spell_conn.send('RECORD')
                
        else: #means caruje
            if game.spell_conn.poll():
                prijaty_spell = game.spell_conn.recv()
                print prijaty_spell
                self.caruje = False
                #tady tedy docaroval ze? ano docaroval, takze pridame veci ze? ano pridame veci
                if prijaty_spell == 0:
                    Kitty((self.rect.x, self.rect.y), game.actions)
                    
                elif prijaty_spell == 1:
                    Drum((self.rect.x, self.rect.y), game.actions)
                    
                elif prijaty_spell == 2:
                    Microphone((self.rect.x, self.rect.y), game.actions)
                    
                elif prijaty_spell == 3:
                    Guitar((self.rect.x, self.rect.y), game.actions)
                    
                elif prijaty_spell == 4:
                    Trumpet((self.rect.x, self.rect.y), game.actions)
                    
            
            if self.direction == 0:
                self.image = self.ani_magic_l[game.ani_state]
            else:
                self.image = self.ani_magic_r[game.ani_state]
                
            #zjistovani stavu kouzlici veci pro odmrznuti
                
                
            
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
    background = None
    tilemap = None
    ani_speed_init = 2
    some_counting_of_desired_delay_in_bunneeeehs_animation = 0
    ani_speed=ani_speed_init
    ani_max=2
    ani_state=0
    
    actions = None
    sprites = None
    player = None
    
    spell_conn = None
    spell_p = None
    camera_conn = None
    camera_p = None
    
    
    def __init__(self):
        self.background = pygame.image.load('background.png')
        self.tilemap = tmx.load('marathon.tmx', screen.get_size())
        #actions layer
        self.actions = tmx.SpriteLayer()
        self.tilemap.layers.append(self.actions)
        for x in self.tilemap.layers['triggers'].find('trumpet'):
            Trumpet((x.px, x.py-64), self.actions)
            
        for x in self.tilemap.layers['triggers'].find('enemy'):
            Enemy((x.px, x.py), self.actions)
            
        for x in self.tilemap.layers['triggers'].find('tardis'):
            Tardis((x.px, x.py-64), self.actions)
            
        for x in self.tilemap.layers['triggers'].find('drum'):
            Drum((x.px, x.py-64), self.actions)
            
        for x in self.tilemap.layers['triggers'].find('mic'):
            Microphone((x.px, x.py-64), self.actions)
            
        for x in self.tilemap.layers['triggers'].find('kytara'):
            Guitar((x.px, x.py-64), self.actions)

        self.sprites = tmx.SpriteLayer()
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tilemap.layers.append(self.sprites)
        
        "Create pipe"
        self.spell_conn, spell_child_conn = Pipe()
        "create process"
        self.spell_p = Process(target=_startSpell, args=(spell_child_conn,))
        "start it"
        self.spell_p.start()
        
        "Create pipe"
        self.camera_conn, camera_child_conn = Pipe()
        "create process"
        self.camera_p = Process(target=_startCamera, args=(camera_child_conn,))
        "start it"
        self.camera_p.start()
        
    #@profile
    def main(self, screen):
        clock = pygame.time.Clock()

        while 1:
            
            
            dt = clock.tick(30)
        
            self.some_counting_of_desired_delay_in_bunneeeehs_animation +=1
            if self.some_counting_of_desired_delay_in_bunneeeehs_animation > self.ani_speed_init:
                self.some_counting_of_desired_delay_in_bunneeeehs_animation = 0
                self.ani_state+=1
                if self.ani_state > self.ani_max:
                    self.ani_state=0
                    
                    
            self.camera_conn.send(("GET",["MOVE"])) # honzovo      
            if self.camera_conn.poll():    
                recReply = self.camera_conn.recv()
                rec_time = int(round(time.time() * 1000))
                self.reply = recReply ["move"]
                if self.reply != "":
                    print "delay to receive: ",(rec_time-recReply ["time"])," - ",self.reply
            

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    print "exiting..."
                    self.camera_conn.send(("KEY",ord('q') )) #vypinani honzove veci
                    self.spell_conn.send('EXIT')
                    self.camera_p.join()
                    self.spell_p.join()
                    return
                

            self.tilemap.update(dt / 1000., self)
            screen.blit(self.background, (0, 0))
            self.tilemap.draw(screen)
            pygame.display.flip()

            if self.player.is_dead:
                print 'YOU DIED'
                return

def _startCamera(conn):
    control = CamControl(conn);
    control.run();
        
def _startSpell(conn):
    spell = Spell(conn)
    spell.main()
    
        

if __name__ == '__main__':
    
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    game = Game()
    game.main(screen)

