import os

from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.getcwd(), 'dundie/templates')
env = Environment(loader=FileSystemLoader(template_dir))
