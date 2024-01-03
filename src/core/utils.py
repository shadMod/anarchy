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
import socket

root_path = os.path.dirname(os.path.dirname(__file__))


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def file_path_to_module_name(path: str) -> str:
    """Convert file path to module name"""
    return (
        os.path.abspath(path)
        .replace(root_path, "of")
        .replace(".py", "")
        .replace("/__init__", "")
        .replace("/", ".")
    )
