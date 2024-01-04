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

import logging
import os.path

from project.settings import TEMPLATE

logger = logging.getLogger("anarchy_template")

STATUS_OK = 200  # get from constants


class TemplateBase:
    template_name = None

    def get_template_name(self) -> str:
        return self.template_name

    @property
    def render_template(self) -> bytes:
        # handler.send_response(STATUS_OK)
        # handler.send_header("Content-type", "text/html")
        # handler.end_headers()
        # # write html
        # handler.wfile.write(
        #    "<h1>template</h1>"
        # )

        if not self.get_template_name or isinstance(self.get_template_name, str):
            raise Exception("No template_name")

        with open(os.path.join(TEMPLATE, self.template_name), "rb") as fn:
            return fn.read()
