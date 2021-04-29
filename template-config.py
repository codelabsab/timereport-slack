import jinja2
from os import getenv

config = {
    "backend_url": getenv("BACKEND_URL"),
    "bot_access_token": getenv("BOT_ACCESS_TOKEN"),
    "enable_queue": getenv("ENABLE_QUEUE", True),
    "environment": getenv("ENVIRONMENT", "dev"),
    "signing_secret": getenv("SIGNING_SECRET"),
}
template_file = "config.json.j2"
destination = ".chalice/config.json"

with open(template_file) as INPUT:
    j2_template = jinja2.Template(INPUT.read())

rendered_file = j2_template.render(config)

with open(destination, "w") as OUTPUT:
    OUTPUT.write(rendered_file)
