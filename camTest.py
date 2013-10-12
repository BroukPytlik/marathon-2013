#!/usr/bin/env python2

# Camera input
# Author: Jan Tulak (jan@tulak.me)

#from CamControl import CamControl,Moves;

from cv2 import cv
from CamControl import CamControl,Camera
from multiprocessing import Process, Pipe
import time

"Will start the camera control"
def worker(conn):
    control = CamControl(conn);
    control.run();


"Draw matrix"
def drawInput(matrix):
    matrix_size = len(matrix)
    
    font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 3, 8) 
    mat = cv.CreateImage((640,480), cv.IPL_DEPTH_8U, 3)
    cv.Set(mat,(200,200,200))
    
    w = mat.width/matrix_size
    h = mat.height/matrix_size
    
    for x in range(matrix_size):
        "draw horizontal line"
        cv.Line(mat,(w*x,0),(w*x,mat.height),(0,0,255))
        for y in range(matrix_size):
            "draw vertical line"
            cv.Line(mat,(0,h*y),(mat.width,h*y),(0,0,255))
            "draw value"
            value = "#" if matrix [x][y] else ""
                       
            cv.PutText(
                       mat,
                       value, 
                       (
                        ( (w*(x+1))-w/2-40 ),
                        ( (h*(y+1))-h/2 )
                        ),
                       font,(0,0,0))
    
    cv.ShowImage("M", mat)


""" ----------------- """

"Create pipe"
parent_conn, child_conn = Pipe()
"create process"
p = Process(target=worker, args=(child_conn,))
"start it"
p.start()

"Create window for the matrix"
cv.NamedWindow("M", cv.CV_WINDOW_AUTOSIZE)

i=0;
reply=""
while True:
    time.sleep(0.1)
    reply = ""
    c = cv.WaitKey(10)& 255
    "detect if a key was pressed"
    
    
    if c != 255:
        "A key was pressed, so send its value" 
        parent_conn.send(("KEY",c))
    elif i % 2:
        "No key was pressed, so in odd cycles ask for status"
        parent_conn.send(("GET",["MOVE","MATRIX"]))
        #parent_conn.send(("GET",["MOVE"]))
    
    "Check if there is something in a queue"
    if parent_conn.poll():
        "Load it"
        recReply = parent_conn.recv()
        "Now check the reply..."
        if not isinstance(recReply, basestring) and len(recReply) == 2:
            "two elements - move and matrix"
            reply = recReply [0]
            matrix = recReply [1]
        elif not isinstance(recReply, basestring) and len(recReply) == 1:
            "one element but in list - move"
            reply = recReply [0]
            matrix = None
        else:
            "one string or number element"
            reply = recReply
            matrix = None
            
        "check the reply for exit"
        if isinstance(reply, basestring):
            if reply == "EXIT":
                break;
            
            elif len(reply) > 0:
                print "PARENT: ",reply       
            
        "Check and draw the matrix"
        if matrix != None:
            drawInput(matrix)
    
        
    "increment counter for odd/even cycles"
    i +=1
         
p.join()
