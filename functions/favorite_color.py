from __future__ import annotations

from typing import Tuple

from pipecat_flows import FlowArgs, FlowManager, FlowsFunctionSchema, NodeConfig


def _create_end_node() -> NodeConfig:
    return NodeConfig(
        name="create_end_node",
        task_messages=[
            {
                "role": "system",
                "content": "Thank the user for answering and end the conversation",
            }
        ],
        post_actions=[{"type": "end_conversation"}],
    )


async def record_favorite_color_and_set_next_node(
    args: FlowArgs, flow_manager: FlowManager
) -> Tuple[str, NodeConfig]:
    print(f"Your favorite color is: {args['color']}")
    return args["color"], _create_end_node()


def get_record_favorite_color_func() -> FlowsFunctionSchema:
    return FlowsFunctionSchema(
        name="record_favorite_color_func",
        description="Record the color the user said is their favorite.",
        required=["color"],
        handler=record_favorite_color_and_set_next_node,
        properties={"color": {"type": "string"}},
    )


