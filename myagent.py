"""import spade
import time

class MyAgent(spade.Agent.Agent):
	def _setup(self):
		#Every SPADE agent should override this method. It is where the initialization (or setup) code of the agent must be placed.
		print "MyAgent starting . . ."

if __name__ == "__main__":
	a = MyAgent("dolores@127.0.0.1", "secret")
	print "before start"
	a.start() #agent goes into asynchronous init i.e. _setup after this. 
	time.sleep(10)
	print "after start"
The next thing the script does is to actually start the agent with the start() method. It is very important to understand that
 when an agent is created, it does not start working automatically. The start() method must be called first in order to trigger
 the agent execution."""
import spade

class MyAgent(spade.Agent.Agent):
	class MyBehav(spade.Behaviour.PeriodicBehaviour): #mediate, polling, eval, ask
	#use MyBehav(spade.Behaviour.PeriodicBehaviour): refer to documentation
	#spade.Behaviour.EventBehaviour
		def onStart(self):
			print "Starting behaviour of agent:"
			self.counter = 0

		def _onTick(self):
			print "Counter:",self.counter
			# print self.getName(), "'s Counter:", self.counter
			self.counter = self.counter + 1
			if self.counter==2:
				print "shutdown"
				print self.myAgent
				try:
					self.myAgent._kill()
				except Exception,e:
					print str(e)
			# 	self._kill() 
			# 	self._owner.stop() 
			# 	err = None 
			# 	if err == None or err == 0:  # None or zero the integer, socket closed 
			# 		self._owner.DEBUG("Agent disconnected: "+self._owner.getAID().getName()+" (dying)","err") 
			# 		self._kill() 
			# 		self._owner.stop() 

	def _setup(self):
		# print "MyAgent starting<<<",self._aid,">>>>"
		print "<",self.getName(),">"
		b = self.MyBehav(1) #change it for test runs maybe even milli seconds
		self.addBehaviour(b, None)

if __name__ == "__main__":
	dolores = MyAgent("dolores@127.0.0.1", "secret")
	teddy = MyAgent("teddy@127.0.0.1", "secret")
	dolores.start()
	teddy.start()