from pathlib import Path
from typing import Iterable, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# json -> pydantic model
def read_jsonl(path: Path, model: Type[T]) -> list[T]:
    with open(path, encoding="utf-8") as f:
        return [model.model_validate_json(l) for l in f if l.strip()]

# Pydantic's model_validate_json() takes a JSON string, parses it and validates it against the specified model.
# Pydantic converts the JSON data into a Doc object and checks whether the data satisfies the model's validation rules. 
# if a field is missing -> validation error

# multiple pydantic models -> multiple json files
def write_jsonl(path: Path, items: Iterable[BaseModel]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True) # ensure dir containing output file exists
    with open(path, "w", encoding="utf-8") as f: # pass modeö
        for it in items: # iterate over pydantic model instances
            f.write(it.model_dump_json() + "\n") # convert model to json string