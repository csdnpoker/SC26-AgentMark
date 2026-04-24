from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass, field
from importlib import import_module
from importlib.util import find_spec
from typing import Any, Callable


ToolHandler = Callable[[dict[str, Any]], str]


@dataclass(frozen=True)
class FrameworkAdapterStatus:
    framework: str
    package_name: str
    package_installed: bool
    integration_mode: str
    native_objects: tuple[str, ...] = ()
    reasoning_cycle: str = "ReAct"


@dataclass(frozen=True)
class UnifiedTool:
    name: str
    description: str
    handler: ToolHandler

    def invoke(self, action_input: dict[str, Any]) -> str:
        return self.handler(action_input)


@dataclass
class ReActStep:
    index: int
    thought: str
    action: str
    action_input: dict[str, Any]
    observation: str


@dataclass
class ReActRunResult:
    framework: str
    reasoning_cycle: str
    integration_mode: str
    package_installed: bool
    task: str
    final_answer: str
    framework_objects: list[str] = field(default_factory=list)
    trace: list[ReActStep] = field(default_factory=list)


@dataclass
class FrameworkRuntimeContext:
    status: FrameworkAdapterStatus
    native_objects: dict[str, Any] = field(default_factory=dict)
    invocation_mode: str = "shim"


class FrameworkAdapter:
    framework_name = "generic"
    package_name = ""

    def is_package_installed(self) -> bool:
        return bool(self.package_name and find_spec(self.package_name))

    def status(self) -> FrameworkAdapterStatus:
        installed = self.is_package_installed()
        return FrameworkAdapterStatus(
            framework=self.framework_name,
            package_name=self.package_name,
            package_installed=installed,
            integration_mode="native" if installed else "shim",
        )

    def build_runtime_context(self, tools: dict[str, UnifiedTool]) -> FrameworkRuntimeContext:
        status = self.status()
        return FrameworkRuntimeContext(status=status, invocation_mode=status.integration_mode)

    def invoke_tool(self, context: FrameworkRuntimeContext, tool_name: str, action_input: dict[str, Any], tools: dict[str, UnifiedTool]) -> str:
        return tools[tool_name].invoke(action_input)


class LangChainAdapter(FrameworkAdapter):
    framework_name = "langchain"
    package_name = "langchain"

    def build_runtime_context(self, tools: dict[str, UnifiedTool]) -> FrameworkRuntimeContext:
        if not self.is_package_installed():
            return super().build_runtime_context(tools)

        try:
            StructuredTool = import_module("langchain_core.tools").StructuredTool
            native_tools: dict[str, Any] = {}
            for tool in tools.values():
                native_tools[tool.name] = _build_langchain_tool(StructuredTool, tool)
            status = FrameworkAdapterStatus(
                framework=self.framework_name,
                package_name=self.package_name,
                package_installed=True,
                integration_mode="native",
                native_objects=tuple(f"StructuredTool:{name}" for name in native_tools),
            )
            return FrameworkRuntimeContext(status=status, native_objects=native_tools, invocation_mode="native")
        except Exception:
            return super().build_runtime_context(tools)

    def invoke_tool(self, context: FrameworkRuntimeContext, tool_name: str, action_input: dict[str, Any], tools: dict[str, UnifiedTool]) -> str:
        if context.invocation_mode != "native":
            return super().invoke_tool(context, tool_name, action_input, tools)
        tool_object = context.native_objects[tool_name]
        return str(tool_object.invoke({"payload_json": json.dumps(action_input, sort_keys=True)}))


