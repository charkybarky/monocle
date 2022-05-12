from PIL import Image

fileName = 'sample/IMG_8218.jpg'

myImage = Image.open(fileName)
myImageLoad = myImage.load()

# returns true if all the following are true:
#	x between values 0 inclusive, horizontal resolution exclusive
#	y between values 0 inclusive, vertical resolution exclusive
def imageBoundsCheck(image, x, y):
	size = image.size
	return (x >= 0 and y >= 0) and (x < size[0] and y < size[1])


def imageBoundsCheckRadius(image, x, y, radius):
	size = image.size
	return (x - radius >= 0 and y - radius >= 0) and (x < size[0] - radius and y < size[1] - radius)


def redBackgroundCheck(color):
	other = 30
	color = (0, other, other)
	
	maxNonRedVal = max(color[1], color[2])
	
	diffBright = 200
	diffThresh = int(diffBright * (maxNonRedVal / 255))
	
	color = (maxNonRedVal + diffThresh, color[1], color[2])
	
	print('maxVal %d' % maxNonRedVal)
	print('color %s' % str(color))
	print('diffB %s' % str(diffThresh))
	
	im = Image.new("RGB", (512, 512), "white")
	im.show()


class RegionChunk:
	
	# you give the exact number of Regions in both the vertical and horizontal direction
	# "posByCorner" = the start X/Y is actually the top left CORNER of a Region instead of the CENTER
	# startPos: tuple (x,y)
	# jump: tuple (x,y)
	# regionNum: tuple (x,y)
	def chunkDefineExact(self, startPos, jump, regionNum, regionRadius, posByCorner=False, jumpByRadius=False):
		self.regionList = []
		navX = startPos[0]
		navY = startPos[1]
		
		if(jumpByRadius):
			jump = (regionRadius, regionRadius)
		
		if(posByCorner):
			navX += regionRadius
			navY += regionRadius
		
		if not imageBoundsCheckRadius(self.imageObject, navX, navY, regionRadius):
			return False
		
		for vert in range(regionNum[1]):
			for horz in range(regionNum[0]):
				self.regionList.append(Region(self.imageObject, self.imageLoaded, (navX, navY), regionRadius))
				
				navX += jump[0]
			
			navY += jump[1]
			navX -= jump[0] * (regionNum[0])
		
		return True
		
	# you give a number of pixels; it will try to pack as many Regions as it can depending on their radius
	# considered to be more "lazy"
	# "useMax" will choose the maximium calculated radius, instaed of minimum
	def chunkDefinePack(self, topLeftCorner, bottomRightCorner, regionNum, useMax=False):
		self.regionList = []
		
		width = bottomRightCorner[0] - topLeftCorner[0]
		height = bottomRightCorner[1] - topLeftCorner[1]
		
		radiusCalc = (int(width / regionNum[0]), int(height / regionNum[1]))
		radius = 0
		
		if(useMax):
			radius = max(radiusCalc)
		else:
			radius = min(radiusCalc)
		
		# regions cannot have arbitrary widths or lengths, they MUST conform to a radius
		# therefore, the radius will be based on the SMALLER of the width or height
		
		return self.chunkDefineExact(topLeftCorner, (0, 0), regionNum, radius, True, True)


	def chunkFillColorAverage(self):
		for region in self.regionList:
			region.imageFillRegion(region.getRegionPixelAverage())
	
	
	def __init__(self, imageObject, imageLoaded):
		self.imageObject = imageObject
		self.imageLoaded = imageLoaded
		self.regionList = []



class Region:

	def imageFillRegion(self, color):
		centerX = self.pixLocation[0]
		centerY = self.pixLocation[1]
		
		for x in range(centerX - self.pixRadius, centerX + self.pixRadius + 1):
			for y in range(centerY - self.pixRadius, centerY + self.pixRadius + 1):
				self.imageLoaded[x, y] = color

	#def getColorDominance(color):
		

	def getRegionPixelList(self):
		centerX = self.pixLocation[0]
		centerY = self.pixLocation[1]
		
		pixelList = []
		
		if self.pixRadius == 0:
			pixelList.append(self.imageLoaded[centerX, centerY])
		else:
			for x in range(centerX - self.pixRadius, centerX + self.pixRadius + 1):
				for y in range(centerY - self.pixRadius, centerY + self.pixRadius + 1):
					#print('[[ %d , %d ]]' % (x, y))
					pixelList.append(self.imageLoaded[x, y])
		
		return pixelList
	

	def getRegionPixelAverage(self):
		redSum = 0
		greenSum = 0
		blueSum = 0
		pixelList = self.getRegionPixelList()
		pixelCount = len(pixelList)
		
		for color in pixelList:
			redSum += color[0]
			greenSum += color[1]
			blueSum += color[2]
		
		return (int(redSum / pixelCount), int(greenSum / pixelCount), int(blueSum / pixelCount))


	def __init__(self, imageObject, imageLoaded, pixLocation, pixRadius=1):
		self.imageObject = imageObject
		self.imageLoaded = imageLoaded
		self.pixLocation = pixLocation # the center of the region
		self.pixRadius = pixRadius



def regionTestA():	
	r1 = Region(myImage, myImageLoad, (2, 2), 2)

	print(r1.getRegionPixelList())

	print(r1.getRegionPixelList())
	print(r1.getRegionPixelAverage())

	r1.imageShowRegion()


def chunkTestA():
	rc1 = RegionChunk(myImage, myImageLoad)

	rc1.chunkDefineExact((0, 0), (0, 0), (40, 20), 25, True, True)

	rc1List = rc1.regionList

	print(len(rc1List))

	for reg in rc1List:
		#print('REGION: radius = %d, location = %s' % (reg.pixRadius, str(reg.pixLocation)))
		reg.imageFillRegion(reg.getRegionPixelAverage())

	myImage.show("cooleo")


def chunkTestB():
	rc2 = RegionChunk(myImage, myImageLoad)
	
	rc2.chunkDefinePack((0, 0), (2000, 400), (80, 15), True)
	
	rc2.chunkFillColorAverage()
	
	myImage.show()


def chunkTestC():
	color = myImageLoad[0, 0]

	redBackgroundCheck(color)


#chunkTestA()
#chunkTestB()
chunkTestC()
