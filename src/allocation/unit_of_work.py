# pylint: disable=attribute-defined-outside-init
import abc
from django.db import transaction

from allocation import config, repository


class AbstractUnitOfWork(abc.ABC):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def init_repositories(self, batches: repository.AbstractRepository):
        self._batches = batches

    @property
    def batches(self) -> repository.AbstractRepository:
        return self._batches



class DjangoUnitOfWork(AbstractUnitOfWork):

    def __enter__(self):
        self.init_repositories(repository.DjangoRepository())
        transaction.set_autocommit(False)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        transaction.set_autocommit(True)

    def commit(self):
        for batch in self.batches.seen:
            self.batches.update(batch)
        transaction.commit()

    def rollback(self):
        transaction.rollback()
