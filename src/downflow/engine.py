from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

from downflow.abstract_syntax_tree.base import (
    ATXHeadingNode,
    AutoLinkNode,
    BlockquoteNode,
    CodeSpanNode,
    ContainerNode,
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
    ContainerBlock,
    InlineContainerBlock,
    List,
    ListItem,
    OrderedListItem,
)
from downflow.handler.container_inlines import (
    ContainerInline,
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
    LeafBlock,
    LinkReferenceDefinition,
    Paragraph,
    ThematicBreak,
)
from downflow.handler.leaf_inlines import (
    AutoLink,
    CodeSpan,
    HardlineBreak,
    LeafInline,
    RawHTML,
    SoftlineBreak,
    Text,
)

from .action import Action

if TYPE_CHECKING:
    from collections.abc import Callable

_NODE_MAP: dict[type, Callable[..., Node]] = {
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

if TYPE_CHECKING:
    from downflow.cursor import Cursor

    from .handler import HandlerChain


class Engine:
    def __init__(
        self,
        *,
        container_block_chain: HandlerChain[ContainerBlock],
        leaf_block_chain: HandlerChain[LeafBlock],
        container_inline_chain: HandlerChain[ContainerInline],
        leaf_inline_chain: HandlerChain[LeafInline],
    ) -> None:
        self._cursor: Cursor | None = None

        self._container_block_chain: Final[HandlerChain[ContainerBlock]] = (
            container_block_chain
        )
        self._leaf_block_chain: Final[HandlerChain[LeafBlock]] = leaf_block_chain
        self._container_inline_chain: Final[HandlerChain[ContainerInline]] = (
            container_inline_chain
        )
        self._leaf_inline_chain: Final[HandlerChain[LeafInline]] = leaf_inline_chain

        self._stack: list[
            ContainerBlock | LeafBlock | ContainerInline | LeafInline
        ] = []
        self._document: list[Node] = []

    def append(
        self,
        handler: type[ContainerBlock | LeafBlock | ContainerInline | LeafInline],
        /,
    ) -> None:
        if issubclass(handler, ContainerBlock):
            self._container_block_chain.append(handler)
        elif issubclass(handler, LeafBlock):
            self._leaf_block_chain.append(handler)
        elif issubclass(handler, ContainerInline):
            self._container_inline_chain.append(handler)
        elif issubclass(handler, LeafInline):
            self._leaf_inline_chain.append(handler)
        else:
            raise TypeError(f"Invalid handler type: {type(handler)}")  # noqa: EM102

    def _emit(
        self,
        handler: ContainerBlock | LeafBlock | ContainerInline | LeafInline,
        /,
    ) -> None:
        if isinstance(handler, (ContainerBlock, ContainerInline)):
            if self._stack and isinstance(
                self._stack[-1],
                (ContainerBlock, ContainerInline),
            ):
                node: Node = self._document.pop()
                cast("ContainerNode", self._document[-1]).append(node)
        else:
            node = _NODE_MAP[type(handler)](handler.content)  # type: ignore[union-attr]
            if self._stack and isinstance(
                self._stack[-1],
                (ContainerBlock, ContainerInline),
            ):
                cast("ContainerNode", self._document[-1]).append(node)
            else:
                self._document.append(node)

    def _dispatch(self) -> Action:  # noqa: PLR0911
        self._cursor: Cursor = cast(
            typ="Cursor",
            val=self._cursor,
        )

        if not self._stack:
            handler = self._container_block_chain(
                self._cursor.current,
                cast(typ="str", val=self._cursor.peek),
            ) or self._leaf_block_chain(
                self._cursor.current,
                cast(typ="str", val=self._cursor.peek),
            )

            if not handler:
                return Action.ADVANCE

            self._stack.append(handler)
            if isinstance(handler, (ContainerBlock, ContainerInline)):
                self._document.append(_NODE_MAP[type(handler)]([]))  # type: ignore[arg-type]

            return handler(
                self._cursor.current,
                cast(typ="str", val=self._cursor.peek),
            )

        if isinstance(self._stack[-1], ContainerBlock):
            action: Action = self._stack[-1](
                self._cursor.current,
                cast(typ="str", val=self._cursor.peek),
            )

            if action is not Action.DELEGATE:
                return action

            if isinstance(self._stack[-1], InlineContainerBlock):
                handler = self._container_inline_chain(
                    self._cursor.current,
                    cast(typ="str", val=self._cursor.peek),
                ) or self._leaf_inline_chain(
                    self._cursor.current,
                    cast(typ="str", val=self._cursor.peek),
                )
            else:
                handler = (
                    self._container_block_chain(
                        self._cursor.current,
                        cast(typ="str", val=self._cursor.peek),
                    )
                    or self._leaf_block_chain(
                        self._cursor.current,
                        cast(typ="str", val=self._cursor.peek),
                    )
                    or self._container_inline_chain(
                        self._cursor.current,
                        cast(typ="str", val=self._cursor.peek),
                    )
                    or self._leaf_inline_chain(
                        self._cursor.current,
                        cast(typ="str", val=self._cursor.peek),
                    )
                )

            if handler is not None:
                self._stack.append(handler)
                if isinstance(handler, (ContainerBlock, ContainerInline)):
                    self._document.append(_NODE_MAP[type(handler)]([]))  # type: ignore[arg-type]

                return handler(
                    self._cursor.current,
                    cast(typ="str", val=self._cursor.peek),
                )

            return Action.ADVANCE

        if isinstance(self._stack[-1], LeafBlock):
            return self._stack[-1](
                self._cursor.current,
                cast(
                    typ="str",
                    val=self._cursor.peek,
                ),
            )

        if isinstance(self._stack[-1], ContainerInline):
            action: Action = self._stack[-1](
                self._cursor.current,
                cast(typ="str", val=self._cursor.peek),
            )

            if action is not Action.DELEGATE:
                return action

            handler = self._container_inline_chain(
                self._cursor.current,
                cast(typ="str", val=self._cursor.peek),
            ) or self._leaf_inline_chain(
                self._cursor.current,
                cast(typ="str", val=self._cursor.peek),
            )

            if handler is not None:
                self._stack.append(handler)
                if isinstance(handler, (ContainerBlock, ContainerInline)):
                    self._document.append(_NODE_MAP[type(handler)]([]))  # type: ignore[arg-type]

                return handler(
                    self._cursor.current,
                    cast(typ="str", val=self._cursor.peek),
                )

            return Action.ADVANCE

        if isinstance(self._stack[-1], LeafInline):
            return self._stack[-1](
                self._cursor.current,
                cast(typ="str", val=self._cursor.peek),
            )

        return Action.ADVANCE

    def __call__(self, cursor: Cursor) -> list[Node]:
        self._cursor: Cursor = cursor
        self._stack: list = []  # TODO: typehint
        self._document: list[Node] = []

        while True:
            if self._cursor.peek is None:
                while self._stack:
                    self._emit(self._stack.pop())
                break

            action: Action = self._dispatch()

            match action:
                case Action.ADVANCE:
                    self._cursor.advance()

                case Action.POP:
                    self._emit(self._stack.pop())

                case Action.POP_AND_ADVANCE:
                    self._emit(self._stack.pop())
                    self._cursor.advance()

        self._cursor: None = None
        return self._document
