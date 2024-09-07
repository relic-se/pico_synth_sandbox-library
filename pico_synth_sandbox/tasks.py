# pico_synth_sandbox/tasks.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import gc, time, asyncio
from pico_synth_sandbox import clamp

_tasks = []
_loop = None
_running = False

def get_loop(reset:bool=False):
    global _loop
    if reset and not _loop is None:
        _loop.stop()
    if reset or _loop is None:
        _loop = asyncio.new_event_loop()
    return _loop
def reset_loop():
    cancel_tasks()
    get_loop(True)
def register_task(task):
    global _tasks
    if not task in _tasks:
        _tasks.append(task)
    return get_loop().create_task(task.loop())
def register_tasks():
    global _tasks
    for task in _tasks:
        task.register()
def cancel_tasks():
    global _tasks
    for task in _tasks:
        task.cancel()

def run():
    global _running
    gc.collect()
    loop = get_loop()
    try:
        _running = True
        loop.run_forever()
    finally:
        _running = False
        loop.close()
def is_running() -> bool:
    global _running
    return _running
def stop():
    get_loop().stop()
def pause():
    global _tasks
    for task in _tasks:
        task.pause()
def resume():
    global _tasks
    for task in _tasks:
        task.resume()
def run_task(coro):
    if is_running():
        get_loop().run_until_complete(coro)
        register_tasks()
    else:
        asyncio.run(coro)

class Task:
    def __init__(self, update_frequency=1):
        self.set_update_frequency(update_frequency)
        self._async_paused = False
        self._async_task = None
        self.register()
    def set_update_frequency(self, frequency=1):
        self._async_time = max(1.0/float(clamp(frequency, 1, 1000)), 0.001)
    def register(self, task:asyncio.Task=None):
        self.cancel()
        if task is None:
            task = register_task(self)
        self._async_task = task
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
    def force_update(self):
        run_task(self.update())
