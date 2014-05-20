from __future__ import absolute_import

from celery import Celery

app = Celery('friendfund', include=['friendfund.tasks.celerytasks.ecard_renderer',
                                    'friendfund.tasks.celerytasks.fb',
                                    'friendfund.tasks.celerytasks.twitter',
                                    'friendfund.tasks.celerytasks.photo_renderer'])

app.config_from_object('celeryconfig')


if __name__ == '__main__':
    app.start()
