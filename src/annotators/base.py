from abc import ABC, abstractmethod

from src.schema import Annotation, Doc


class Annotator(ABC):
    name: str

    @abstractmethod
    def annotate(self, doc: Doc) -> Annotation: ...

    def annotate_all(self, docs: list[Doc]) -> list[Annotation]:
        return [self.annotate(d) for d in docs]