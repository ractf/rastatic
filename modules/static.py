import shutil
import os

from . import Module

class StaticHandler(Module):
    def __init__(self, input, output=None):
        self.input = input
        self.output = output if output is not None else input

    def logpath(self, path, names):
        if isinstance(path, str):
            print(f'    {path} -> {self.render.dest}/{self.output}/{path}')
        else:
            print(f'    {path.path} -> {self.render.dest}/{self.output}/{path.path}')
        return []

    def run(self, render):
        self.render = render

        if not os.path.exists(self.input):
            self.log(f"Cannot possibly copy {self.input} - it doesn't exist!")
            return render.abort()

        if os.path.isfile(self.input):
            self.log(f'Copying {self.input} -> {render.dest}/{self.output}')
            shutil.copy(self.input, render.dest + '/' + self.output)
        else:
            self.log(f'Copying static files')
            shutil.copytree(self.input, render.dest + '/' + self.output, ignore=self.logpath, dirs_exist_ok=True)

        render.watch(self.input)
    
    def handle(self, render, subscription, event):
        render.watch(subscription)

        output = render.dest + "/" + self.output + "/" + event.src_path[len(subscription):]

        if isinstance(event, (FileModifiedEvent, FileCreatedEvent)):
            if isinstance(event, FileModifiedEvent):
                os.remove(output)
            self.log(f'Copying {event.src_path} -> {output}')
            shutil.copy(event.src_path, output)
        elif isinstance(event, (FileDeletedEvent)):
            os.remove(output)
        else:
            print("Unhandled file event:", subscription, event)
