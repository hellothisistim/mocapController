import mido

ports = mido.get_input_names()
print("Available intput ports: " + ', '.join(ports))

print("Using ", ports[0],  '. ', sep='', end='')
with mido.open_input(ports[0]) as inport:
	print("Open.")

	print("Starting loop.")
	while True:
		for msg in inport:
			print(msg)






