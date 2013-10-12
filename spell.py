#!/usr/bin/env python2
# -*- coding: utf-8 -*-
 
# skript cte soubor "zaznam.wav", nema zadny parametr, v pripade shody
# melodie se vzorem je vracen kod kouzla, jinak nula a nebo chybovy
# kod
#
# kody kouzel:
#  1 = 7 6 4 2 4 (black tears)
#  2 = 8 10 11 10 8 7 (classico)
#  3 = 1 3 4 1 3 4 1 3 4 (blreaking the law - hrat od G(2|))
#  4 = 4 6 8 11 9 8 6 (one more magic potion, end of fast part)
#
# chybove kody:
#  -1 - nelze otevrit soubor zaznamu
#
# cokoli dulezite bude tady:
# a=1, a#=2, b=3, c=4, c#=5, d=6, d#=7, e=8, f=9, f#=10, g=11, g#=12
#
# zaznam .wav souboru:
# $ arecord -d 7 -f cd -t wav -D copy zaznam.wav
 
 
import wave, commands, time, numpy
from scipy import stats
from multiprocessing import Process, Pipe

class Spell:
    def __init__(self, conn):
        self.conn = conn
        
    def main(self):
        while True:
            recReply = self.conn.recv()
            if recReply == 'EXIT':
                exit()
            elif recReply == 'RECORD':
                #self.dummy()
                self.run()
                
            
    def dummy(self):
        time.sleep(2)
        self.conn.send(4)
    
    def run(self): 
        #arecord -d 7 -f cd -t wav -D copy zaznam.wav
        print 'ZACINAME NAHRAVAT:'        
        print commands.getoutput('arecord -d 7 -f cd -t wav zaznam.wav')
        # open up a wave
        try:
            wf=wave.open('zaznam.wav', 'rb')
        except:
            return -1
             
             
        chunk = 1024
        swidth=wf.getsampwidth()
        RATE=wf.getframerate()
        # use a Blackman window
        window=numpy.blackman(chunk)
        #enum tonu, viz nahore
        tone=0
        #shlukovani fragmentu, snaha nalezeni prechodu
        blok=[]
        i=0
        #seznam tonu melodie
        melody=[]
         
         
        # read some data
        sounddata=wf.readframes(chunk/2)
        # play stream and find the frequency of each chunk
        while len(sounddata)==chunk*swidth:
             
            # unpack the data and times by the hamming window
            indata=numpy.array(wave.struct.unpack("%dh"%(len(sounddata)/swidth), sounddata))*window
            # Take the fft and square each value
            fftData=abs(numpy.fft.rfft(indata))**2
            # find the maximum
            which=fftData[1:].argmax() + 1
            # use quadratic interpolation around the max
            if which!=len(fftData)-1:
                y0,y1,y2=numpy.log(fftData[which-1:which+2:])
                x1=(y2-y0)*.5/(2*y1-y2-y0)
                # find the frequency and output it
                fr=(which+x1)*RATE/chunk
            else:
                fr=which*RATE/chunk
                 
            #normalizace frekvence do rozsahu ~440/880
            if fr>50:
                while fr<430:
                    fr*=2
            while fr>905:
                fr/=2
             
            #zjisteni tonu frekvence
            if fr>=430 and fr<453:
                tone=1
            elif fr>=453 and fr<480:
                tone=2
            elif fr>=480 and fr<508:
                tone=3
            elif fr>=508 and fr<539:
                tone=4
            elif fr>=539 and fr<571:
                tone=5
            elif fr>=571 and fr<605:
                tone=6
            elif fr>=605 and fr<641:
                tone=7
            elif fr>=641 and fr<678:
                tone=8
            elif fr>=678 and fr<718:
                tone=9
            elif fr>=718 and fr<761:
                tone=10
            elif fr>=761 and fr<807:
                tone=11
            elif fr>=807 and fr<855:
                tone=12
             
            #zapis melodie
            blok.append(tone)
            if i<6:
                i+=1
            else:
                i=0
                mod=stats.mode(blok)
                if mod[1][0]>4:
                    if len(melody)>0:
                        tone=mod[0][0]
                        if melody[-1]!=tone:
                            melody.append(tone)
                    else:
                        melody.append(tone)
                else:
                    tone=0
                blok=[]
         
            # read some more data
            sounddata=wf.readframes(chunk/2)
         
         
        # stav je slozen z radku*10 a pozice noty indexovano od 1
        print melody
        while True:
            s=0
            for n in melody:
                if s==0 and n==7:
                    s=11
                elif s==11 and n==6:
                    s=12
                elif s==12 and n==4:
                    s=13
                elif s==13 and n==2:
                    s=14
                elif s==14 and n==4:
                    s=15
                    break
                 
                elif s==0 and n==8:
                    s=21
                elif s==21 and n==10:
                    s=22
                elif s==22 and n==11:
                    s=23
                elif s==23 and n==10:
                    s=24
                elif s==24 and n==8:
                    s=25
                elif s==25 and n==7:
                    s=26
                    break
                     
                elif s==0 and n==1:
                    s=31
                elif s==31 and n==3:
                    s=32
                elif s==32 and n==4:
                    s=33
                elif s==33 and n==1:
                    s=34
                elif s==34 and n==3:
                    s=35
                elif s==35 and n==4:
                    s=36
                elif s==36 and n==1:
                    s=37
                elif s==37 and n==3:
                    s=38
                elif s==38 and n==4:
                    s=39
                    break
                     
                elif s==0 and n==4:
                    s=41
                elif s==41 and n==6:
                    s=42
                elif s==42 and n==8:
                    s=43
                elif s==43 and n==11:
                    s=44
                elif s==44 and n==9:
                    s=45
                elif s==45 and n==8:
                    s=46
                elif s==46 and n==6:
                    s=47
                    break
                     
            if s==15 or s==26 or s==39 or s==47:
                break
            elif len(melody)<5:
                print "unknown melody"
                self.conn.send(0)
                return
            else:
                del melody[0]
        print melody 
        if s==15:
            print "black tears"
            self.conn.send(1)
            return
        elif s==26:
            print "classico"
            self.conn.send(2)
            return
        elif s==39:
            print "Breaking the law"
            self.conn.send(3)
            return
        elif s==47:
            print "One more magic potion"
            self.conn.send(4)
            return
        else:
            print "unknown melody"
            self.conn.send(0)
            return