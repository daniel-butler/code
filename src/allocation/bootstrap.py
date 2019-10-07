from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from allocation import config, messagebus, orm, redis_pubsub, unit_of_work
from allocation.notifications import EmailNotifications

DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(
    config.get_postgres_uri(),
    isolation_level="SERIALIZABLE"
))

EMAIL_HOST = config.get_email_host_and_port()['host']
EMAIL_PORT = config.get_email_host_and_port()['port']


def bootstrap(
        start_orm=orm.start_mappers,
        session_factory=DEFAULT_SESSION_FACTORY,
        notifications=None,
        publish=redis_pubsub.publish,
):
    start_orm()
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory=session_factory)
    if notifications is None:
        notifications = EmailNotifications(smtp_host=EMAIL_HOST, port=EMAIL_PORT)
    bus = messagebus.MessageBus(uow=uow, notifications=notifications, publish=publish)
    uow.set_bus(bus)
    return bus
