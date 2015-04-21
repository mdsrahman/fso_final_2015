
f = open("./collected/spec/17.txt","r")

gfound = False
sinks = []
for line in f:
  if gfound:
    sinks.append(int(line[0:-1]))
  if line[0:-1]=='gateways:':
    gfound = True
print sinks