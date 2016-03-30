class EyetrackerBrowser(object):
    def __init__(self, _mainloop, callback, *args, **kwargs):
        callback(11, "Found", object(), *args, **kwargs)
    
    def stop(self):
        pass