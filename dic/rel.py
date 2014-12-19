class Relationship(object):
    def __init__(self):
        self._container = None


class FactoryRelationship(Relationship):
    def __init__(self, component_type):
        super().__init__()
        self.component_type = component_type

    def __call__(self, *args, **kwargs):
        return self._container.resolve(self.component_type)


def factory(component_type):
    """
    Models a factory relationship capable of creating the given type.
    :param component_type:
    :return: A factory relationship
    """
    return FactoryRelationship(component_type)



