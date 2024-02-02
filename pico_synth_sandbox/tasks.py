# pico_synth_sandbox/tasks.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import time, asyncio
from pico_synth_sandbox import clamp

_tasks = []

class Task:
    def __init__(self, update_frequency=1):
        self.set_update_frequency(update_frequency)
        self._async_paused = False
        self._async_task = None
        self.register()
        global _tasks
        _tasks.append(self)
    def set_update_frequency(self, frequency=1):
        self._async_time = max(1.0/float(clamp(frequency, 1, 1000)), 0.001)
    def register(self):
        if not self._async_task is None: return
        self._async_task = asyncio.get_event_loop().create_task(self.loop())
    def cancel(self):
        if not self._async_task is None and self._async_task.cancel():
            self._async_task = None
    def pause(self):
        self._async_paused = True
    def resume(self):
        self._async_paused = False
    async def loop(self):
        while True:
            try:
                start = time.monotonic()
                if not self._async_paused:
                    await self.update()
                await asyncio.sleep(max(self._async_time - (time.monotonic() - start), 0.001))
            except asyncio.CancelledError:
                break
    async def update(self):
        pass

def run():
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    finally:
        loop.close()
def stop():
    asyncio.get_event_loop().stop()
def pause():
    global _tasks
    for task in _tasks:
        task.pause()
def resume():
    for task in _tasks:
        task.resume()
