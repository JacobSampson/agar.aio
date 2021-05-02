from threading import Lock
import os
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class DriverFactory:
    def __init__(self, url_format, port=None, num_servers=1):
        self.base_port = port
        self.curr_port = port
        self.url_format = url_format

        self.num_servers = num_servers

        # Multiprocessing
        self.mutex = Lock()

    def _setup(self):
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--log-level=3")
        # options.add_argument("--test-type")

        # return webdriver.Chrome(options=options)
        return webdriver.Chrome(options=options, executable_path="C:/agar.aio/scripts/chromedriver.exe")

    # Generate agents
    def create(self):
        # Thread-safe update port and create URL
        url = self.url_format
        if self.curr_port:
            self.mutex.acquire()
            self.curr_port = self.curr_port + 1
            
            if self.curr_port > (self.base_port + self.num_servers - 1):
                self.curr_port = self.base_port

            url = self.url_format.format(self.curr_port)
            self.mutex.release()

        # Create driver
        return self._setup(), url

class ServerFactory():
    def create(port):
        curr_env = os.environ.copy()

        curr_env["SERVER_PORT"] = f'{port}'
        curr_env["COMPOSE_PROJECT_NAME"] = f'agario-{port}'

        return subprocess.Popen(["docker-compose", "-f", "servers/gulp/docker-compose.yaml", "up", "--build"], env=curr_env, stdout=subprocess.DEVNULL).pid
