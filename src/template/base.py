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

logger = logging.getLogger("anarchy_template")

STATUS_OK = 200  # get from constants


class TemplateBase:
    def render_template(self, handler):
        handler.send_response(STATUS_OK)
        handler.send_header("Content-type", "text/html")
        handler.end_headers()
        # write html
        handler.wfile.write(
            """
<html>
<head>

	<title>
		Index - Anarchy
	</title>

	<style>
		.w-100 {
			width: 100%;
		}

		.bg-black {
			background-color: #000;
		}

		.text-center {
			text-align: center;
		}

		.text-white {
			color: white;
		}
	</style>

</head>
<body class="bg-black">

<div class="w-100 text-center">
	<h1 class="text-white">
		Hello Man!
	</h1>
	<img src="https://i.gifer.com/n8E.gif">
</div>

</body>
</html>
            """.encode()
        )
