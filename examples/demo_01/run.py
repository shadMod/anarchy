#! /usr/bin/env python3

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

import os
import sys
import logging

from http import HTTPStatus
from importlib import import_module

DEMO_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path += [os.path.join(DEMO_DIR, "..", ".."), os.path.join(DEMO_DIR, "project")]  # brutal force to imports

logger = logging.getLogger("anarchy_main")


def main():
    from src.core.service import start_cli_service

    try:
        import hub

        mod = import_module("hub")
    except ModuleNotFoundError as ex:
        logger.error(ex)  # TODO: if DEBUG is True put traceback
        return print(HTTPStatus.NOT_FOUND)
    except Exception as ex:
        logger.error(ex)  # TODO: if DEBUG is True put traceback
        return print(ex)

    env = (os.environ.get("env") or "prod").lower()
    is_dev = env == "dev" or env == "local"
    port, autoreload_observer = start_cli_service(autoreload=is_dev, mod=mod)
    if autoreload_observer:
        # move autoreload observer to the foreground, so process won't exit while reloading
        autoreload_observer.join()


if __name__ == "__main__":
    main()
