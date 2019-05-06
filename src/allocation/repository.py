from typing import Set
import abc
from allocation import model

from djangoproject.alloc import models as django_models

class AbstractRepository(abc.ABC):

    def __init__(self):
        self.seen = set()  # type: Set[model.Batch]

    @abc.abstractmethod
    def add(self, batch):
        self.seen.add(batch)

    def get(self, reference):
        p = self._get(reference)
        if p:
            self.seen.add(p)
        return p

    @abc.abstractmethod
    def _get(self, sku):
        raise NotImplementedError



class DjangoRepository(AbstractRepository):

    def __init__(self):
        super().__init__()

    def add(self, batch):
        super().add(batch)
        self.update(batch)

    def update(self, batch):
        django_models.Batch.update_from_domain(batch)

    def _get(self, reference):
        batch = django_models.Batch.objects.filter(
            reference=reference
        ).first().to_domain()
        self.seen.add(batch)
        return batch

    def list(self):
        return [b.to_domain() for b in django_models.Batch.objects.all()]

