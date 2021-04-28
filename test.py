import mido
import random, time

ports = mido.get_output_names()
print("Available output ports: " + ', '.join(ports))

print("Using ", ports[0],  '. ', sep='', end='')
with mido.open_output(ports[0]) as outport:
	print("Open.")

	print("Starting loop.")
	while True:
		time.sleep(0.5)
		v = random.randint(0,127)
		msg = mido.Message('control_change', 
			channel = 0, 
			control = 0, 
			value = v, 
			time=0)
		print("Sending:", str(msg) )

		outport.send(msg)
		time.sleep(0.5)

		v = random.randint(0,127)
		msg = mido.Message('control_change', 
			channel = 0, 
			control = 1, 
			value = v, 
			time=0)
		print("Sending:", str(msg) )
		
		outport.send(msg)






