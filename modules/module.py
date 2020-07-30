import io


class Module:
    def run(self, render):
        pass

    def handle(self, render, subscription, event):
        pass

    def log(self, *args):
        print('::', *args)
    
    def error(self, *args):
        output = io.StringIO()
        print(*args, file=output, end="")
        error = output.getvalue()
        output.close()

        print(f'\033[91m{error}\033[m')
