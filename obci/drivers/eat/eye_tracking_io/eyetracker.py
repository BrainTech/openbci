from tobii.eye_tracking_io.utils.events import Events

class EyetrackerEvents(Events):
    __events__ = ("OnCalibrationStarted", "OnCalibrationStopped", "OnFramerateChanged", "OnTrackBoxChanged", "OnXConfigurationChanged", "OnGazeDataReceived", "OnError")

class Eyetracker(object):
    def __init__(self):
        self.events = EyetrackerEvents()
    
    @classmethod
    def create_async(cls, _mainloop, _info, _callback, *args, **kwargs):
        obj = cls()
        _callback(object(), obj, *args, **kwargs)
        return obj
    
    def StartCalibration(self, callback):
        if callback:
            callback()
    
    def StopCalibration(self, callback):
        if callback:
            callback()
    
    def AddCalibrationPoint(self, _point):
        pass
    
    def ComputeCalibration(self, callback):
        callback(0, object())
        
    def StartTracking(self, callback=None):
        if callback:
            callback()
    
    def StopTracking(self):
        pass
    
    def GetCalibration(self, callback=None):
        if callback:
            callback(object())
        else:
            return object()