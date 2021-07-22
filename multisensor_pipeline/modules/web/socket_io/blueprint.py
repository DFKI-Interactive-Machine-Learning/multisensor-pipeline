from flask import Blueprint, render_template
from flask_socketio import SocketIO


def get_blueprint(socket_io: SocketIO) -> Blueprint:
    blueprint: Blueprint = Blueprint(
        'simple_page', __name__,
        template_folder='templates',
    )

    @blueprint.route('/favicon.ico')
    def favicon():
        return ""

    @blueprint.route('/robots.txt')
    def robots():
        return ""

    @blueprint.route('/')
    @blueprint.route('/index')
    @blueprint.route('/index.htm')
    @blueprint.route('/index.html')
    def index():
        return render_template(
            template_name_or_list='index.html',
            async_mode=socket_io.async_mode,
        )

    return blueprint
