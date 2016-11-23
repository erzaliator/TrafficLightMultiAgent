import spade
import random
from xml.etree.ElementTree import XML, fromstring, tostring

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


def getAgentLoc(name) :
	name = name.split('@')[0]
	i, j = int(name.split('_')[1]), int(name.split('_')[2])
	return i, j

def VehiclesFrom(agent, toAgentName, direction) :
	i, j = getAgentLoc(toAgentName)
	agent_i, agent_j = getAgentLoc(agent['name'])

	if direction == "NS" :
		if agent_i < i :
			return traffic['col'][agent_i]
		else :
			return traffic['col'][i]

	else :
		if agent_j < j :
			return traffic['row'][agent_j]
		else :
			return traffic['row'][j]


class JunctionController(spade.Agent.Agent) :

	class InitReceive(spade.Behaviour.OneShotBehaviour) :
		def _process(self) :
			self.msg = None

			self.msg = self._receive(True)

			if(self.msg) :
				d = {}

				#xml parsing
				root = fromstring(str(self.msg))
				content = root.find('content')
				agentInfo = content.text.split("|")
				name, priority, value, m = agentInfo[0], agentInfo[1], agentInfo[2], agentInfo[3]
				d['name'] = name
				d['priority'] = priority
				d['value'] = value
				d['m'] = m

				self.myAgent.agent_view.append(d)
				self.myAgent.good_list.append(d)

				# print "recieve from " + name + " to " + self.myAgent.getName() + "\n"


	class InitSend(spade.Behaviour.OneShotBehaviour) :
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
				self.msg.setContent(self.myAgent.getName() + '|' + str(self.myAgent.priority) + '|' + str(self.myAgent.value) \
				 + '|' + str(self.myAgent.m))

				self.myAgent.send(self.msg)
				# print "send from " + self.getName() + " to " + str(neighbour) + " : " + self.msg.getContent() + "\n"


	class CheckAgentView(spade.Behaviour.PeriodicBehaviour) :
		def onStart(self) :
			print self.myAgent.name + " checking Agent View...\n"

		def _onTick(self) :
			Fcost = self.myAgent.getFcost()

			if Fcost > self.myAgent.Fstar :
				if self.myAgent.value == "NS" :
					self.myAgent.value = "EW"
				else :
					self.myAgent.value = "NS"

			Fcost_new = self.myAgent.getFcost()

			if Fcost_new > self.myAgent.Fstar :
				self.myAgent.m = 1

			for agent in self.myAgent.agent_view :
				receiver = spade.AID.aid(name=agent['name'], addresses=["xmpp://" + agent['name']])

				self.msg = spade.ACLMessage.ACLMessage()
				self.msg.setPerformative("inform")
				self.msg.setOntology("value")
				self.msg.setLanguage("OWL-S")
				self.msg.addReceiver(receiver)
				self.msg.setContent(self.myAgent.getName() + '|' + str(self.myAgent.priority) + '|' + str(self.myAgent.value) \
				 + '|' + str(self.myAgent.m))

				self.myAgent.send(self.msg)
				print "send from " + self.getName() + " to " + str(agent['name']) + "\n"


	class ValueReceive(spade.Behaviour.PeriodicBehaviour) :
		def _process(self) :
			self.msg = None

			self.msg = self._receive(True)

			if(self.msg) :
				d = {}

				#xml parsing
				root = fromstring(str(self.msg))
				content = root.find('content')
				agentInfo = content.text.split("|")
				name, priority, value, m = agentInfo[0], agentInfo[1], agentInfo[2], agentInfo[3]
				d['name'] = name
				d['priority'] = priority
				d['value'] = value
				d['m'] = m

				added = 0

				for i in range(len(self.myAgent.agent_view)) :
					if d['name'] == self.myAgent.agent_view[i]['name'] :
						self.myAgent.agent_view[i]['priority'] = d['priority']
						self.myAgent.agent_view[i]['value'] = d['value']
						self.myAgent.agent_view[i]['m'] = d['m']

						added = 1

				if added == 0 :
					self.myAgent.agent_view.append(d)

				print "recieve from " + name + " to " + self.myAgent.getName() + "\n"


	def _setup(self) :
		print "Setup agent: ", self.getName() + "\n"

		self.priority = getPriority(self.getName())

		val = random.randint(0, 1)

		if val < 0.5 :
			self.value = 'NS'
		else:
			self.value = 'EW'

		self.agent_view = []
		self.good_list = []
		self.m = 0
		self.Fstar = 0

		sender = self.InitSend()
		self.addBehaviour(sender, None)

		init_template = spade.Behaviour.ACLTemplate()
		init_template.setOntology("init")
		mt1 = spade.Behaviour.MessageTemplate(init_template)

		init = self.InitReceive()
		self.addBehaviour(init, mt1)

		checkAgentView = self.CheckAgentView(2)
		self.addBehaviour(checkAgentView, None)

		value_template = spade.Behaviour.ACLTemplate()
		value_template.setOntology("value")
		mt2 = spade.Behaviour.MessageTemplate(value_template)

		value = self.ValueReceive(2)
		self.addBehaviour(value, mt2)

		print "setup(over)\n"

	def getfcost(self, agent, direction) :
		if self.value == direction :
			if agent['value'] == self.value :
				return 0;

			else :
				return (float(VehiclesFrom(agent, self.name, direction)) / float(self.priority))

		else :
			return 2 * (float(VehiclesFrom(agent, self.name, direction)) / float(self.priority))


	def getFcost(self) :
		Fcost = 0

		neighbours = getNeighbours(self.name)

		nsTraffic = 0
		ewTraffic = 0

		i, j = getAgentLoc(self.name)

		for neighbour in neighbours :
			if neighbour[0] == i and neighbour[1] < j :
				ewTraffic += traffic['row'][neighbour[1]]

			elif neighbour[0] == i and neighbour[1] > j :
				ewTraffic += traffic['row'][j]

			elif neighbour[1] == j and neighbour[0] < i :
				nsTraffic += traffic['col'][neighbour[0]]

			elif neighbour[1] == j and neighbour[0] > i :
				nsTraffic += traffic['col'][j]

		if nsTraffic >= ewTraffic :
			for agent in self.good_list :
				agent_i, agent_j = getAgentLoc(agent['name'])
				if agent_j == j :
					Fcost += self.getfcost(agent, "NS")

		else :
			for agent in self.good_list :
				agent_i, agent_j = getAgentLoc(agent['name'])
				if agent_i == i :
					Fcost += self.getfcost(agent, "EW")

		return Fcost

if __name__ == "__main__" :
	traffic = initializeTraffic(GRID_SIZE)

	grid = [[JunctionController(getName(i, j), getPwd(i, j)) for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]

	for row in grid:
		for junction in row:
			junction.start()
