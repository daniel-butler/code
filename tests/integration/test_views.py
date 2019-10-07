# pylint: disable=redefined-outer-name
from datetime import date
from unittest import mock
from sqlalchemy.orm import sessionmaker, clear_mappers
import pytest
from allocation import bootstrap, commands, views


@pytest.fixture
def sqlite_bus(sqlite_session_factory):
    bus = bootstrap.bootstrap(
        start_orm=lambda: None,
        session_factory=sqlite_session_factory,
        notifications=mock.Mock(),
        publish=mock.Mock(),
    )
    yield bus
    clear_mappers()


def test_allocations_view(sqlite_bus):
    sqlite_bus.handle(commands.CreateBatch('b1', 'sku1', 50, None))
    sqlite_bus.handle(commands.CreateBatch('b2', 'sku2', 50, date.today()))
    sqlite_bus.handle(commands.Allocate('o1', 'sku1', 20))
    sqlite_bus.handle(commands.Allocate('o1', 'sku2', 20))

    assert views.allocations('o1', sqlite_bus.uow) == [
        {'sku': 'sku1', 'batchref': 'b1'},
        {'sku': 'sku2', 'batchref': 'b2'},
    ]


def test_deallocation(sqlite_bus):
    sqlite_bus.handle(commands.CreateBatch('b1', 'sku1', 50, None))
    sqlite_bus.handle(commands.CreateBatch('b2', 'sku1', 50, date.today()))
    sqlite_bus.handle(commands.Allocate('o1', 'sku1', 40))
    sqlite_bus.handle(commands.ChangeBatchQuantity('b1', 10))

    assert views.allocations('o1', sqlite_bus.uow) == [
        {'sku': 'sku1', 'batchref': 'b2'},
    ]
