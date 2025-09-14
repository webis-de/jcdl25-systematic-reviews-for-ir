from nicegui import ui
from src import start_app
from dotenv import load_dotenv
import os

load_dotenv()

DEMO_PORT = os.getenv('DEMO_PORT')

ui.run(title='IR Anthology Boolean Search Demo', port=DEMO_PORT if DEMO_PORT else 8080, reconnect_timeout=30, reload=False)
start_app()
