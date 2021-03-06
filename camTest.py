#!/usr/bin/env python2

# Camera input
# Author: Jan Tulak (jan@tulak.me)

#from CamControl import CamControl,Moves;

from cv2 import cv
from CamControl import CamControl,Camera
from multiprocessing import Process, Pipe
import time

"Will start the camera control"
def _startCamera(conn):
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
camera_conn, camera_child_conn = Pipe()
"create process"
p = Process(target=_startCamera, args=(camera_child_conn,))
"start it"
p.start()

"Create window for the matrix"
cv.NamedWindow("M", cv.CV_WINDOW_AUTOSIZE)

i=0;
reply=""
mtime = 0;
while True:
    time.sleep(0.1)
    reply = ""
    c = cv.WaitKey(10)& 255
    "detect if a key was pressed"
    
    
    send_time = int(round(time.time() * 1000))
    if c != 255:
        "A key was pressed, so send its value" 
        camera_conn.send(("KEY",c))
    elif i % 2:
        "No key was pressed, so in odd cycles ask for status"
        camera_conn.send(("GET",["MOVE","MATRIX"]))
        #camera_conn.send(("GET",["MOVE"]))
    
    "Check if there is something in a queue"
    if camera_conn.poll():
        "Load it"
        recReply = camera_conn.recv()
        rec_time = int(round(time.time() * 1000))
        "Now check the reply..."
        if not isinstance(recReply, basestring) and len(recReply) == 3:
            "two elements - move and matrix"
            reply = recReply ["move"]
            matrix = recReply ["matrix"]
            mtime = recReply ["time"]
        elif not isinstance(recReply, basestring) and len(recReply) == 2:
            "one element but in list - move"
            reply = recReply ["move"]
            matrix = None
            mtime = recReply ["time"]
        else:
            "one string or number element"
            reply = recReply
            matrix = None
            
        "check the reply for exit"
        if isinstance(reply, basestring):
            if reply == "EXIT":
                break;
            
            elif len(reply) > 0:
                print "PARENT (delay to receive: ",(rec_time-mtime),"): ",reply       
            
        "Check and draw the matrix"
        if matrix != None:
            drawInput(matrix)
    
        
    "increment counter for odd/even cycles"
    i +=1
         
p.join()
