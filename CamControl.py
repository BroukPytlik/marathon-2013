# Camera input
# Author: Jan Tulak (jan@tulak.me)
#import cv
import numpy, time
from cv2 import cv
from Camera import Camera
from multiprocessing import Process, Pipe

class Moves (object):
    
    STAND = 0
    M_STAND = [
          [0,0,2,0,0],
          [0,1,1,1,0],
          [0,0,1,0,0],
          [0,1,1,1,0],
          [0,0,2,0,0]
          ]
    
    UP = 1
    M_UP = [
          [0,0,0,0,0],
          [0,0,0,0,0],
          [0,0,0,0,0],
          [0,2,2,2,0],
          [0,2,1,2,0]
          ]

    LEFT = 2
    M_LEFT = [
          [0,0,0,2,2],
          [0,0,0,2,2],
          [0,0,2,1,2],
          [0,0,2,1,2],
          [0,0,2,1,2]
          ]
    
    RIGHT = 3
    M_RIGHT = [
          [2,2,0,0,0],
          [2,2,0,0,0],
          [2,1,2,0,0],
          [2,1,2,0,0],
          [2,1,2,0,0]
          ]
    
    ATTACK_L = 4
    M_ATTACK_L = [
          [0,0,2,0,0],
          [0,0,2,2,0],
          [0,0,1,1,2],
          [0,0,1,2,0],
          [0,0,1,0,0]
          ]
    
    ATTACK_R = 5
    M_ATTACK_R = [
          [0,0,2,0,0],
          [0,2,2,0,0],
          [2,1,1,0,0],
          [0,2,1,0,0],
          [0,0,1,0,0]
          ]
    
    SPELL = 6
    M_SPELL = [
          [2,2,2,2,2],
          [2,1,1,1,2],
          [0,0,1,0,0],
          [0,0,1,0,0],
          [0,0,2,0,0]
          ]
    
    UP_RIGHT = 7
    M_UP_RIGHT = [
          [0,0,0,0,0],
          [0,0,0,0,0],
          [0,0,0,0,0],
          [2,2,2,0,0],
          [2,1,2,0,0]
          ]
    UP_LEFT  = 8
    M_UP_LEFT = [
          [0,0,0,0,0],
          [0,0,0,0,0],
          [0,0,0,0,0],
          [0,0,2,2,2],
          [0,0,2,1,2]
          ]
    
    
    def getMove(self,mat):
        movesTable = [True,True,True,True,True,True,True,True,True]
        #print mat
        for x in range(len(mat)):
            for y in range(len(mat)):
                
                if self.M_STAND[x][y] != mat[y][x] and self.M_STAND[x][y] != 2:
                    movesTable[self.STAND] = False
                    
                if self.M_UP[x][y] != mat[y][x] and self.M_UP[x][y] != 2:
                    movesTable[self.UP] = False
                    
                if self.M_LEFT[x][y] != mat[y][x] and self.M_LEFT[x][y] != 2:
                    movesTable[self.LEFT] = False
                    
                if self.M_RIGHT[x][y] != mat[y][x] and self.M_RIGHT[x][y] != 2:
                    movesTable[self.RIGHT] = False
                    
                if self.M_ATTACK_L[x][y] != mat[y][x] and self.M_ATTACK_L[x][y] != 2:
                    movesTable[self.ATTACK_L] = False
                    
                if self.M_ATTACK_R[x][y] != mat[y][x] and self.M_ATTACK_R[x][y] != 2:
                    movesTable[self.ATTACK_R] = False
                    
                if self.M_SPELL[x][y] != mat[y][x] and self.M_SPELL[x][y] != 2:
                    movesTable[self.SPELL] = False
                    
                if self.M_UP_RIGHT[x][y] != mat[y][x] and self.M_UP_RIGHT[x][y] != 2:
                    movesTable[self.UP_RIGHT] = False
                    
                if self.M_UP_LEFT[x][y] != mat[y][x] and self.M_UP_LEFT[x][y] != 2:
                    movesTable[self.UP_LEFT] = False

        "Now look for what move it is"
        for i in range(len(movesTable)):
            if movesTable[i]:
                return i;
        "If no move was found..."
        #return self.UNKNOWN
    
