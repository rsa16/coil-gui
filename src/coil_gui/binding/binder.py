from typing import Any, Callable, Optional
from .observable import Observable

def bind(target: Any, property_name: str, observable: Observable, transform: Optional[Callable[[Any], Any]] = None) -> Callable[[], None]:
    """
    Binds a target object's property to an Observable.
    When the observable changes, the target's property is updated.
    Supports nested property paths like "style.background_color".
    Returns a callable that can be used to unbind.
    """
    def observer(value: Any):
        val = transform(value) if transform is not None else value
        parts = property_name.split(".")
        obj = target
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], val)

    observable.subscribe(observer)
    return lambda: observable.unsubscribe(observer)