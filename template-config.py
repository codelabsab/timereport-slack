import jinja2
from os import getenv

config = {
    "bot_access_token": getenv("BOT_ACCESS_TOKEN"),
    "signing_secret": getenv("SIGNING_SECRET"),
    "backend_api_key": getenv("BACKEND_API_KEY"),
}
template_file = "config.json.j2"
destination = ".chalice/config.json"

with open(template_file) as INPUT:
    j2_template = jinja2.Template(INPUT.read())

rendered_file = j2_template.render(config)

with open(destination, "w") as OUTPUT:
    OUTPUT.write(rendered_file)
