from __future__ import annotations


class Node: ...


class ContainerNode(Node):
    def __init__(self, children: list[Node]) -> None:
        self._children: list[Node] = children

    @property
    def children(self) -> list[Node]:
        return self._children

    def append(self, node: Node, /) -> None:
        if (
            self._children
            and isinstance(self._children[-1], LeafNode)
            and isinstance(node, LeafNode)
            and type(self._children[-1]) is type(node)
        ):
            self._children[-1].content += node.content  # type: ignore[union-attr]
        else:
            self._children.append(node)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._children!r})"


class LeafNode(Node):
    def __init__(self, content: str) -> None:
        self._content: str = content

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str, /) -> None:
        self._content = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.content!r})"


class BlockquoteNode(ContainerNode): ...


class ListNode(ContainerNode): ...


class ListItemNode(ContainerNode): ...


class OrderedListItemNode(ContainerNode): ...


class ThematicBreakNode(LeafNode): ...


class ATXHeadingNode(LeafNode): ...


class IndentedCodeBlockNode(LeafNode): ...


class FencedCodeBlockNode(LeafNode): ...


class HTMLBlockNode(LeafNode): ...


class LinkReferenceDefinitionNode(LeafNode): ...


class ParagraphNode(ContainerNode): ...


## Inline nodes
class EmphasisNode(ContainerNode): ...


class StrongEmphasisNode(ContainerNode): ...


class LinkNode(ContainerNode):
    def __init__(self, children: list[Node], url: str = "") -> None:
        super().__init__(children)
        self._url: str = url

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str, /) -> None:
        self._url = value


class ImageNode(ContainerNode):
    def __init__(self, children: list[Node], url: str = "") -> None:
        super().__init__(children)
        self._url: str = url

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str, /) -> None:
        self._url = value


class StrikethroughNode(ContainerNode): ...


class CodeSpanNode(LeafNode): ...


class AutoLinkNode(LeafNode): ...


class RawHTMLNode(LeafNode): ...


class HardlineBreakNode(LeafNode): ...


class SoftlineBreakNode(LeafNode): ...


class TextNode(LeafNode): ...
