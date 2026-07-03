from __future__ import annotations

from typing import TYPE_CHECKING

from downflow.abstract_syntax_tree.base import (
    ATXHeadingNode,
    AutoLinkNode,
    BlockquoteNode,
    CodeSpanNode,
    EmphasisNode,
    FencedCodeBlockNode,
    HardlineBreakNode,
    HTMLBlockNode,
    ImageNode,
    IndentedCodeBlockNode,
    LinkNode,
    LinkReferenceDefinitionNode,
    ListItemNode,
    ListNode,
    Node,
    OrderedListItemNode,
    ParagraphNode,
    RawHTMLNode,
    SoftlineBreakNode,
    StrikethroughNode,
    StrongEmphasisNode,
    TextNode,
    ThematicBreakNode,
)
from downflow.handler.container_blocks import (
    Blockquote,
    List,
    ListItem,
    OrderedListItem,
    Paragraph,
)
from downflow.handler.container_inlines import (
    Emphasis,
    Image,
    Link,
    Strikethrough,
    StrongEmphasis,
)
from downflow.handler.leaf_blocks import (
    ATXHeading,
    FencedCodeBlock,
    HTMLBlock,
    IndentedCodeBlock,
    LinkReferenceDefinition,
    ThematicBreak,
)
from downflow.handler.leaf_inlines import (
    AutoLink,
    CodeSpan,
    HardlineBreak,
    RawHTML,
    SoftlineBreak,
    Text,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from downflow.handler.base import Handler


class Mapper:
    def __init__(self) -> None:
        self._node_map: dict[type, Callable[..., Node]] = {
            Blockquote: BlockquoteNode,
            List: ListNode,
            ListItem: ListItemNode,
            OrderedListItem: OrderedListItemNode,
            ThematicBreak: ThematicBreakNode,
            ATXHeading: ATXHeadingNode,
            IndentedCodeBlock: IndentedCodeBlockNode,
            FencedCodeBlock: FencedCodeBlockNode,
            HTMLBlock: HTMLBlockNode,
            LinkReferenceDefinition: LinkReferenceDefinitionNode,
            Paragraph: ParagraphNode,
            Emphasis: EmphasisNode,
            StrongEmphasis: StrongEmphasisNode,
            Link: LinkNode,
            Image: ImageNode,
            Strikethrough: StrikethroughNode,
            CodeSpan: CodeSpanNode,
            AutoLink: AutoLinkNode,
            RawHTML: RawHTMLNode,
            HardlineBreak: HardlineBreakNode,
            SoftlineBreak: SoftlineBreakNode,
            Text: TextNode,
        }
        self._finalizers: dict[type, Callable[..., None]] = {
            Link: lambda h, n: setattr(n, "url", h.url),
            Image: lambda h, n: setattr(n, "url", h.url),
        }

    def __getitem__(self, handler_type: type) -> Callable[..., Node]:
        return self._node_map[handler_type]

    def register(
        self,
        handler_type: type,
        factory: Callable[..., Node],
        finalizer: Callable[..., None] | None = None,
        /,
    ) -> None:
        self._node_map[handler_type] = factory
        if finalizer is not None:
            self._finalizers[handler_type] = finalizer

    def finalize(self, handler: Handler, node: Node, /) -> None:
        for handler_type, fn in self._finalizers.items():
            if isinstance(handler, handler_type):
                fn(handler, node)
                return
