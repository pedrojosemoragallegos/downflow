from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

from downflow.handler.container_blocks import ContainerBlock, InlineContainerBlock
from downflow.handler.container_inlines import ContainerInline
from downflow.handler.leaf_blocks import LeafBlock
from downflow.handler.leaf_inlines import LeafInline
from downflow.mapper import Mapper

from .action import Action

if TYPE_CHECKING:
    from downflow.abstract_syntax_tree.base import ContainerNode, Node
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
        block_fallback: type[InlineContainerBlock] | None = None,
        mapper: Mapper | None = None,
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
        self._block_fallback: Final[type[InlineContainerBlock] | None] = block_fallback
        self._mapper: Final[Mapper] = mapper if mapper is not None else Mapper()

        self._stack: list[
            ContainerBlock | LeafBlock | ContainerInline | LeafInline
        ] = []
        self._tree: list[Node] = []

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
            self._mapper.finalize(handler, self._tree[-1])
            if self._stack and isinstance(
                self._stack[-1],
                (ContainerBlock, ContainerInline),
            ):
                node: Node = self._tree.pop()
                cast(typ="ContainerNode", val=self._tree[-1]).append(node)
        else:
            node: Node = self._mapper[type(handler)](handler.content)  # type: ignore[union-attr]
            if self._stack and isinstance(
                self._stack[-1],
                (ContainerBlock, ContainerInline),
            ):
                cast(typ="ContainerNode", val=self._tree[-1]).append(node)
            else:
                self._tree.append(node)

    def _match_block(
        self,
        current: str,
        peek: str,
    ) -> ContainerBlock | LeafBlock | None:
        handler = self._container_block_chain(current, peek) or self._leaf_block_chain(
            current,
            peek,
        )
        if handler is None and self._block_fallback is not None:
            handler = self._block_fallback.matches(current, peek)
        return handler

    def _match_inline(
        self,
        current: str,
        peek: str,
    ) -> ContainerInline | LeafInline | None:
        return self._container_inline_chain(current, peek) or self._leaf_inline_chain(
            current,
            peek,
        )

    def _push(
        self,
        handler: ContainerBlock | LeafBlock | ContainerInline | LeafInline,
    ) -> None:
        self._stack.append(handler)
        if isinstance(handler, (ContainerBlock, ContainerInline)):
            self._tree.append(self._mapper[type(handler)]([]))  # type: ignore[arg-type]

    def _dispatch(self) -> Action:  # noqa: PLR0911
        cursor: Cursor = cast(typ="Cursor", val=self._cursor)
        current: str = cursor.current
        peek: str = cast(typ="str", val=cursor.peek)

        if not self._stack:
            handler = self._match_block(current, peek)
            if not handler:
                return Action.ADVANCE
            self._push(handler)
            return handler(current, peek)

        top = self._stack[-1]

        if isinstance(top, ContainerBlock):
            action: Action = top(current, peek)
            if action is not Action.DELEGATE:
                return action
            if isinstance(top, InlineContainerBlock):
                handler = self._match_inline(current, peek)
            else:
                handler = self._match_block(current, peek) or self._match_inline(
                    current,
                    peek,
                )
            if handler is not None:
                self._push(handler)
                return handler(current, peek)
            return Action.ADVANCE

        if isinstance(top, LeafBlock):
            return top(current, peek)

        if isinstance(top, ContainerInline):
            if current == "\n" and cursor.peek == "\n":
                return Action.POP
            action = top(current, peek)
            if action is not Action.DELEGATE:
                return action
            handler = self._match_inline(current, peek)
            if handler is not None:
                self._push(handler)
                return handler(current, peek)
            return Action.ADVANCE

        if isinstance(top, LeafInline):
            return top(current, peek)

        return Action.ADVANCE

    def __call__(self, cursor: Cursor) -> list[Node]:
        self._cursor: Cursor = cursor
        self._stack: list[
            ContainerBlock | LeafBlock | ContainerInline | LeafInline
        ] = []
        self._tree: list[Node] = []

        while True:
            if self._cursor.is_exhausted:
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
        return self._tree