class CamControl(object):
    procConn = 0;
    
    font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 3, 8) 
        
    #cv.NamedWindow("Detection", cv.CV_WINDOW_AUTOSIZE)
    #cv.NamedWindow("Matrix", cv.CV_WINDOW_AUTOSIZE)
    
    matrix_size = 5;
    cam = Camera(matrix_size);
    
    
    matrixObjects =  [[0 for x in xrange(matrix_size)] for x in xrange(matrix_size)] ;
    
    
    
    RAW = 0;
    FILTERED = 1;
    OBJECTS = 2;    
    
    "what kind of values should be displayed?"
    showValueType = OBJECTS
    
    "What frame should be shown?"
    showFrameType = RAW
    
    def __init__(self,procConn):
        self.procConn = procConn
        #self.run()
    
    def objDetect(self,frame):
        diff = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
        result = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
        
        
        cv.AbsDiff(frame, self.cam.frameCalibrationSynced,diff)
        
        cv.InRangeS(diff,cv.Scalar(20,20,20), cv.Scalar(256,256,256), result)
        
        return result;
    
    def run(self):
        
        self.cam.calibrate();
        moves = Moves()
        i = 0;
        while True:
            c=-1
            if self.procConn != None and self.procConn.poll():
                (operation,value) = self.procConn.recv()
                if operation == "KEY":
                    c = value
                    if c == ord('g'):
                        print ("Switching grayscale/color")
                        self.cam.grayscale = not self.cam.grayscale
                    elif c == ord('e'):
                        print ("Switching canny (edge detection)")
                        self.cam.canny = not self.cam.canny
                    elif c == ord('c'):
                        print ("Calibrating...")
                        self.cam.calibrate();
                    elif c == ord('f'):
                        if self.showFrameType == self.RAW:
                            self.showFrameType = self.FILTERED;
                            print ("Displaying filtered frames.")
                        elif self.showFrameType == self.FILTERED:
                            self.showFrameType = self.OBJECTS;
                            print ("Displaying object detection frames.")
                        else:
                            self.showFrameType = self.RAW;
                            print ("Displaying raw frames.")
                    elif c == ord('d'):
                        if self.showValueType == self.RAW:
                            self.showValueType = self.FILTERED;
                            print ("Displaying filtered values.")
                        elif self.showValueType == self.FILTERED:
                            self.showValueType = self.OBJECTS;
                            print ("Displaying objects.")
                        elif self.showValueType == self.OBJECTS:
                            self.showValueType = self.RAW;
                            print ("Displaying raw values.")
                            
                    elif c == ord('n'):
                        print("Switching camera")
                        self.cam.camera_index = (self.cam.camera_index+1) % self.cam.cameras
                        self.cam.capture = cv.CaptureFromCAM(self.cam.camera_index)
                    elif c == ord('q'):
                        self.procConn.send(("EXIT",None))
                        exit(0)
                elif operation == "GET":
                    
                        reply =[]
                        for vType in value:
                            if vType == "MOVE":
                                "Test moves"
                                mv = moves.getMove(self.matrixObjects)
                                if mv == moves.LEFT:
                                    reply.append("LEFT")
                                elif mv == moves.RIGHT:
                                    reply.append("RIGHT")
                                elif mv == moves.ATTACK_L:
                                    reply.append("ATTACK LEFT")
                                elif mv == moves.ATTACK_R:
                                    reply.append("ATTACK RIGHT")
                                elif mv == moves.UP:
                                    reply.append("UP")
                                elif mv == moves.UP_LEFT:
                                    reply.append("UP LEFT")
                                elif mv == moves.UP_RIGHT:
                                    reply.append("UP RIGHT")
                                elif mv == moves.SPELL:
                                    reply.append("SPELL")
                                else:
                                    reply.append("")
                            elif vType=="MATRIX":
                                "sent matrix"
                                reply.append(self.matrixObjects)
                            else:
                                print("UNKNOWN GET MESSAGE")
                        #print reply
                        self.procConn.send(reply)
                    
            
            frame = self.cam.getFrame();
            self.findObjects(self.cam.matrixFiltered)
            #obj = self.objDetect(frame,0,numpy.median(frame[:,:]))
            if self.showFrameType == self.RAW:
                self.drawInput(self.cam.frameRaw)
            elif self.showFrameType == self.FILTERED: 
                f = cv.CreateImage(cv.GetSize(self.cam.frameCalibrationSynced), cv.IPL_DEPTH_8U,3)
                #cv.CvtColor(self.cam.frameCalibrationSynced, f, cv.CV_HLS2BGR)
                f = self.cam.frameCalibrationSynced;
                self.drawInput(f)
            else:
                #obj = self.objDetect(frame)
                self.drawInput(frame)
                
                
            if i < 5:
                i +=1
            if i == 4:
                self.cam.calibrate();
                print (".")
                
            #time.sleep(0.01)
            
    
    """
        Main cyclic function for getting frames
    """
   
    
    def drawInput(self,frame):
        w = frame.width/self.matrix_size
        h = frame.height/self.matrix_size
        
        mat = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
        cv.Copy(self.cam.frameRaw, mat)
        #cv.CvtColor(frame, out, cv.CV_GRAY2BGR)
        out = frame
        
        for x in range(self.matrix_size):
            "draw horizontal line"
            cv.Line(out,(w*x,0),(w*x,frame.height),(0,0,255))
            cv.Line(mat,(w*x,0),(w*x,frame.height),(0,0,255))
            for y in range(self.matrix_size):
                "draw vertical line"
                cv.Line(out,(0,h*y),(out.width,h*y),(0,0,255))
                cv.Line(mat,(0,h*y),(out.width,h*y),(0,0,255))
                "draw value"
                if self.showValueType == self.RAW:
                    value = str(self.cam.matrix [x][y])
                elif self.showValueType == self.FILTERED:
                    value = str(self.cam.matrixFiltered [x][y])
                elif self.showValueType == self.OBJECTS:
                    value = "#" if self.matrixObjects [x][y] else ""
                    
                    
                cv.PutText(
                           out,
                           value, 
                           (
                            ( (w*(x+1))-w/2-40 ),
                            ( (h*(y+1))-h/2 )
                            ),
                           #self.font,(255 if self.cam.matrix [x][y] < 128 else 0,0,0))
                           self.font,(128,0,0))
                           #self.font,(0,0,0))
                           
                cv.PutText(
                           mat,
                           value, 
                           (
                            ( (w*(x+1))-w/2-40 ),
                            ( (h*(y+1))-h/2 )
                            ),
                           self.font,(255 if self.cam.matrix [x][y] < 128 else 0,0,0))
                           #self.font,(0,0,255))
                           #self.font,(0,0,0))
        
        #cv.ShowImage("Detection", out)
        #cv.ShowImage("Matrix", mat)
        #return mat
        
    def findObjects(self,matrix):
        for x in range(self.matrix_size):
            for y in range(self.matrix_size):
                #print matrix[x][y]
                if matrix[x][y] >0 :
                    self.matrixObjects[x][y] = True
                    #print "object on ",x,", ",y
                else:
                    self.matrixObjects[x][y] = False
                
                
        
        