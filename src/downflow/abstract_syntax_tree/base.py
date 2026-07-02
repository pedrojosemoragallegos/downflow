from __future__ import annotations


class Node: ...


class ContainerNode(Node):
    def __init__(self, children: list[Node]) -> None:
        self._children: list[Node] = children

    def append(self, node: Node, /) -> None:
        if (
            self._children
            and isinstance(self._children[-1], LeafNode)
            and isinstance(node, LeafNode)
            and type(self._children[-1]) is type(node)
        ):
            self._children[-1]._content += node._content  # type: ignore[attr-defined]
        else:
            self._children.append(node)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._children!r})"


class LeafNode(Node):
    def __init__(self, content: str) -> None:
        self._content: str = content

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._content!r})"


## Block nodes
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


class LinkNode(ContainerNode): ...


class ImageNode(ContainerNode): ...


class StrikethroughNode(ContainerNode): ...


class CodeSpanNode(LeafNode): ...


class AutoLinkNode(LeafNode): ...


class RawHTMLNode(LeafNode): ...


class HardlineBreakNode(LeafNode): ...


class SoftlineBreakNode(LeafNode): ...


class TextNode(LeafNode): ...
