
#from concurrent.futures import thread
import threading
from threading import Event
import time
import asyncio
from types import coroutine
import types
from typing import Coroutine

class ThreadWrapper():
	ev_exit = threading.Event()
	runloop_period = 10

	def __init__(self, thread_name : str) -> None:
		self.name = thread_name
		self.event = threading.Event()
	
		self.thread : threading.Thread = None
		
		self.loop = asyncio.new_event_loop()
		self.task = None

	def run(self):
		
		# Non Coroutine Version
		#while (not ThreadWrapper.ev_exit.is_set()):
		
			# self.event.wait(timeout=self.timeout)
			#print ('Thread {0} {1} Run: {2}'.format(threading.current_thread().native_id, self.txt, i))
			# if self.work_func_param == None:
			# 	self.work_func()
			# else:
			# 	self.work_func(self.work_func_param)
			
		asyncio.set_event_loop(self.loop)
		self.loop.run_forever()

		print ('Ending Thread {}'.format(threading.current_thread().native_id))
		

	def start(self):
		if (self.thread != None):
			while self.thread.is_alive():
				self.thread.join()
			
		self.thread = threading.Thread(target=self.run, args=(), daemon=True)
		self.thread.name = self.name
		self.thread.start()
		print ('Starting {1} ID:{0}'.format(self.thread.native_id, self.thread.name))

		
	def sendEvent(self):
		self.event.set()

	def stop(self):
		print ('Stopping Event Loop')
		self.loop.stop()

	def run_asyncfuncion(self, async_func):
		#self.task = asyncio.create_task(async_func)
		print (self.loop.is_running())
		self.task = self.loop.create_task(async_func)
		asyncio.run_coroutine_threadsafe(self.task, self.loop)
		

	# @staticmethod
	# def disable():
	# 	ThreadWrapper.ev_exit.set()
		
	# @staticmethod
	# def enable():
	# 	ThreadWrapper.ev_exit.clear()

	async def dowork(self):
		print ('{0} {1}'.format(threading.current_thread().native_id, threading.current_thread().name))	

	async def dosomething(self):
		t = self.loop.create_task(self.dowork())
		r = await(t)
		return r
		


# async def somefunction():
# 	return await asyncio.gather(t)

# async def somefuction1():
# 	print ('{0} {1}'.format(threading.current_thread().native_id, threading.current_thread().name))
	

if __name__ == '__main__':
	#t = asyncio.create_task(somefuction)
	q1 = ThreadWrapper('Thread A')
	q2 = ThreadWrapper('Thread B')
	q3 = ThreadWrapper('Thread C')

	# t = q3.loop.create_task(somefuction1())
	# asyncio.run_coroutine_threadsafe(somefunction(), q3.loop)

	

	q1.start()
	q2.start()
	q3.start()
	
	asyncio.run_coroutine_threadsafe(q3.dosomething(), q3.loop)

	#time.sleep(3)
	#q3.run_asyncfuncion(somefunction())
	#q2.run_asyncfuncion(somefuction)
	#q1.run_asyncfuncion(somefuction)

	time.sleep(3)

	q1.stop()
	q2.stop()
	q3.stop()