class AgentScopeAdapter(FrameworkAdapter):
    framework_name = "agentscope"
    package_name = "agentscope"

    def build_runtime_context(self, tools: dict[str, UnifiedTool]) -> FrameworkRuntimeContext:
        if not self.is_package_installed():
            return super().build_runtime_context(tools)

        try:
            message_module = import_module("agentscope.message")
            tool_module = import_module("agentscope.tool")
            toolkit = tool_module.Toolkit()
            wrappers: dict[str, Any] = {}
            for tool in tools.values():
                wrapper = _build_agentscope_tool_function(tool_module, message_module, tool)
                toolkit.register_tool_function(wrapper)
                wrappers[tool.name] = wrapper

            status = FrameworkAdapterStatus(
                framework=self.framework_name,
                package_name=self.package_name,
                package_installed=True,
                integration_mode="native",
                native_objects=("Toolkit",) + tuple(f"ToolFunction:{name}" for name in wrappers),
            )
            return FrameworkRuntimeContext(
                status=status,
                native_objects={
                    "toolkit": toolkit,
                    "tool_use_block": message_module.ToolUseBlock,
                    "wrappers": wrappers,
                },
                invocation_mode="native",
            )
        except Exception:
            return super().build_runtime_context(tools)

    def invoke_tool(self, context: FrameworkRuntimeContext, tool_name: str, action_input: dict[str, Any], tools: dict[str, UnifiedTool]) -> str:
        if context.invocation_mode != "native":
            return super().invoke_tool(context, tool_name, action_input, tools)

        async def _invoke() -> str:
            toolkit = context.native_objects["toolkit"]
            ToolUseBlock = context.native_objects["tool_use_block"]
            result_stream = await toolkit.call_tool_function(
                ToolUseBlock(
                    type="tool_use",
                    id=f"{tool_name}-react",
                    name=tool_name,
                    input={"payload_json": json.dumps(action_input, sort_keys=True)},
                )
            )
            chunks: list[str] = []
            async for tool_response in result_stream:
                chunks.extend(_extract_agentscope_text(tool_response))
            return " ".join(part for part in chunks if part).strip()

        return _run_async_blocking(_invoke())


class ReActPlanner:
    def plan(
        self,
        task: str,
        trace: list[ReActStep],
        tool_names: set[str],
    ) -> tuple[str, str, dict[str, Any]]:
        task_lower = task.lower()

        if not trace:
            if "flight" in task_lower and "search_flights" in tool_names:
                return (
                    "I should first gather candidate flights before deciding on a travel plan.",
                    "search_flights",
                    {"destination": "Tokyo", "passengers": 1},
                )
            return (
                "I should inspect the request context before choosing any travel tools.",
                "inspect_request",
                {"task": task},
            )

        actions_taken = {step.action for step in trace}
        if "check_hotels" not in actions_taken and "check_hotels" in tool_names:
            return (
                "I have flight options. Next I need hotel availability for the requested stay.",
                "check_hotels",
                {"city": "Tokyo", "nights": 3},
            )

        if "lookup_local_policy" not in actions_taken and "lookup_local_policy" in tool_names:
            return (
                "I should verify simple local travel policy constraints before issuing the final answer.",
                "lookup_local_policy",
                {"country": "Japan"},
            )

        return (
            "I have enough observations to synthesize a final recommendation.",
            "finish",
            {},
        )


def _search_flights(action_input: dict[str, Any]) -> str:
    destination = action_input.get("destination", "Tokyo")
    passengers = action_input.get("passengers", 1)
    return f"Found 2 flights to {destination} for {passengers} passenger(s): NH105 nonstop, JL62 one-stop."


def _check_hotels(action_input: dict[str, Any]) -> str:
    city = action_input.get("city", "Tokyo")
    nights = action_input.get("nights", 3)
    return f"Hotel Sakura in {city} has availability for {nights} nights at a stable refundable rate."


def _lookup_local_policy(action_input: dict[str, Any]) -> str:
    country = action_input.get("country", "Japan")
    return f"{country} itinerary policy check passed: no extra visa workflow is required for the demo scenario."


def _inspect_request(action_input: dict[str, Any]) -> str:
    task = action_input.get("task", "")
    return f"Task inspected successfully: {task}"


def build_default_tools() -> list[UnifiedTool]:
    return [
        UnifiedTool(
            name="search_flights",
            description="Search candidate flights for the itinerary workload.",
            handler=_search_flights,
        ),
        UnifiedTool(
            name="check_hotels",
            description="Check hotel inventory for the itinerary workload.",
            handler=_check_hotels,
        ),
        UnifiedTool(
            name="lookup_local_policy",
            description="Return a simple travel policy summary.",
            handler=_lookup_local_policy,
        ),
        UnifiedTool(
            name="inspect_request",
            description="Inspect a task when no domain tool applies yet.",
            handler=_inspect_request,
        ),
    ]


