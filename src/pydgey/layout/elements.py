"""UI layout elements and containers."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class UIElement:
    """Base class for all UI elements.

    UIElements form a tree structure that describes the layout
    of the pipeline widget interface. They are typically created using
    factory methods in `Layout` and `Field`.

    Attributes:
        type (str): Element type (e.g., 'page', 'section', 'row', 'card').
        props (Dict[str, Any]): Dictionary of properties passed to the frontend component.
        children (List[UIElement]): List of nested child elements.
        visible_when (Optional[Tuple[str, str, Any]]): Conditional visibility rule.
            Format: `(field_name, operator, value)`.
            Example: `("advanced_mode", "=", True)`.
    """

    type: str
    props: Dict[str, Any] = field(default_factory=dict)
    children: List["UIElement"] = field(default_factory=list)
    visible_when: Optional[Tuple[str, str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dict[str, Any]: JSON-serializable dictionary representation.
        """
        d: Dict[str, Any] = {
            "type": self.type,
            "props": self.props,
            "children": [c.to_dict() for c in self.children],
        }
        if self.visible_when:
            field_name, operator, value = self.visible_when
            d["visibleWhen"] = {
                "field": field_name,
                "operator": operator,
                "value": value,
            }
        return d


class Layout:
    """Factory methods for structural layout components.

    This class provides static methods to organize your UI into pages,
    sections, rows, tabs, and cards.
    """

    @staticmethod
    def Page(
        children: List[UIElement],
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Create the root page container.

        Every layout definition typically starts with `Layout.Page`.

        Args:
            children: List of child elements (Sections, Cards, etc.)
            visible_when: Optional visibility condition.
        """
        return UIElement("page", children=children, visible_when=visible_when)

    @staticmethod
    def Section(
        title: str,
        children: List[UIElement],
        description: str = "",
        collapsed: bool = False,
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Create a collapsible section.

        Args:
            title: Header text for the section.
            children: Content elements.
            description: Optional description text displayed below the title.
            collapsed: Whether the section starts collapsed by default.
            visible_when: Optional visibility condition.
        """
        return UIElement(
            "section",
            props={"title": title, "description": description, "collapsed": collapsed},
            children=children,
            visible_when=visible_when,
        )

    @staticmethod
    def Row(
        children: List[UIElement],
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Create a horizontal row.

        Arranges its children horizontally. Useful for placing multiple small
        fields side-by-side.

        Args:
            children: Elements to arrange horizontally.
            visible_when: Optional visibility condition.
        """
        return UIElement("row", children=children, visible_when=visible_when)

    @staticmethod
    def Tabs(
        children: List[UIElement],
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Create a tabbed interface container.

        Must contain `Layout.Tab` elements as children.

        Args:
            children: List of `Layout.Tab` elements.
            visible_when: Optional visibility condition.
        """
        return UIElement("tabs", children=children, visible_when=visible_when)

    @staticmethod
    def Tab(
        label: str,
        children: List[UIElement],
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Create a single tab within a `Layout.Tabs` container.

        Args:
            label: Text on the tab button.
            children: Content elements for this tab.
            visible_when: Optional visibility condition.
        """
        return UIElement(
            "tab",
            props={"label": label},
            children=children,
            visible_when=visible_when,
        )

    @staticmethod
    def Card(
        title: str,
        children: List[UIElement],
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Create a grouped card container.

        Cards provide a visually distinct grouping for related fields.

        Args:
            title: Title text at the top of the card.
            children: Content elements.
            visible_when: Optional visibility condition.
        """
        return UIElement(
            "card",
            props={"title": title},
            children=children,
            visible_when=visible_when,
        )

    @staticmethod
    def Text(
        content: str,
        class_name: str = "",
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Render a block of plain text.

        Args:
            content: The text string to display.
            class_name: Optional CSS class names (e.g. "text-muted").
            visible_when: Optional visibility condition.
        """
        return UIElement(
            "text",
            props={"content": content, "className": class_name},
            visible_when=visible_when,
        )

    @staticmethod
    def Html(
        content: str,
        class_name: str = "",
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Render raw HTML content.

        Allows embedding rich text, links, or custom markup.

        Args:
            content: The HTML string.
            class_name: Optional CSS class names.
            visible_when: Optional visibility condition.
        """
        return UIElement(
            "html",
            props={"content": content, "className": class_name},
            visible_when=visible_when,
        )
