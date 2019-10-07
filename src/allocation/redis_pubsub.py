import json
import logging
from dataclasses import asdict
import redis
from allocation import bootstrap, config, commands, events, messagebus

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    logger.info('Redis pubsub starting')
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('change_batch_quantity')

    for m in pubsub.listen():
        handle_change_batch_quantity(m, bus)


def handle_change_batch_quantity(m, bus: messagebus.MessageBus):
    logger.info('handling %s', m)
    data = json.loads(m['data'])
    cmd = commands.ChangeBatchQuantity(ref=data['batchref'], qty=data['qty'])
    bus.handle(cmd)


def publish(channel, event: events.Event):
    logger.info('publishing: channel=%s, event=%s', channel, event)
    r.publish(channel, json.dumps(asdict(event)))


if __name__ == '__main__':
    main()
