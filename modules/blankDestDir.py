import shutil
import os

from . import Module

class BlankDestDir(Module):
    def run(self, render):
        if os.path.exists(render.dest):
            self.log(f'Removing {render.dest}')
            shutil.rmtree(render.dest)

        os.makedirs(render.dest, exist_ok=True)
