from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

from downflow.abstract_syntax_tree.base import Node
from downflow.handler.container_blocks import ContainerBlock
from downflow.handler.container_inlines import ContainerInline
from downflow.handler.leaf_blocks import LeafBlock
from downflow.handler.leaf_inlines import LeafInline

from .action import Action

if TYPE_CHECKING:
    from downflow.abstract_syntax_tree.base import Node
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

    def _dispatch(self) -> Action:  # noqa: PLR0911
        self._cursor: Cursor = cast(
            typ="Cursor",
            val=self._cursor,
        )

        if not self._stack:
            print("STACK IS EMPTY, TRYING TO FIND A HANDLER")

            handler = self._container_block_chain(
                self._cursor.current,
                cast(
                    typ="str",
                    val=self._cursor.peek,
                ),
            ) or self._leaf_block_chain(
                self._cursor.current,
                cast(
                    typ="str",
                    val=self._cursor.peek,
                ),
            )

            if not handler:
                raise RuntimeError("No handler found!")

            print(f"FOUND HANDLER: {handler.__class__.__name__}")

            self._stack.append(handler)

            return handler(
                self._cursor.current,
                cast(
                    typ="str",
                    val=self._cursor.peek,
                ),
            )

        if isinstance(self._stack[-1], ContainerBlock):
            print("TOP OF STACK IS CONTAINER BLOCK")

            action = self._stack[-1](
                self._cursor.current,
                cast(typ="str", val=self._cursor.peek),
            )

            if action is not Action.DELEGATE:
                return action

            print("CONTAINER DELEGATED, TRYING TO FIND A CHILD HANDLER")

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
                print(f"FOUND HANDLER: {handler.__class__.__name__}")

                self._stack.append(handler)

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
            print("TOP OF STACK IS CONTAINER INLINE, TRYING TO FIND A HANDLER")

            handler = self._container_inline_chain(
                self._cursor.current,
                cast(typ="str", val=self._cursor.peek),
            ) or self._leaf_inline_chain(
                self._cursor.current,
                cast(typ="str", val=self._cursor.peek),
            )

            if handler is not None:
                print(f"FOUND HANDLER: {handler.__class__.__name__}")

                self._stack.append(handler)
                return handler(
                    self._cursor.current,
                    cast(
                        typ="str",
                        val=self._cursor.peek,
                    ),
                )

        if isinstance(self._stack[-1], LeafInline):
            print("TOP OF STACK IS LEAF INLINE, CALLING IT")

            return self._stack[-1](
                self._cursor.current,
                cast(
                    typ="str",
                    val=self._cursor.peek,
                ),
            )

        return Action.ADVANCE

    def __call__(self, cursor: Cursor) -> list[Node]:
        self._cursor: Cursor = cursor

        while True:
            if self._cursor.peek is None:
                print("End of input reached, may not all tags were closed")
                # TODO: handle stack unclosed tags
                break

            action: Action = self._dispatch()

            print(f"Action: {action}")

            match action:
                case Action.ADVANCE:
                    self._cursor.advance()

                case Action.POP:
                    self._stack.pop()

                case Action.POP_AND_ADVANCE:
                    self._stack.pop()
                    self._cursor.advance()

        self._cursor: None = None
        return self._document
