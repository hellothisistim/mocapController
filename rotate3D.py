import numpy as np
import math


def angle_between(p1, p2):
	"""Angle between two points and origin in degrees.

	Source: https://stackoverflow.com/a/31735642"""

	ang1 = np.arctan2(*p1[::-1])
	ang2 = np.arctan2(*p2[::-1])
	return np.rad2deg((ang1 - ang2) % (2 * np.pi))

def translateToOrigin(points):
	"""Shift the first point in a given list of points to the origin. Apply 
	the same shift to the rest of the points in the list. Return a list of 
	the new positions in the same order."""

	shiftVector = 0 - points[0]

	out = []
	for point in points:
		out.append(point + shiftVector)
	return out

def rotateToXAxis(points):
	"""Given a list of 3D points where the first sits on the origin (0,0,0), the points will all be rotated around the Z and Y axes so that the the second point will sit on the X axis. Return a list of 
	the new positions in the same order."""
	
	assert points[0].sum() == 0

	# Source for rotation math: 
	# https://www.geeksforgeeks.org/computer-graphics-3d-rotation-transformations/

	#First, rotate around Z axis. 
	zAngle = 0 - angle_between(points[1][:2], np.array([1,0]))
	zAngleRad = math.radians(zAngle)
	#print('z axis roatation degrees', zAngle, 'radians', zAngleRad)

	zRotPoints = []
	for point in points:
		#x = xo * cos - yo * sin
		x = point[0] * math.cos(zAngleRad) - point[1] * math.sin(zAngleRad)
		#y = xo * sin + yo * cos
		y = point[0] * math.sin(zAngleRad) + point[1] * math.cos(zAngleRad)
		#print(point, x, y)
		zRotPoints.append(np.array([x, y, point[2]]))

	#Then, rotate around Y axis.
	yAngle = angle_between(np.array([zRotPoints[1][0], zRotPoints[1][2]]), 
		np.array([1,0]))
	yAngleRad = math.radians(yAngle)
	#print('y axis roatation degrees', yAngle, 'radians', yAngleRad)

	outPoints = []
	for point in zRotPoints:
		#x = xo * cos + zo * sin
		x = point[0] * math.cos(yAngleRad) + point[2] * math.sin(yAngleRad)
		#z = zo * cos - xo * sin
		z = point[2] * math.cos(yAngleRad) - point[0] * math.sin(yAngleRad)
		#print(point, x, z)
		outPoints.append(np.array([x, point[1], z]))

	return outPoints

def normalize(points):
	"""Given a list of points where the first sits on the origin (0,0,0), 
	and the second sits on the X axis, scale all points from the origin so 
	that the second point has a magnitude of 1. Return a list of the new 
	positions in the same order."""

	assert points[0].sum() == 0
	assert points[1][0] > 0
	assert points[1][1] < 0.01
	assert points[1][2] < 0.01

	mag = np.linalg.norm(points[1])
	scale = 1 / mag

	outPoints = []
	for point in points:
		point *= scale
		outPoints.append(point)

	return points

def prepPoints(points):
	"""Given a list of points where the first point is to be the origin and the second point is to sit on the positive X axis, reposition, rotate, and scale the point cloud so the origin point sits at (0,0,0), the xPos point sits on the x axis at (1,0,0), and the rest of the points are transformed in the same manner.

	Return a list of transformed points."""

	points = translateToOrigin(points)
	points = rotateToXAxis(points)
	points = normalize(points)

	return points


if __name__ == "__main__":

	markerApos = np.array([-461, 123, 231])
	markerBpos = markerApos + np.array([100, 100, 100])
	markerCpos = np.array([400,400,400])
	points = [markerApos, markerBpos, markerCpos]


	print('start', points)

	points = prepPoints(points)

	print('prepped', points)
