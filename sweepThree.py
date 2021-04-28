import mido
import time

ports = mido.get_output_names()
print("Available output ports: " + ', '.join(ports))

print("Using ", ports[0],  '. ', sep='', end='')
with mido.open_output(ports[0]) as outport:
	print("Open.")

	control = [0, 0, 0]
	duration = [20, 30, 60]
	finish_time = [ time.time() + duration[0],
		time.time() + duration[1],
		time.time() + duration[2] ]


	for i in range(3):
		msg = mido.Message('control_change', 
			channel = 0, control = i, value = control[i], time=0)
		print("Sending:", str(msg))
		outport.send(msg)


	print("Starting loop.")
	while not all(val == 127 for val in control):
		for i in range(3):

			prog = 1 - ((finish_time[i] - time.time()) / duration[i])
			code = round(prog * 127)
			if code > 127: code = 127
			#print( code, prog )
			if code > control[i]:
				control[i] = code
				msg = mido.Message('control_change', 
					channel = 0, control = i, value = control[i], time=0)
				print("Sending:", str(msg))
				outport.send(msg)


	for i in range(3):
		msg = mido.Message('control_change', 
			channel = 0, control = i, value = 0, time=0)
		print("Sending:", str(msg))
		outport.send(msg)







