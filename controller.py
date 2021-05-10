from __future__ import print_function
import argparse
import logging
import math
import mido
import numpy as np
import sys
import time

from rotate3D import *

ports = mido.get_output_names()

parser = argparse.ArgumentParser(description="Use markers in the Vicon DataStream as a realtime MIDI controller.")
parser.add_argument('host', nargs='?', help="Host name, in the format of server:port", default = "172.32.3.195:801")
parser.add_argument('-o', '--origin', help="Marker name to use as the origin of the point cloud.", default="rbA", required=False)
parser.add_argument('-x', '--xPos', help="Marker name to place at +1 on the X axis when normalizing the point cloud.", default="rbB", required=False)
parser.add_argument('-n', '--noVicon', help="Run without connecting to Vicon DataStream. Will generate smulated data for setting up without requiring the Vicon software to be present.", action="store_true", required=False)
parser.add_argument('-l', '--listPorts', help="List available MIDI ports.", action='store_true', required=False)
parser.add_argument('-p', '--port', help="Specify MIDI port to use.", default=ports[0], required=False)
args = parser.parse_args()

if args.listPorts:
	ports = mido.get_output_names()
	sys.exit("Available output ports: " + ', '.join(ports))

if not args.noVicon:
	from vicon_dssdk import ViconDataStream

	logging.info("Found ViconDataStream. Setting up.")

	client = ViconDataStream.Client()
	client.Connect( args.host )

	# Check the version
	logging.debug( 'Version', client.GetVersion() )

	# Check setting the buffer size works
	client.SetBufferSize( 1 )

	#Enable all the data types
	client.EnableSegmentData()
	client.DisableMarkerData()
	client.DisableUnlabeledMarkerData()
	client.DisableMarkerRayData()
	client.DisableDeviceData()
	client.DisableCentroidData()

	# Report whether the data types have been enabled
	logging.debug( 'Segments', client.IsSegmentDataEnabled() )
	logging.debug( 'Markers', client.IsMarkerDataEnabled() )
	logging.debug( 'Unlabeled Markers', client.IsUnlabeledMarkerDataEnabled() )
	logging.debug( 'Marker Rays', client.IsMarkerRayDataEnabled() )
	logging.debug( 'Devices', client.IsDeviceDataEnabled() )
	logging.debug( 'Centroids', client.IsCentroidDataEnabled() )

	client.SetStreamMode( ViconDataStream.Client.StreamMode.EServerPush )

	try:
		client.ConfigureWireless()
	except ViconDataStream.DataStreamException as e:
		logging.info( 'Failed to configure wireless', e )


	logging.info("Finished setting up.")



def getMarkerLocations():
	"""Connect to the Vicon system and get the locations of all the 
	subjects (a.k.a. markers) that the system knows about.

	Return the frame number and a dictionary of marker names (as String) 
	and locations (as Numpy arrays.)
	"""

	try:

		HasFrame = False
		while not HasFrame:
			try:
				client.GetFrame()
				HasFrame = True
			except ViconDataStream.DataStreamException as e:
				client.GetFrame()

		frame = client.GetFrameNumber()

		locators = {}
		
		subjectNames = client.GetSubjectNames()
		print("subject names:", subjectNames)
		
		for subjectName in subjectNames:
			print("subject name:", subjectName )
			
			rootSegmentName = client.GetSubjectRootSegmentName(subjectName)
			print("root segment name:", rootSegmentName)
			globalTranslation = client.GetSegmentGlobalTranslation(subjectName, rootSegmentName)
			print("global translation:", globalTranslation)
			globalTranslation = globalTranslation[0]
			xpos, ypos, zpos = globalTranslation
			#xpos = round(xpos)
			#ypos = round(ypos)
			#zpos = round(zpos)
				
			locators[subjectName] = np.array([xpos, ypos, zpos])
			print('frame', client.GetFrameNumber(), subjectName, rootSegmentName, xpos, ypos, zpos)


		#print( 'frame', client.GetFrameNumber(), locators)
		return frame, locators

	except ViconDataStream.DataStreamException as e:
		print( 'Handled data stream error', e )


def simulateMarkerLocations():

	markers = {args.origin: np.array([0, 0, 0]),
			   args.xPos: np.array([2.2, 0, 0])}

	# The first other marker switches on and off.
	if (time.time() % 10) > 1:
		markers['rbC'] = np.array([math.sin(time.time()), math.cos(time.time()), 0])

	markers['rbD'] = np.array([(math.sin(time.time() / 10) + 1) / 2, 
							   (math.cos(time.time() / 10) + 1) / 2, 
							   time.time() - math.floor(time.time())])
	markers['rbE'] = np.array([(math.sin(time.time() / 100) + 1) / 2, 
							   (math.cos(time.time() / 100) + 1) / 2, 
							   (time.time() / 1000) - math.floor((time.time() / 1000))])
	frame = math.floor(time.time()) % 10000

	return frame, markers


if __name__ == "__main__":


	print(args)

	lastFrame = 0

	"""
	Marker-to-MIDI-channel mapping:
	other1	on/off: 0
			x:		1
			y:		2
			z:		3
	other2	on/off: 4
			x:		5
			y:		6
			z:		7
	other3	on/off: 8
			x:		9
			y:		10
			z:		11

	"""

	subjectMarkers = ['rbC', 'rbD', 'rbE']

	print("Using ", args.port,  '. ', sep='', end='')
	with mido.open_output(args.port) as outport:
		print("Open.")

		while True:

			if args.noVicon:
				frame, markers = simulateMarkerLocations()
			else:
				frame, markers = getMarkerLocations()
			
			if frame != lastFrame:
				lastFrame = frame

				markers = normalize(markers, args.origin, args.xPos)

				print('Frame:', frame, 'Markers:', markers)

				controller = 0
				for name in subjectMarkers:
					# First controller: marker on/off (gets sent at the end)
					value = 0
					if name in markers.keys():
						value = 127
						# Second controller: X  
						msg2 = mido.Message('control_change', channel = 0, 
								control = controller + 1, 
								value = int( max(min(markers[name][0] * 127, 127), 0) ), 
								time=0)
						outport.send(msg2)
						# Third controller: Y 
						msg3 = mido.Message('control_change', channel = 0, 
								control = controller + 2, 
								value = int( max(min(markers[name][1] * 127, 127), 0) ), 
								time=0)
						outport.send(msg3)
						# Fourth controller: Z 
						msg4 = mido.Message('control_change', channel = 0, 
								control = controller + 3, 
								value = int( max(min(markers[name][2] * 127, 127), 0) ), 
								time=0)
						outport.send(msg4)
					msg1 = mido.Message('control_change', channel = 0, control = controller, value = value, time=0)
					outport.send(msg1)
					controller += 4 # 4 controllers per marker (exists, x, y, z)



		# logging.info("frame:", frame, "markers:", markers)

		# markers = normalize(markers, originName, xPosName)

		# logging.info("frame:", frame, "markers:", markers)



