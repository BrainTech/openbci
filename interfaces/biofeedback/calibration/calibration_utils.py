import os

def isExtensionSupported(filename):
    """ Supported extensions viewable in SlideShow
    """
    if filename.endswith('PNG') or filename.endswith('png') or\
     filename.endswith('JPG') or filename.endswith('jpg'):
        return True

def imageFilePaths(paths):
    imagesWithPath = []

    for _path in paths:
        try:
            dirContent = os.listdir(_path)
        except OSError:
            raise OSError("Provided path '%s' doesn't exists." % _path)

        for each in dirContent:
            selFile = os.path.join(_path, each)
            if os.path.isfile(selFile) and isExtensionSupported(selFile):
                imagesWithPath.append(selFile)
    imagesWithPath.sort(reverse=True)
    return imagesWithPath