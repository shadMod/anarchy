# Source code of Anarchy Framework
# Copyright (C) 2023 shadMod <info@shadmod.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import time
import logging
import importlib
import threading

from typing import Set
from threading import Thread

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from .server import server as httpserver
from .utils import file_path_to_module_name, is_port_in_use, root_path

logger = logging.getLogger("anarchy_service")
logger.handlers = [logging.StreamHandler()]


def start_server_thread(mod, port: int) -> httpserver.HTTPServer:
    """Start the CLI http server in another thread"""
    try:
        importlib.reload(httpserver)  # always reload the module
    except SyntaxError:
        # ignore syntax error (which often means we are editing files)
        logger.exception("Reloading httpserver module failed")
        return
    server = httpserver.HTTPServer(mod, port)
    server_thread = Thread(target=lambda: server.start())
    server_thread.start()
    return server


class AutoreloadHandler(PatternMatchingEventHandler):
    """Auto reload handlers"""

    def __init__(
            self,
            server: httpserver.HTTPServer,
            patterns=None,
            ignore_patterns=None,
            ignore_directories=False,
            case_sensitive=False,
    ):
        super().__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.server = server
        self.needs_reload: Set[str] = set()  # modules that need to be reloaded

        # mark last update to make sure we only reload 1s after the last update
        self.last_updated_at = time.time()
        # start another thread to check if we need to reload
        threading.Thread(target=lambda: self.check_reload()).start()

    def reload_modules(self) -> None:
        logging.debug("%s modules updated", len(self.needs_reload))
        for mname in self.needs_reload:
            logging.debug(mname)
            if mname in sys.modules:
                importlib.reload(sys.modules[mname])
        self.needs_reload.clear()

    def check_reload(self) -> None:
        while True:
            if self.needs_reload and time.time() - self.last_updated_at > 1:
                logger.debug("Change detected, restarting service...\n")
                self.reload_modules()
                self.server.stop()
                mod = None
                new_server = start_server_thread(mod, self.server.server_port)
                if new_server:
                    self.server = new_server
            time.sleep(1)

    def on_any_event(self, event) -> None:
        self.needs_reload.add(file_path_to_module_name(event.src_path))
        self.last_updated_at = time.time()


def start_cli_service(mod=None, autoreload=True) -> (int, Observer):
    port, max_port = httpserver.PORT_RANGE
    while port < max_port and is_port_in_use(port):
        port += 1

    server = start_server_thread(mod, port)
    observer = None

    if autoreload:
        # start autoreload watcher
        observer = Observer()
        observer.schedule(
            AutoreloadHandler(
                server=server,
                patterns=["*.py"],
                ignore_patterns=["__pycache__"],
            ),
            # monitor all files
            root_path,
            recursive=True,
        )
        observer.start()
        observer.on_thread_stop = lambda: server.stop()

    return port, observer
