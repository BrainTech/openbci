import numpy as np 
import cv as CV
import cv2 as cv
import sys, time



class Camera:
    def __init__(self):
        
        self.initConst()
        self.initCamVideo()
        self.setRef()

        #~ //~ Inicjuje okna do ogladania
        cv.namedWindow("original",0)
        #~ cv.namedWindow("threshold",0)
        cv.namedWindow("edge",0)

        # display orig image
        flag, self.img = self.cap.read()
        if flag == False:
            while(1): 
                flag, self.img = self.cap.read()
                time.sleep(0.33)
        #~ cv.imshow("original", self.img)
        
        # convert to gray and alter bits
        self.gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        #~ cv.bitwise_not(self.gray, self.gray)

        # shape of images
        print "shape: ", self.gray.shape
        self.rows, self.cols = self.gray.shape
        self.roi[2] = self.cols
        self.roi[3] = self.rows
        
        
        # Create trackbar and init default values
        self.switch_callback(self._threshold)
        CV.CreateTrackbar( "THRESHOLD", "original", self._threshold, 255, self.switch_callback )
        #~ cv.createTrackbar( "RadiusMin", "original", _minRad, 10, self.switch_callback )
        
        # Set mouse events on
        cv.setMouseCallback( "original", self.onMouse, 0)

        #~ For each frame
    def newFrame(self):
            
        # Read frame
        flag, self.img = self.cap.read()
        cv.imshow("original", self.img)
        
        #~ // invers color
        self.gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        #~ cv.bitwise_not(self.gray, self.gray)
        retVal, self.grayOut = cv.threshold(self.gray, self._threshold, 250, cv.THRESH_BINARY)

        self.checkROI()

        c = cv.waitKey(10)
        #~ print chr(c)
        if (c==ord('q')): sys.exit()
        if (c==ord('s')): self.setRef()
            
    def calibrationStart(self):
        self.setRef()
        return self.getInvTransformMatrix()
    
    def setTreshold(self, val):
        self._treshold = val
        
    def initConst(self):
        # define constants

        
        self._threshold = 170
        self.edge_thresh = 3

        self.dots = 4
        self.nCirc = self.dots
        self.xCMS, self.yCMS = 0, 0
        self.xP, self.yP = np.zeros(self.dots), np.zeros(self.dots)
        self.roi = np.zeros(4)

        
    def initCamVideo(self):
        """
        Initiates camera/video source.
        """
        
        if len(sys.argv) >= 2:
            self.filename = sys.argv[1]
        else: 
            self.filename = "dot_4.avi"
            
        # init cam/video
        #~ self.cap = cv.VideoCapture(self.filename)
        self.cap = cv.VideoCapture(1)
        
        if(not self.cap.isOpened()):
            return -1


    def checkROI(self):
        print "__checkROI__"
        print "self.xP: ", self.xP
        print "self.yP: ", self.yP

        self.refreshROI()
        self.calcMom()
        self.drawPoints()
        #~ cv.imshow("threshold", self.grayOut)
        cv.imshow("edge", self.edge)        
        cv.imshow("original", self.img)
        
    def refreshROI(self):
        if not (np.any(self.xP) and np.any(self.yP)): return
        
        xP = np.array(self.xP)
        yP = np.array(self.yP)
        
        # sprawdzic jakie to sa xP i yP wartosci
        xMin, xMax = xP.min(), xP.max()
        yMin, yMax = yP.min(), yP.max()
        
        err = 10
        dis = 50
         
        # Tworzenie troche wiekszego ROI od znalezionego czworokata
        if xMin < dis: xMin = 0
        else:         xMin -= dis
        if yMin < dis: yMin = 0
        else:         yMin -= dis
        if xMax > self.cols-dis: xMax = self.cols-1
        else: xMax += dis
        if yMax > self.rows-dis: yMax = self.rows-1
        else: yMax += dis
        
        self.roi = [xMin, yMin, xMax, yMax]

        print "xMin, xMax = {0}, {1}".format(xMin, xMax)
        print "yMin, yMax = {0}, {1}".format(yMin, yMax)
        
        
    def drawPoints(self):
        """
        This function is responsible for drawings.
        """
        
        xMean = self.xP.mean()
        yMean = self.yP.mean()

        self.edge = self.grayOut.copy()
        
        #~ //~ Draw dots
        CMS = int(self.xCMS), int(self.yCMS)
        radius = 11
        cv.circle( self.edge, CMS, radius, (20,20,20), 3, 8 )
        

        # Draws dots as corners of screen
        for i in range(self.dots):
            x = int(self.xP[i])
            y = int(self.yP[i])
            cv.circle( self.edge, (x,y), 5, (255,255,255), 3, 8, 0 )

        # Draws dots in corner of refrence screen
        print "self.corners: "
        print self.corners
        for i in range(self.dots):
            x = int(self.corners[0,i])
            y = int(self.corners[1,i])
            cv.circle( self.img, (x,y), 5, (0,0,255), 3, 8, 0 )
            
        # Draws dot in center of corners
        cv.circle( self.edge, (int(xMean), int(yMean)), 10, (200,100,100), 3, 8,0)
        cv.circle( self.img, (int(xMean), int(yMean)), 10, (200,100,100), 3, 8,0)

        # Draws dot in center of refrence screen
        print "self.centerDot.T[:1]: ", np.array(self.centerDot[:2].T)
        cv.circle( self.img, (int(self.centerDot[0]),int(self.centerDot[1])), 10, (255,255,255), 3, 8,0)        
        
        # Draws lines between corner dots
        for i in range(self.dots):
            exec("P%i = int(self.xP[%i]), int(self.yP[%i])" %(i,i,i))

            for j in range(i):
                exec("cv.line(self.edge, P%i, P%i, ( 255,255,255))" %(i,j))

        # Connect center dots
        p_ref = int(self.centerDot[0]), int(self.centerDot[1])
        p_new =  int(xMean), int(yMean)
        cv.line(self.img, p_ref, p_new, (0,0,255))
        
        # Draw test dot, which coordinates are calulcated from
        # inversed transformation matrix
        # X' = S X -> X = S^-1 X'
        Xp = np.matrix( [int(xMean), int(yMean),1]).T
        p_test = self.getInvTransformMatrix()*Xp
        cv.circle( self.img, (int(p_test[0]),int(p_test[1])), 10, (255,255,255), 3, 8,0)
     
    def switch_callback(self, threshold ):

        self._threshold = threshold
        retVal, self.grayOut = cv.threshold(self.gray, threshold, 250, cv.THRESH_BINARY)
        
        #~ //smooth the image to reduce unneccesary results
        self.grayOut = cv.GaussianBlur( self.grayOut, (9, 9), 2)
        self.grayOut = cv.medianBlur( self.grayOut, 5)

        #~ //get edges
        #~ //~ Canny(grayOut, edge, (float)edge_thresh, (float)edge_thresh*3, 5)

        #~ self.roi = [0, 0, self.rows-1, self.cols-1]
        #~ self.roi = [0, 0, self.cols, self.rows]
        self.calcMom()
            
        self.drawPoints()
        
        #~ cv.imshow("threshold", self.grayOut)
        cv.imshow("edge", self.edge)

    def calcMom(self):
        print "\n"
        print " ++ self.calcMom(self) ++"
        print "self.roi: ", self.roi
        
        ROI = self.roi
        M = self.grayOut[ROI[1]:ROI[3],ROI[0]:ROI[2]]

        #~ //~ Obliczanie momentow - srodka masy
        
        Mom = cv.moments(M, True)
        if(Mom["m00"]):
            xCMS = Mom['m10']/Mom["m00"]
            yCMS = Mom["m01"]/Mom["m00"]
        else:
            return

        self.xCMS = int(xCMS)
        self.yCMS = int(yCMS)
        
        if np.any(self.xP):
			xCenter = self.xP.mean()
			yCenter = self.yP.mean()
			xCMS, yCMS = xCenter, yCenter
			self.xCMS, self.yCMS = xCenter, yCenter
        
        xInit = [ROI[0], xCMS, ROI[0], xCMS]
        yInit = [ROI[1], ROI[1], yCMS, yCMS]
        xFin  = [xCMS,   ROI[2], xCMS, ROI[2]]
        yFin  = [yCMS, yCMS, ROI[3], ROI[3]]
        roi = [0]*4
        
        #~ //~ Counting mean val
        for i in range(self.dots):
            roi[0] = np.floor(xInit[i]) # x0
            roi[1] = np.floor(yInit[i]) # y0
            roi[2] = np.floor(xFin[i]) # x1
            roi[3] = np.floor(yFin[i]) # y1
            print "roi " + str(i) + ": " + str(roi)
            
            if not (roi[0]<roi[2] and roi[1]<roi[3]):
                return

            image_roi = self.grayOut[roi[1]:roi[3],roi[0]:roi[2]]

            Mom = cv.moments(image_roi, True)
            if(Mom["m00"]):
                self.xP[i] = roi[0] + Mom["m10"]/Mom["m00"]
                self.yP[i] = roi[1] + Mom["m01"]/Mom["m00"]
            else:
                self.xP[i] = roi[i] + 0
                self.yP[i] = roi[i] + 0
        
        # Calculate Transform matrix:
        P1p = np.matrix( (self.xP[0], self.yP[0], 1)).T
        P2p = np.matrix( (self.xP[1], self.yP[1], 1)).T
        P3p = np.matrix( (self.xP[2], self.yP[2], 1)).T
        
        Pp = np.concatenate( (P1p, P2p, P3p), axis=1)
        self.S = self.getTransformMatrix(Pp)
        print "S: "
        print self.S

    def setRef(self):
        """
        Sets values for new refrence coordinates.
        """
        print " ++ self.setRef(self) ++"
        
        P1 = np.matrix([self.xP[0], self.yP[0],1]).T
        P2 = np.matrix([self.xP[1], self.yP[1],1]).T
        P3 = np.matrix([self.xP[2], self.yP[2],1]).T
        P4 = np.matrix([self.xP[3], self.yP[3],1]).T
        
        self.P = np.concatenate((P1,P2,P3),axis=1)
        try:
            self.invP = np.linalg.inv(self.P)
        except:
            self.invP = np.eye(self.P.shape[0],self.P.shape[1])
            
        print "self.P: "
        print self.P
        
        self.corners = np.concatenate((self.P,P4),axis=1)
        self.centerDot = np.mean( self.corners, axis=1)
        
        

    def getTransformMatrix(self, P):
        return P*self.invP
    
    def getInvTransformMatrix(self):
        return np.linalg.inv(self.S)
        
    def onMouse(self, event, x, y, flags, param ):
        if( event != cv.EVENT_LBUTTONDOWN ):
            return


        self.nCirc = (self.nCirc+1)%self.dots
        self.xP[self.nCirc] = x
        self.yP[self.nCirc] = y
            
        print "nCirc = ", self.nCirc
        print "(x,y) = ({0}, {1})".format(self.xP[self.nCirc], self.yP[self.nCirc])

        self.drawPoints()
        self.refreshROI()
        #~ self.checkROI()
        
        #~ cv.imshow("threshold", self.grayOut);
        cv.imshow("edge", self.edge);



if __name__ == "__main__":
    Camera()
