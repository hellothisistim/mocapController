import numpy as np
import math
import logging

def angle_between(p1, p2):
	"""Angle between two points and origin in degrees.

	Source: https://stackoverflow.com/a/31735642"""

	ang1 = np.arctan2(*p1[::-1])
	ang2 = np.arctan2(*p2[::-1])
	return np.rad2deg((ang1 - ang2) % (2 * np.pi))

def translateToOrigin(points, originName):
	"""Shift the origin point to the origin. Apply 
	the same shift to the rest of the points. """

	try:
		assert originName in points.keys()
	except AssertionError as e:
		raise AssertionError(originName + " is not in the point cloud.")

	shiftVector = 0 - points[originName]

	out = {}
	for name in points.keys():
		out[name] = points[name] + shiftVector
	return out

def rotateToXAxis(points, xPosName):
	"""Rotate the point cloud so that the xPos point sits on the X axis."""
	
	# Source for rotation math: 
	# https://www.geeksforgeeks.org/computer-graphics-3d-rotation-transformations/

	try:
		assert xPosName in points.keys()
	except AssertionError as e:
		logging.critical(xPosName + " is not in the point cloud.")

	#First, rotate around Z axis. 
	zAngle = 0 - angle_between(points[xPosName][:2], np.array([1,0]))
	zAngleRad = math.radians(zAngle)
	# logging.debug('__z axis roatation in degrees: ' + str(zAngle) + '  in radians: ' + str(zAngleRad))

	zRotPoints = {}
	for name in points.keys():
		#x = xo * cos - yo * sin
		x = points[name][0] * math.cos(zAngleRad) - points[name][1] * math.sin(zAngleRad)
		#y = xo * sin + yo * cos
		y = points[name][0] * math.sin(zAngleRad) + points[name][1] * math.cos(zAngleRad)
		zRotPoints[name] = np.array([x, y, points[name][2]])
	# logging.debug("finished Z rotation. " + str(zRotPoints))

	#Then, rotate around Y axis.
	yAngle = angle_between(np.array([zRotPoints[xPosName][0], zRotPoints[xPosName][2]]), 
		np.array([1,0]))
	yAngleRad = math.radians(yAngle)
	# logging.debug('__y axis roatation degrees: ' + str(yAngle) + ' radians: ' + str(yAngleRad))

	# TODO: I managed to mess up this part when changing to the dict representation of the point cloud. Fix it.

	outPoints = {}
	for name in zRotPoints.keys():
		xIn, yIn, zIn = zRotPoints[name]
		#x = xo * cos + zo * sin
		xOut = xIn * math.cos(yAngleRad) + zIn * math.sin(yAngleRad)
		yOut = yIn
		#z = zo * cos - xo * sin
		zOut = zIn * math.cos(yAngleRad) - xIn * math.sin(yAngleRad)
		outPoints[name] = np.array([xOut, yOut, zOut])
	# logging.debug("finished Y rotation. " + str(outPoints))

	return outPoints

def normalize(points, originName, xPosName):
	"""Translates, rotates, and scales a point cloud so that the given origin 
	point sits on the origin and the xPos point sits at +1 on the X axis.
	
	Takes three things: 1. a dict of points in 3D space, where the keys are the 
	points' names and the location in space is stored as a numpy array, 2. the 
	name of the point to place at the origin (0,0,0), and 3. the name of the point that will end up at +1 on the X axis (1,0,0). 

	Return a dict of the points in their new positions.
	"""

	for item in [originName, xPosName]:
		try:
			assert item in points.keys()
		except AssertionError as e:
			raise AssertionError(originName + " is not in the point cloud.")

	# First, translate the cloud so that the origin point sits on the origin (0,0,0).
	points = translateToOrigin(points, originName)
	# logging.debug("After translateToOrigin:" + str(points))

	# Then, rotate so that the xPos point sits on the X axis.
	points = rotateToXAxis(points, xPosName)
	# logging.debug("After rotateToXAxis:" + str(points))


	# Then, scale the cloud so that the xPos point sits at +1 on the X axis.
	assert points[originName].sum() == 0
	assert points[xPosName][0] > 0
	assert points[xPosName][1] < 0.01
	assert points[xPosName][2] < 0.01

	mag = np.linalg.norm(points[xPosName])
	scale = 1 / mag

	outPoints = {}
	for name in points.keys():
		outPoints[name] = points[name] * scale
	return points



if __name__ == "__main__":

	logging.basicConfig(level=logging.DEBUG)

	logging.debug("Checking normalize.")
	markers = {'rbA': np.array([ 1819.56044853, -1204.24919905, -30.55150338]), 
			   'rbB': np.array([1804.77464868, 1874.82370907, 10.63022218]), 
			   'rbC': np.array([314, 345, 567]),
			   'rbD': np.array([456, 678, 890]), 
			   'rbE': np.array([ -19.07449426, 685.0376895, 1066.10069388])
			   }
	originName = 'rbA'
	xPosName = 'rbB'
	normal = normalize(markers, originName, xPosName)
	assert normal[originName].sum() == 0
	assert normal[xPosName][0] > 0
	assert normal[xPosName][1] < 0.01
	assert normal[xPosName][2] < 0.01
	logging.debug("Pass: normalize")

