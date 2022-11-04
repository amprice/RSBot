
import os
import threading
from threading import Thread

import asyncio
from time import sleep

async def somethingToDo(e : asyncio.Event):
	for i in range(10):
		print('somethingToDo: Hello from Thread ID: {0}'.format(threading.current_thread().native_id))
		await asyncio.sleep(2)

	await e.wait()
	print ('Got event e')

async def somethingToDo1(e : asyncio.Event):
	for i in range(10):
		print('somethingToDo1: Hello from Thread ID: {0}'.format(threading.current_thread().native_id))
		await asyncio.sleep(1)
	e.set()

async def main():
	e = asyncio.Event()

	t1 = asyncio.create_task(somethingToDo(e))
	t2 = asyncio.create_task(somethingToDo1(e))

	await t1
	await t2
	#L = await asyncio.gather (t1, t2)
	#print (L)

	#await somethingToDo(e)
	#await somethingToDo1(e)

if __name__ == '__main__':
	#e = threading.Event()
	asyncio.run(main())

	#for i in range(2):
	#threading.Thread(target=somethingToDo, args=(e,)).start()
	#threading.Thread(target=somethingToDo1, args=(e,)).start()