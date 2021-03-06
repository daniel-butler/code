from datetime import datetime
from flask import Flask, jsonify, request
from allocation import (
    commands, exceptions, messagebus, notifications, orm, redis_pubsub,
    unit_of_work, views,
)

app = Flask(__name__)
orm.start_mappers()
uow = unit_of_work.SqlAlchemyUnitOfWork()
bus = messagebus.MessageBus(
    uow=uow,
    notifications=notifications.EmailNotifications(),
    publish=redis_pubsub.publish
)
uow.set_bus(bus)



@app.route("/add_batch", methods=['POST'])
def add_batch():
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    cmd = commands.CreateBatch(
        request.json['ref'], request.json['sku'], request.json['qty'], eta,
    )
    bus.handle(cmd)
    return 'OK', 201


@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    try:
        cmd = commands.Allocate(
            request.json['orderid'], request.json['sku'], request.json['qty'],
        )
        bus.handle(cmd)
    except exceptions.InvalidSku as e:
        return jsonify({'message': str(e)}), 400

    return 'OK', 202


@app.route("/allocations/<orderid>", methods=['GET'])
def allocations_view_endpoint(orderid):
    result = views.allocations(orderid, bus.uow)
    if not result:
        return 'not found', 404
    return jsonify(result), 200
