import numpy as np
import cv as CV
import cv2 as cv
import sys, time



class Camera:
    
    def debugPrint(self, text):
        if self.debug:
            print text
        
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

        while(1):
            # Read frame
            flag, self.img = self.cap.read()
            cv.imshow("original", self.img)

            #~ // invers color
            self.gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
            #~ cv.bitwise_not(self.gray, self.gray)
            retVal, self.grayOut = cv.threshold(self.gray, self._threshold, 250, cv.THRESH_BINARY)

            self.checkROI()

            c = cv.waitKey(33)
            #~ print chr(c)
            if (c==ord('q')): break
            if (c==ord('s')): self.setRef()



    def initConst(self):
        # define constants

        # black/white threshold
        self._threshold = 100
        self.edge_thresh = 3

        # ile pikseli wziac wiecej do analizy
        self.dis = 50

        # no of dots
        self.dots = 4
        self.nCirc = self.dots

        # tmp values for coordinates
        self.xCMS, self.yCMS = 0, 0
        self.xP, self.yP = np.zeros(self.dots), np.zeros(self.dots)
        self.roi = np.zeros(4)
        
        self.S = np.eye(3)

        # debug option
        self.debug = False

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
        self.cap = cv.VideoCapture(-1)

        if(not self.cap.isOpened()):
            return -1

    def setRef(self):
        """
        Sets values for new refrence coordinates.
        """
        print " ++ self.setRef(self) ++"

        # P = [x, y, 1].T
        P1 = np.matrix([self.xP[0], self.yP[0], 1]).T
        P2 = np.matrix([self.xP[1], self.yP[1], 1]).T
        P3 = np.matrix([self.xP[2], self.yP[2], 1]).T
        P4 = np.matrix([self.xP[3], self.yP[3], 1]).T

        self.P = np.concatenate((P1,P2,P3),axis=1)
        try:
            self.invP = np.linalg.inv(self.P)
        except:
            self.invP = np.eye(self.P.shape[0],self.P.shape[1])

        self.debugPrint("self.P: ")
        self.debugPrint(self.P)

        # corners of displaied IR LEDs
        self.corners = np.concatenate((self.P,P4),axis=1)
        
        # central dot of a screen
        self.centerDot = np.mean( self.corners, axis=1)


    def checkROI(self):
        self.debugPrint("__checkROI__")
        self.debugPrint("self.xP: " + str(self.xP))
        self.debugPrint("self.yP: " + str(self.yP))

        self.improveVideo()
        self.refreshROI()
        corners = self.calcMom()
        self.setTransformationMatrix(corners)
        self.drawPoints()
        
        #~ cv.imshow("threshold", self.grayOut)
        cv.imshow("edge", self.edge)
        cv.imshow("original", self.img)

    def refreshROI(self):
        """
        Refreshes ROI sizes.
        """
        if not (np.any(self.xP) and np.any(self.yP)): return

        xP = np.array(self.xP)
        yP = np.array(self.yP)

        # sprawdzic jakie to sa xP i yP wartosci
        xMin, xMax = xP.min(), xP.max()
        yMin, yMax = yP.min(), yP.max()


        # Tworzenie troche wiekszego ROI od znalezionego czworokata
        if xMin < self.dis: xMin = 0
        else:         xMin -= self.dis
        if yMin < self.dis: yMin = 0
        else:         yMin -= self.dis
        if xMax > self.cols-self.dis: xMax = self.cols-1
        else: xMax += self.dis
        if yMax > self.rows-self.dis: yMax = self.rows-1
        else: yMax += self.dis

        self.roi = [xMin, yMin, xMax, yMax]

        self.debugPrint("xMin, xMax = {0}, {1}".format(xMin, xMax))
        self.debugPrint("yMin, yMax = {0}, {1}".format(yMin, yMax))

    def calcMom(self):
        self.debugPrint("\n")
        self.debugPrint(" ++ self.calcMom(self) ++")
        self.debugPrint("self.roi: " + str(self.roi))

        ROI = self.roi
        M = self.grayOut[ROI[1]:ROI[3],ROI[0]:ROI[2]]


        if np.any(self.xP):
            xCenter = self.xP.mean()
            yCenter = self.yP.mean()
            xCMS, yCMS = xCenter, yCenter
            self.xCMS, self.yCMS = xCenter, yCenter
        else:
            # Finds mass center of region
            Mom = cv.moments(M, True)
            if(Mom["m00"]):
                xCMS, yCMS = [ int(m/Mom["m00"]) for m in [Mom['m10'], Mom['m01']] ]
            else:
                return


        self.debugPrint("xCMS, yCMS = {0}, {1}".format( xCMS, yCMS))
        
        # Coordinates of left-up corner and bottom-right corner
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
            self.debugPrint("roi " + str(i) + ": " + str(roi))

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
        P4p = np.matrix( (self.xP[3], self.yP[3], 1)).T
        
        Pp = np.concatenate( (P1p, P2p, P3p, P4p), axis=1)
        return Pp
        
    def setTransformationMatrix(self, points):
        try:
            Pp = points[:,:3]
            self.S = self.getTransformMatrix(Pp)
            self.debugPrint("S: \n" + str(self.S) )
        except TypeError:
            self.debugPrint("Coudn't set transformation matrix.")
            self.S = np.eye(3)

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
        self.debugPrint("self.corners: \n" +str(self.corners))

        for i in range(self.dots):
            x = int(self.corners[0,i])
            y = int(self.corners[1,i])
            cv.circle( self.img, (x,y), 5, (0,0,255), 3, 8, 0 )

        # Draws dot in center of corners
        cv.circle( self.edge, (int(xMean), int(yMean)), 10, (200,100,100), 3, 8,0)
        cv.circle( self.img, (int(xMean), int(yMean)), 10, (200,100,100), 3, 8,0)

        # Draws dot in center of refrence screen
        self.debugPrint("self.centerDot.T[:1]: " + str(np.array(self.centerDot[:2].T))  )
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
        """
        What is done after change of threshold.
        """
        
        self._threshold = threshold
        retVal, self.grayOut = cv.threshold(self.gray, threshold, 250, cv.THRESH_BINARY)

        self.improveVideo()
        self.calcMom()
        self.drawPoints()

        #~ cv.imshow("threshold", self.grayOut)
        cv.imshow("edge", self.edge)

    def getTransformMatrix(self, P):
        return P*self.invP

    def getInvTransformMatrix(self):
        try:
            return np.linalg.inv(self.S)
        except np.linalg.LinAlgError('Singular matrix'):
            self.debugPrint("Singular matrix problem. Matrix can't be inversed!")
            return np.eye(self.S.shape[0])
        

    def onMouse(self, event, x, y, flags, param ):
        if( event != cv.EVENT_LBUTTONDOWN ):
            return


        self.nCirc = (self.nCirc+1)%self.dots
        self.xP[self.nCirc] = x
        self.yP[self.nCirc] = y

        self.debugPrint("nCirc = " + str(self.nCirc))
        self.debugPrint("(x,y) = ({0}, {1})".format(self.xP[self.nCirc], self.yP[self.nCirc]) )

        self.drawPoints()
        self.refreshROI()
        #~ self.checkROI()

        #~ cv.imshow("threshold", self.grayOut);
        cv.imshow("edge", self.edge);


    def calibrationStart(self):
        self.setRef()
        return self.getInvTransformMatrix()

    def setTreshold(self, val):
        self._treshold = val

    def improveVideo(self):
        """
        Does 2D filters on video.
        """
        self.grayOut = cv.GaussianBlur( self.grayOut, (9, 9), 2)
        self.grayOut = cv.medianBlur( self.grayOut, 5)

if __name__ == "__main__":
    Camera()