def _build_langchain_tool(StructuredTool: Any, tool: UnifiedTool) -> Any:
    def _native_tool(payload_json: str = "{}") -> str:
        action_input = json.loads(payload_json or "{}")
        return tool.invoke(action_input)

    _native_tool.__name__ = tool.name
    _native_tool.__doc__ = (
        f"{tool.description}\n\n"
        "Args:\n"
        "    payload_json (str): JSON-encoded action arguments produced by the unified ReAct planner.\n"
    )
    return StructuredTool.from_function(
        func=_native_tool,
        name=tool.name,
        description=tool.description,
    )


def _build_agentscope_tool_function(tool_module: Any, message_module: Any, tool: UnifiedTool) -> Callable[..., Any]:
    ToolResponse = tool_module.ToolResponse
    TextBlock = message_module.TextBlock

    def _native_tool(payload_json: str = "{}") -> Any:
        """Proxy a unified ReAct tool through AgentScope Toolkit.

        Args:
            payload_json (str):
                JSON-encoded action arguments produced by the unified ReAct planner.
        """

        action_input = json.loads(payload_json or "{}")
        observation = tool.invoke(action_input)
        return ToolResponse(content=[TextBlock(type="text", text=observation)])

    _native_tool.__name__ = tool.name
    _native_tool.__doc__ = (
        f"{tool.description}\n\n"
        "Args:\n"
        "    payload_json (str): JSON-encoded action arguments produced by the unified ReAct planner.\n"
    )
    return _native_tool


def _extract_agentscope_text(tool_response: Any) -> list[str]:
    texts: list[str] = []
    for block in getattr(tool_response, "content", []):
        if isinstance(block, dict):
            text = block.get("text")
        else:
            text = getattr(block, "text", None)
        if text:
            texts.append(str(text))
    return texts


def _run_async_blocking(awaitable: Any) -> str:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(awaitable)

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(awaitable)
    finally:
        loop.close()


class UnifiedReActAgent:
    def __init__(
        self,
        framework: str,
        tools: list[UnifiedTool] | None = None,
        planner: ReActPlanner | None = None,
    ) -> None:
        self.adapter = create_framework_adapter(framework)
        self.tools = {tool.name: tool for tool in (tools or build_default_tools())}
        self.planner = planner or ReActPlanner()

    def run(self, task: str, max_steps: int = 4) -> ReActRunResult:
        runtime_context = self.adapter.build_runtime_context(self.tools)
        status = runtime_context.status
        trace: list[ReActStep] = []
        final_answer = "No answer generated."

        for index in range(1, max_steps + 1):
            thought, action, action_input = self.planner.plan(task, trace, set(self.tools))
            if action == "finish":
                observations = [step.observation for step in trace]
                final_answer = (
                    "ReAct summary: "
                    + " ".join(observations)
                    + " Final recommendation: take the nonstop flight and book Hotel Sakura for 3 nights."
                )
                break

            observation = self.adapter.invoke_tool(runtime_context, action, action_input, self.tools)
            trace.append(
                ReActStep(
                    index=index,
                    thought=thought,
                    action=action,
                    action_input=action_input,
                    observation=observation,
                )
            )
        else:
            final_answer = "ReAct summary incomplete: max step budget reached before finishing."

        return ReActRunResult(
            framework=status.framework,
            reasoning_cycle=status.reasoning_cycle,
            integration_mode=status.integration_mode,
            package_installed=status.package_installed,
            task=task,
            final_answer=final_answer,
            framework_objects=list(status.native_objects),
            trace=trace,
        )


def create_framework_adapter(framework: str) -> FrameworkAdapter:
    normalized = framework.strip().lower()
    if normalized == "langchain":
        return LangChainAdapter()
    if normalized == "agentscope":
        return AgentScopeAdapter()
    raise ValueError(f"Unsupported framework: {framework}")


def run_unified_react_demo(task: str | None = None) -> dict[str, Any]:
    demo_task = task or "Plan a Tokyo trip with a direct flight preference and a 3-night hotel stay."
    results = {}
    for framework in ("langchain", "agentscope"):
        result = UnifiedReActAgent(framework).run(demo_task)
        results[framework] = {
            "framework_status": {
                "framework": result.framework,
                "package_name": create_framework_adapter(framework).package_name,
                "package_installed": result.package_installed,
                "integration_mode": result.integration_mode,
                "native_objects": result.framework_objects,
                "reasoning_cycle": result.reasoning_cycle,
            },
            "run": asdict(result),
        }
    return results
