import falcon

from app import log

from app.api import rcvBibleWebHook
from app.database import redis_db
from app.errors import AppError

LOG = log.get_logger()

class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        LOG.info('API Server is starting')
        db = redis_db.RedisStorageEngine()
        self.add_route('/fb_rcvbiblebot/66d2b8f4a09cd35cb23076a1da5d51529136a3373fd570b122', rcvBibleWebHook.BibleResoure(db))
        self.add_error_handler(AppError, AppError.handle)

application = App()


if __name__ == "__main__":
    from wsgiref import simple_server
    httpd = simple_server.make_server('127.0.0.1', 8000, application)
    httpd.serve_forever()
