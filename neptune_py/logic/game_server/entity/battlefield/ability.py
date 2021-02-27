import abc
from .components import ComponentMixin


class AbilityComponent(ComponentMixin):
    @abc.abstractmethod
    def Cast(self):
        pass
