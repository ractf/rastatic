import os

from jinja2 import Environment, FileSystemLoader
from watchdog.events import FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

from . import Module


class Jinja2Pages(Module):
    def __init__(self, templates="templates", pages="pages", output="", splat_index=False, variables=None):
        self.templates = templates
        self.pages = pages
        self.output = output
        self.variables = None
        self.splat_index = splat_index

        self.env = Environment(loader=FileSystemLoader(templates))
    
    def get_variables(self, page):
        if self.variables is None:
            return {}
        elif callable(self.variables):
            return self.variables(page)
        return self.variables
    
    def get_error_page(self, in_fqn, error):
        return (
            "<html>"
                "<head>"
                    "<title>Error rendering page</title>"
                    "<meta http-equiv=\"refresh\" content=\"1\">"
                "</head>"
                "<body>"
                    f"<h1>Error rendering <code>{in_fqn}</code>:</h1>"
                    f"<h2><code>{error}</code></h2>"
                "</body>"
            "</html>"
        )

    def gen_paths(self, render, root, name=None):
        if name is None:
            name = os.path.basename(root)
            root = os.path.dirname(root)

        base = (root + '/').replace('\\', '/')
        while '//' in base:
            base = base.replace('//', '/')
        base = '/' + base[len(self.templates + self.pages) + 2:].strip('/') + '/'
        
        in_fqn = (self.pages + base + name).replace('//', '/')
        name = name[::-1].split(".")[-1][::-1]

        if self.splat_index and name != "index":
            name += "/index"
        out_fqn = (render.dest + base + name + ".html").replace('//', '/')

        return in_fqn, out_fqn
    
    def render_one(self, in_fqn, out_fqn):
        print(f'    {self.templates}/{in_fqn}', end='')

        try:
            template = self.env.get_template(in_fqn)
            rendered = template.render(**self.get_variables(in_fqn))
        except Exception as e:
            self.error(" -> [ERROR]")
            self.error(f"Error parsing template {in_fqn}: {e}")
            rendered = self.get_error_page(in_fqn, e)

        os.makedirs(os.path.dirname(out_fqn), exist_ok=True)
        with open(out_fqn, 'w') as f:
            f.write(rendered)

        print(f' -> {out_fqn}')

    def render_all(self, render):
        for root, _, files in os.walk(self.templates + "/" + self.pages):
            for name in files:
                self.render_one(*self.gen_paths(render, root, name))

    def run(self, render):
        self.render_all(render)

        render.watch(self.templates)
    
    def handle(self, render, subscription, event):
        if not event.src_path.replace("\\", "/").startswith(self.templates + "/" + self.pages):
            render.watch(subscription)
            self.log(f"Change detected in {event.src_path} - updating all pages")
            return self.render_all()

        in_fqn, out_fqn = self.gen_paths(render, *os.path.split(event.src_path))

        if isinstance(event, (FileModifiedEvent, FileCreatedEvent)):
            print(f"Change detected in {event.src_path} - updating page")
            if isinstance(event, FileModifiedEvent):
                os.remove(out_fqn)
            self.render_one(in_fqn, out_fqn)
        elif isinstance(event, (FileDeletedEvent)):
            print(f"{event.src_path} deleted - removing page")
            os.remove(out_fqn)
            return
        else:
            print("Unhandled file event:", subscription, event)

        render.watch(subscription)
