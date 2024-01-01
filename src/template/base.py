import logging

logger = logging.getLogger("anarchy_template")

STATUS_OK = 200  # get from constants


class TemplateBase:
    def render_template(self, handler):
        handler.send_response(STATUS_OK)
        handler.send_header("Content-type", "text/html")
        handler.end_headers()
        # Send the html message
        handler.wfile.write(
            "<b> Hello World !</b>".encode()
        )
