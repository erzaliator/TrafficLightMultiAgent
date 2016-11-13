import spade
import random

GRID_SIZE = 2

grid = []
traffic = {}

def getName(row, col) :
	return "junction_" + str(row) + "_" + str(col) + "@127.0.0.1"

def getPwd(row, col) :
	return "secret_" + str(row) + "_" + str(col)


def initializeTraffic(size) :
	traffic = {}

	traffic['row'] = []
	traffic['col'] = []

	for i in (range(size-1)) :
		traffic['row'].append(random.randint(10, 40))
		traffic['col'].append(random.randint(10, 40))

	return traffic


def getPriority(name) :
	name = name.split('@')[0]
	i, j = int(name.split('_')[1]), int(name.split('_')[2])

	priority = 0

	if i != 0 and i != (GRID_SIZE - 1) :
		priority += (traffic['row'][i-1] + traffic['row'][i])

	elif i != 0 :
		priority += traffic['row'][i-1]

	elif i != (GRID_SIZE - 1) :
		priority += traffic['row'][i]


	if j != 0 and j != (GRID_SIZE - 1) :
		priority += (traffic['col'][j-1] + traffic['col'][j])

	elif j != 0 :
		priority += traffic['col'][j-1]

	elif j != (GRID_SIZE - 1) :
		priority += traffic['col'][j]


	return priority


def getNeighbours(name) :
	name = name.split('@')[0]
	i, j = int(name.split('_')[1]), int(name.split('_')[2])

	neighbours = []

	if i != 0 :
		neighbours.append((i-1, j))

	if j != 0 :
		neighbours.append((i, j-1))

	if i != (GRID_SIZE-1) :
		neighbours.append((i+1, j))

	if j != (GRID_SIZE-1) :
		neighbours.append((i, j+1))

	return neighbours


class JunctionController(spade.Agent.Agent) :

	class InitReceive(spade.Behaviour.Behaviour) :
		def _process(self) :
			self.msg = None

			self.msg = self._receive(True)

			if(self.msg) :
				d = {}
				agentInfo = self.msg.split('|')
				name, priority, value = agentInfo[0], agentInfo[1], agentInfo[2]
				d['name'] = name
				d['priority'] = priority
				d['value'] = value

				self.agent_view.append(d)
				self.good_list.append(d)

				print name + " in " + self.getName()


	class InitSend(spade.Behaviour.Behaviour) :
		def _process(self) :
			neighbours = getNeighbours(self.getName())

			for neighbour in neighbours :
				receiver = spade.AID.aid(name=getName(neighbour[0], neighbour[1]) + "@127.0.0.1", 
					addresses=["xmpp://" + getName(neighbour[0], neighbour[1]) +"@127.0.0.1"])

				self.msg = spade.ACLMessage.ACLMessage()
				self.msg.setPerformative("inform")
				self.msg.setOntology("init")
				self.msg.setLanguage("OWL-S")
				self.msg.addReceiver(receiver)
				self.msg.setContent(self.getName() + '|' + self.priority + '|' + self.value)

				print "here"

				self.JunctionController.send(self.msg)

				print "send from " + self.getName() + " to " + str(neighbour) + " : " + self.msg


	def _setup(self) :
		print "Starting agent : ", self.getName()

		self.priority = getPriority(self.getName())

		val = random.randint(0, 1)

		if val < 0.5 :
			self.value = 'NS'
		else:
			self.value = 'EW'

		self.agent_view = []
		self.good_list = []


		sender = self.InitSend()
		self.addBehaviour(sender, None)

		init_template = spade.Behaviour.ACLTemplate()
		init_template.setOntology("init")
		mt = spade.Behaviour.MessageTemplate(init_template)
		
		init = self.InitReceive()
		self.addBehaviour(init, mt)


if __name__ == "__main__" :
	traffic = initializeTraffic(GRID_SIZE)

	grid = [[JunctionController(getName(i, j), getPwd(i, j)) for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]

	for row in grid:
		for junction in row:
			junction.start()