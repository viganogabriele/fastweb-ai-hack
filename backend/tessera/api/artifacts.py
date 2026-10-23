"""Current operational artifacts, with exact historical citations still readable."""

from tessera.core.contracts.common import DerivedRecord


class CurrentArtifacts:
    """Keep follow-up support out of queues, counts and decision inputs.

    The answer worker reserves ``parent:`` versions for remapped derived lineage.
    Source documents/segments stay visible; only explicit version pins can read
    historical derived records. The canonical repository remains unchanged.
    """

    def __init__(self, repo):
        self._repo = repo

    def __getattr__(self, name):
        return getattr(self._repo, name)

    @staticmethod
    def _historical(record):
        return isinstance(record, DerivedRecord) and record.version.startswith("parent:")

    def list(self, kind, **filters):
        return [r for r in self._repo.list(kind, **filters) if not self._historical(r)]

    def get(self, kind, id, version=None):
        record = self._repo.get(kind, id, version)
        if version is None and self._historical(record):
            # Do not let insertion order turn a support record into the current
            # version, or hide an actual current version of the same identity.
            current = self.list(kind, where={"id": id})
            return current[-1] if current else None
        return record
