from typing import Dict, Any, List
from .selector import Selector

class StyleRule:
    """
    Represents a single style rule consisting of a selector and a set of properties.
    """

    def __init__(self, selector: str, properties: Dict[str, Any]):
        self.selector = Selector(selector)
        self.properties = properties


class StyleSheet:
    """
    A collection of style rules that can be applied to widgets.
    """

    def __init__(self):
        self.rules: List[StyleRule] = []
        self._update_counter: int = 0

    def add_rule(self, selector: str, properties: Dict[str, Any]):
        """
        Adds a new style rule to the stylesheet.

        Args:
            selector: A selector string (e.g., 'button.primary:hover').
            properties: A dictionary of style properties.
        """
        self.rules.append(StyleRule(selector, properties))
        self._update_counter += 1

    def compute_style(self, widget) -> Dict[str, Any]:
        """
        Computes the final style for a widget by matching it against all rules.
        Rules are applied in order of selector specificity.
        """
        computed = {}
        matched_rules = [rule for rule in self.rules if rule.selector.matches(widget)]
        matched_rules.sort(key=lambda r: r.selector.specificity)

        for rule in matched_rules:
            computed.update(rule.properties)

        return computed
