from typing import List, Any, Optional, Callable
from ..core.container import Container
from ..layout.flex import FlexLayout, FlexDirection
from .label import Label

class ListView(Container):
    def __init__(self, items: List[Any] = None, item_renderer: Optional[Callable[[Any], 'Widget']] = None, **kwargs):
        layout = kwargs.pop("layout", FlexLayout(direction=FlexDirection.COLUMN))
        super().__init__(layout=layout, **kwargs)
        self._items = items or []
        self._item_renderer = item_renderer or self._default_renderer
        self._rebuild_items()

    def _default_renderer(self, item: Any) -> 'Widget':
        return Label(str(item), padding=5)

    @property
    def items(self) -> List[Any]:
        return self._items

    @items.setter
    def items(self, value: List[Any]):
        self._items = value
        self._rebuild_items()

    def _rebuild_items(self):
        self.children.clear()
        for item in self._items:
            child = self._item_renderer(item)
            self.add_child(child)
        self.mark_layout_dirty()
