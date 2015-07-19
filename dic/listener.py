import logging


class ContainerListener(object):
    def resolve_started(self, context_id, component_type):
        """
        Called when a resolve operation starts.
        :param context_id: The unique id of the context (e.g. a top-level resolve operation).
        :param component_type: The type of the component being resolved.
        """
        pass

    def resolve_failed(self, context_id, component_type):
        """
        Called when any resolve operation fails.
        :param context_id: The unique id of the context (e.g. a top-level resolve operation).
        :param component_type: The type of the component being resolved.
        """
        pass

    def resolve_succeeded(self, context_id, component_type):
        """
        Called when any resolve operation fails.
        :param context_id: The unique id of the context (e.g. a top-level resolve operation).
        :param component_type: The type of the component being resolved.
        """
        pass


class LoggingListener(ContainerListener):
    def __init__(self, logger):
        self._logger = logger or logging.getLogger()

    def resolve_started(self, context_id, component_type):
        self._logger.debug('Resolving %s', component_type)

    def resolve_failed(self, context_id, component_type):
        self._logger.error('Failed to resolve %s', component_type)

    def resolve_succeeded(self, context_id, component_type):
        self._logger.debug('... resolved %s', component_type)
