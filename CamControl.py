# Camera input
# Author: Jan Tulak (jan@tulak.me)
#import cv
from cv2 import cv
from Camera import Camera;
import numpy

class CamControl(object):
    font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 3, 8) 
        
    cv.NamedWindow("Detection", cv.CV_WINDOW_AUTOSIZE)
    cv.NamedWindow("Matrix", cv.CV_WINDOW_AUTOSIZE)
    
    matrix_size = 7;
    cam = Camera(matrix_size);
    
    
    matrixObjects =  [[0 for x in xrange(matrix_size)] for x in xrange(matrix_size)] ;
    
    
    
    RAW = 0;
    FILTERED = 1;
    OBJECTS = 2;    
    
    "what kind of values should be displayed?"
    showValueType = OBJECTS
    
    "What frame should be shown?"
    showFrameType = RAW
    
    def objDetect(self,frame):
        diff = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
        result = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
        
        #imgHSV = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,3)
        #cv.CvtColor(frame, imgHSV, cv.CV_BGR2HSV)
        
        cv.AbsDiff(frame, self.cam.frameCalibrationSynced,diff)
        
        cv.InRangeS(diff,cv.Scalar(20,20,20), cv.Scalar(256,256,256), result)
        
        return result;
    
    def run(self):
        self.cam.calibrate();
        i = 0;
        while True:
            frame = self._repeat()
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
            
    
    """
        Main cyclic function for getting frames
    """
    def _repeat(self):
        frame = self.cam.getFrame();
        #self.cam.matrix = self.cam.computeMatrix(frame);
            
        c = cv.WaitKey(10)& 255
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
            exit(0)
        
        return frame;
    
    def drawInput(self,frame):
        w = frame.width/self.matrix_size
        h = frame.height/self.matrix_size
        
        out = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
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
                    value = self.matrixObjects [x][y]
                    
                    
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
                           #self.font,(255 if self.cam.matrix [x][y] < 128 else 0,0,0))
                           self.font,(0,0,255))
                           #self.font,(0,0,0))
                           
        cv.ShowImage("Detection", out)
        cv.ShowImage("Matrix", mat)
        
    def findObjects(self,matrix):
        for x in range(self.matrix_size):
            for y in range(self.matrix_size):
                #print matrix[x][y]
                if matrix[x][y] >0 :
                    self.matrixObjects[x][y] = "#"
                    #print "object on ",x,", ",y
                else:
                    self.matrixObjects[x][y] = ""
                
                
        
        