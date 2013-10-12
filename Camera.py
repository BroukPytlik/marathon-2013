# Camera input
# Author: Jan Tulak (jan@tulak.me)
from cv2 import cv
import math,numpy

"Pass matrix size in constructor"

class Camera(object):
    camera_index = 0;
    cameras = 2;
    capture = 0;
    grayscale = False
    canny = False
    capture = None
    
    matrix_width = 0;
    matrix_height = 0;
    
    matrix =  0
    matrixFiltered =  0
    matrixCalibration =  0
    
    "Default size to avoid crash on adjCalibrationFrame"
    frameRaw = cv.CreateImage((40,40), cv.IPL_DEPTH_8U, 3);
    frameCalibration = cv.CreateImage((40,40), cv.IPL_DEPTH_8U, 3);
    frameCalibrationSynced = cv.CreateImage((40,40), cv.IPL_DEPTH_8U, 3);

    def __init__(self,matrix_size):
        self.matrix_width = matrix_size
        self.matrix_height = matrix_size
        self.matrix =  [[0 for x in xrange(self.matrix_width)] for x in xrange(self.matrix_height)] ;
        self.matrixFiltered =  [[0 for x in xrange(self.matrix_width)] for x in xrange(self.matrix_height)] ;
        self.matrixCalibration =  [[0 for x in xrange(self.matrix_width)] for x in xrange(self.matrix_height)] ;
        
        "Try find a camera "
        while self.capture == None and self.camera_index < self.cameras:
            try:
                self.capture = cv.CaptureFromCAM(self.camera_index)
            except Exception as e:
                print e
                self.capture = None
                self.camera_index += 1
        

    def objDetect(self,frame):
        if frame.height != self.frameCalibrationSynced.height:
            return frame;
        diff = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
        result = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
        
        #imgHSV = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,3)
        #cv.CvtColor(frame, imgHSV, cv.CV_BGR2HSV)
        
        cv.AbsDiff(frame, self.frameCalibrationSynced,diff)
        
        #cv.CvtColor(diff, diff, cv.CV_BGR2HSV)
        
        cv.InRangeS(diff,cv.Scalar(20,20,20), cv.Scalar(256,256,256), result)
        #cv.InRangeS(diff,cv.Scalar(20,20,50), cv.Scalar(256,256,256), result)
        
        return result;
    
    def ajdCalibrationFrame(self,frame):
        fc = cv.CreateImage(cv.GetSize(self.frameCalibration), cv.IPL_DEPTH_8U,3)
        cv.Copy(self.frameCalibration, fc)
        
        ff = frame
        
        hc = cv.CreateMat(fc.height, fc.width, cv.CV_8UC1)
        lc = cv.CreateMat(fc.height, fc.width, cv.CV_8UC1)
        sc = cv.CreateMat(fc.height, fc.width, cv.CV_8UC1)
        cv.Split(fc, hc, lc, sc, None)
        
        hf = cv.CreateMat(ff.height, ff.width, cv.CV_8UC1)
        lf = cv.CreateMat(ff.height, ff.width, cv.CV_8UC1)
        sf = cv.CreateMat(ff.height, ff.width, cv.CV_8UC1)
        cv.Split(ff, hf, lf, sf, None)
        
        self.syncChannel(hc, hf)
        self.syncChannel(lc, lf)
        self.syncChannel(sc, sf)
        cv.Merge(hc, lc, sc, None, fc)
        
        self.frameCalibrationSynced = fc
            
    "add/subtract to orig channel to be similar to wanted (based on top left corner)"
    def syncChannel(self,orig,wanted):
        oMed = numpy.median(orig[0:20,0:20])
        wMed = numpy.median(wanted[0:20,0:20])
        diff = (wMed - oMed)
        cv.AddS(orig, diff, orig)
        return orig

    def getFrame(self):
        frame = self.getRawFrame()
        self.ajdCalibrationFrame(frame)
        frame = self.objDetect(frame)
        self.matrix = self.computeMatrix(frame);
        self.matrixFiltered = self.getFilteredMatrix(self.matrix)
        return frame;
    
    def calibrate(self):
        frame = self.getRawFrame();
        self.frameCalibration  = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
        cv.Copy(frame, self.frameCalibration )
        #cv.CvtColor(frame, self.frameCalibration, cv.CV_BGR2HLS)
        self.matrixCalibration = self.computeMatrix(self.frameCalibration);
        print("New default matrix set.");
        print(self.matrixCalibration);
    

        "Get one frame from a camera"
    def getRawFrame(self):
        frame = cv.QueryFrame(self.capture)
        self.frameRaw = frame
       # print cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_SATURATION) 
        cv.Smooth(frame, frame)
        if self.grayscale:
            gray = cv.CreateImage(cv.GetSize(frame), frame.depth, 1)
            cv.CvtColor(frame, gray, cv.CV_RGB2GRAY)
            frame = gray
            
        
        if self.grayscale and self.canny:
            c = cv.CreateImage(cv.GetSize(frame), frame.depth, frame.channels)
            cv.Canny(frame, c, 10, 100, 3)
            frame = c
        return frame;
    
    
    "Compute median values for the matrix"
    def computeMatrix(self, frame):
        w = frame.width/self.matrix_width
        h = frame.height/self.matrix_height
        
        "Because the matrix has to be always synchronized, we have to compute it to another variable."
        m = [[0 for x in xrange(self.matrix_width)] for x in xrange(self.matrix_height)] 
        
        for x in range(self.matrix_width):
            for y in range(self.matrix_height):
                m[x][y]=math.floor(( numpy.median(frame[(h*y):(h*(y+1)),(w*x):(w*(x+1))])))
                
        return m;
    
    
    
    "Filter it - background values and so"
    def getFilteredMatrix(self,mat):
        m = [[0 for x in xrange(self.matrix_width)] for x in xrange(self.matrix_height)]
         
        for x in range(self.matrix_width):
            for y in range(self.matrix_height):
                m[x][y] = mat[x][y] - self.matrixCalibration[x][y]
        return m;
    