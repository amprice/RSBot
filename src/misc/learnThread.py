
#from concurrent.futures import thread
import threading
from threading import Event
import time

class ThreadWrapper():
	ev_exit = threading.Event()
	runloop_period = 10

	def __init__(self, thread_name : str, timeout, function_ptr : 'function', function_param = None) -> None:
		self.name = thread_name
		self.event = threading.Event()
	
		self.timeout = timeout
		self.thread : threading.Thread = None
		
		self.work_func = function_ptr
		self.work_func_param = function_param

	def run(self):
		while (not ThreadWrapper.ev_exit.is_set()):
			self.event.wait(timeout=self.timeout)
			#print ('Thread {0} {1} Run: {2}'.format(threading.current_thread().native_id, self.txt, i))
			if self.work_func_param == None:
				self.work_func()
			else:
				self.work_func(self.work_func_param)
			
			# if QueueThread.ev_exit.is_set():
			# 	break;

		print ('Ending Thread {}'.format(threading.current_thread().native_id))
		

	def start(self):
		if (self.thread != None):
			while self.thread.is_alive():
				self.thread.join()
			
		self.thread = threading.Thread(target=self.run, args=())
		self.thread.name = self.name
		self.thread.start()
		
	def sendEvent(self):
		self.event.set()

	@staticmethod
	def disable():
		ThreadWrapper.ev_exit.set()
		
	@staticmethod
	def enable():
		ThreadWrapper.ev_exit.clear()

# def somethingToDo(e : Event):
# 	e.wait(timeout=10)
# 	print('somethingToDo: Hello from Thread ID: {0}'.format(threading.current_thread().native_id))

# def somethingToDo1(e : Event):
# 	e.wait(timeout=10)
# 	print('somethingToDo1: Hello from Thread ID: {0}'.format(threading.current_thread().native_id))

# async def cotoraiseevent():
# 	print('cotoraiseevent: Hello from Thread ID: {0}'.format(threading.current_thread().native_id))
# 	e.set()
def somefuction():
	print ('{0} {1}'.format(threading.current_thread().native_id, threading.current_thread().name))

if __name__ == '__main__':
	# e = threading.Event()
	# print('main: Hello from Thread ID: {0}'.format(threading.current_thread().native_id))
	# #for i in range(2):
	# threading.Thread(target=somethingToDo, args=(e,)).start()
	# threading.Thread(target=somethingToDo1, args=(e,)).start()

	# asyncio.run(cotoraiseevent())
	q1 = ThreadWrapper('Thread A', 10, somefuction)
	q2 = ThreadWrapper('Thread B', 1, somefuction)
	q3 = ThreadWrapper('Thread C', 5, somefuction)

	q1.start()
	q2.start()
	q3.start()

	time.sleep(20)

	ThreadWrapper.disable()

	time.sleep(10)

	ThreadWrapper.enable()
	q1.start()


	time.sleep(20)
	ThreadWrapper.disable()
	#q1.start()