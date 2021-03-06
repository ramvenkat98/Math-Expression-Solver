import matplotlib.pyplot as plt
import numpy as np
from skimage import color, io
from scipy import ndimage
from skimage.filters import threshold_otsu
from skimage import feature
import skimage
from skimage.filters import threshold_local
from skimage.morphology import *
from skimage import transform
from functools import *
from skimage import measure

##Steps:
#1. Process the image
#2. Get the contours
#3. Get bounding boxes for the contours (filter out wrong contours by size)
#4. Resize the contents of each bounding box to a 28*28 square 

def processImg(img):
    #img = ndimage.median_filter(img, (7,7))
    #img = erosion(img, selem = np.ones((10, 5)))
    #maskSize = 1
    #img = ndimage.convolve(img, np.ones((maskSize, maskSize)), 
    #                           mode = 'constant')
    #img /= (maskSize * maskSize)
    #try and later see if mask needed
    #img = ndimage.median_filter(img, (7,7))
    #print(np.median(img.flatten()) * 0.8)
    img = img > 0.5
    #img = closing(img)#, selem = np.ones((10, 10)))
    img = 1 - img
    #img = skeletonize(img)
    #img = dilation(img, selem = np.ones((10, 5)))
    #plt.imshow(img)
    #plt.show()
    #img = skeletonize(img)
    img = dilation(img, selem = np.ones((10, 3)))
    #plt.imshow(img)
    #plt.show()
    return img * 255

def showContours(img, show = True):
    plt.clf()
    img = processImg(img)
    contours = measure.find_contours(img, 200)
    kMin = lambda x, y: [min(x[0], y[0]), min(x[1], y[1])]
    kMax = lambda x, y: [max(x[0], y[0]), max(x[1], y[1])]
    diff = lambda x, y: [abs(x[0]-y[0]), abs(x[1]-y[1])]
    width, height = img.shape
    def acceptable(x):
        [x0, y0], [x1, y1] = reduce(kMin, x), reduce(kMax, x)
        #if x0 - 5 < 0 or y0 - 5 < 0 or x1+5 >= width or y1 + 5 >= height:
        #    return False
        diffHeight = diff([x0, y0], [x1, y1])
        return ((diffHeight[0] > 30 or diffHeight[1] > 30)
        and not (diffHeight[0] > width * 4/5 and diffHeight[1] > height * 4/5))
        return diffHeight[0] < 1000 and diffHeight[1] < 1000
        return ((diffHeight[0] > 100 and diffHeight[1] > 100 
                and 1/2 < (diffHeight[0]/diffHeight[1]) < 2
                and diffHeight[0] < 1000 and diffHeight[1] < 1000))
    dims = [diff(reduce(kMin, x), reduce(kMax, x)) for x in contours]
    #print(dims)
    #correctContours = contours
    correctContours = list(filter(acceptable, contours))
    
    if not show: return kMin, kMax, correctContours, img, img
    plt.figure(1)
    for n, contour in enumerate(correctContours):
        plt.plot(contour[:, 1], contour[:, 0], linewidth=2)
    plt.show()
    return kMin, kMax, correctContours, edgeImg, dilatedImg

def getBoxes(img):
    kMin, kMax, correctContours, edgeImg, dilatedImg = showContours(img, False)
    boxes = [reduce(kMin, contour)+reduce(kMax, contour) 
            for contour in correctContours]

    def overlapsInside(box, boxes, i):
        [ya, xa, yb, xb] = box
        for j in range(len(boxes)):
            if i == j: continue
            [y0, x0, y1, x1] = boxes[j]
            if ((x0 <= xa and xb <= x1) and (y0 <= ya and yb <= y1)):
                return True
        return False
    
    boundingBoxes = []
    i = 0
    while i < len(boxes):
        if not overlapsInside(boxes[i], boxes, i):
            boundingBoxes += [boxes[i]]
        i += 1
    
    realBoundingBoxes = []

    #TO-DO: re-factor this for-loop later
    for boundingBox in boundingBoxes:
        [y0, x0, y1, x1] = boundingBox
        inside = lambda l: (l[0] >= y0 and l[1] >= x0
                            and l[2] <= y1 and l[3] <= x1
                            and (not l == [y0, x0, y1, x1]))
        innerBoxes = list(filter(inside, boxes))

        innerBoundingBoxes = []
        i = 0
        while i < len(innerBoxes):
            if not overlapsInside(innerBoxes[i], innerBoxes, i):
                innerBoundingBoxes += [innerBoxes[i]]
            i += 1
        if len(innerBoundingBoxes) > 1:
            #print("len", len(innerBoundingBoxes))
            check = True
            for i1 in range(len(innerBoundingBoxes)):
                [yl1, xl1, yr1, xr1] = innerBoundingBoxes[i1]
                #check if center is vertically aligned
                if abs((yl1+yr1)/2 - (y0+y1)/2)/((y0+y1)/2) > 0.15:
                    check = False
                #check if contiguous in x direction
                for i2 in range(i1+1, len(innerBoundingBoxes)):
                    [yl2, xl2, yr2, xr2] = innerBoundingBoxes[i2]
                    if not (xr1 <= xl2 or xl1 >= xr2):
                        check = False
            if check:
                realBoundingBoxes += innerBoundingBoxes
            else:
                realBoundingBoxes += [boundingBox]
        else: realBoundingBoxes += [boundingBox]

    #print("Bounding boxes", realBoundingBoxes)
    return realBoundingBoxes

def resizeToSquare(croppedImg):
    rows, cols = croppedImg.shape
    extras = abs((rows-cols)//2)
    if rows < cols:
        extras = np.full((extras, cols), 255)
        sqrImg = np.vstack([extras, croppedImg, extras])
    elif cols < rows:
        extras = np.full((rows, extras), 255)
        sqrImg = np.hstack([extras, croppedImg, extras])
    else:
        sqrImg = croppedImg
    sizedImg = transform.resize(sqrImg, (28, 28))
    return sizedImg
