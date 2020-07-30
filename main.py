@click.command()
@click.option("--watch/--no-watch", default=False, help="Start a development server and watch for changes")
@click.option("--host", default="0.0.0.0", help="Development server host")
@click.option("--port", default=3000, help="Development server port")
def main(watch, host, port):
    modules = [
        BlankDir(DEST),

        StaticHandler('challenge1'),
        StaticHandler('favicon.ico'),
        StaticHandler('wordmark.png'),

        StaticHandler('brand_assets/'),
        StaticHandler("static/"),

        Jinja2Pages(splat_index=True),

        DevelopmentServer(host, port) if watch else None,
    ]

    Render(modules).start(watch=watch)
