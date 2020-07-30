import time

from watchdog.observers import Observer

from .modules import Module


class WatchdogHandler:
    def __init__(self, render, path, index):
        self.__path = path
        self.__render = render
        self.__index = index
        self.watcher = None

    def dispatch(self, event):
        self.__render.handle(self.__path, self.__index, event, self.watcher)


class Render:
    def __init__(self, modules, dest="dist"):
        self.modules = [i for i in modules if i]
        assert all(isinstance(i, Module) for i in self.modules)
        self.watchers = {}

        self.options = {}
        self.observer = None
        self.dest = dest

    def start(self, watch=False):
        self.run_once()

        if not watch:
            return

        if not self.watchers:
            print("Nothing to do!")
            return

        self.observer = Observer()

        for path in self.watchers:
            for index in range(len(self.watchers[path])):
                handler = WatchdogHandler(self, path, index)
                handler.watcher = self.observer.schedule(handler, path, recursive=True)

        self.observer.start()

        print(':: Watchdog started')
        while True:
            time.sleep(1)
        
    def handle(self, path, index, event, watcher):
        module, options = self.watchers[path][index]

        self.watchers[path].pop(index)
        self.observer.unschedule(watcher)
        new_watchers = []

        def watch(path, **options):
            self.watchers[path].insert(index, (module, options))
            new_watchers.append(path)
        self.watch = watch

        module.handle(self, path, event, **options)

        if not new_watchers:
            print("Watcher unregistered!")
        else:
            for n, path in enumerate(new_watchers):
                handler = WatchdogHandler(self, path, index + n)
                handler.watcher = self.observer.schedule(handler, path, recursive=True)

    def run_once(self):
        self.watchers = {}
        for i in self.modules:
            def watch(path, **options):
                if path not in self.watchers:
                    self.watchers[path] = []
                self.watchers[path].append((i, options))

            self.watch = watch
            i.run(self)
    
    def abort(self):
        print()
        print("Aborted!")
        quit()
