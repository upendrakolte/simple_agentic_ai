import json
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage
from langchain_community.tools import DuckDuckGoSearchRun

# -------------------
# STATE
# -------------------
class AgentState(TypedDict):
    """The state of the agent."""
    messages: List[BaseMessage]

# -------------------
# MODEL
# -------------------
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
).bind_tools([
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for real-time information",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate basic math expressions",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
])

# -------------------
# TOOL IMPLEMENTATIONS
# -------------------
def calculator_tool(expression: str):
    """A simple calculator tool that evaluates a math expression."""
    try:
        # WARNING: eval is not safe for production use.
        return {"result": str(eval(expression))}
    except Exception as e:
        return {"error": str(e)}

# Instantiate the web search tool
web_search_tool = DuckDuckGoSearchRun()

# -------------------
# AGENT LOOP NODES
# -------------------
def agent_node(state: AgentState):
    """LLM decides whether to call a tool or give a final answer."""
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": messages + [response]}

def tool_node(state: AgentState):
    """Execute the tool(s) requested by the agent."""
    messages = state["messages"]
    last_message = messages[-1]

    tool_calls = last_message.additional_kwargs.get("tool_calls", [])
    if not tool_calls:
        # This should not happen in the current graph structure
        return {"messages": messages}

    tool_outputs = []
    for call in tool_calls:
        tool_name = call["function"]["name"]
        args = json.loads(call["function"]["arguments"])
        
        print(f"--- Calling Tool: {tool_name} with args: {args} ---")

        if tool_name == "calculator":
            result = calculator_tool(**args)
        elif tool_name == "web_search":
            # The DuckDuckGo tool expects a string query, not a dict
            result = web_search_tool.run(args["query"])
        else:
            result = {"error": f"Unknown tool {tool_name}"}

        tool_outputs.append(
            ToolMessage(
                content=str(result),
                tool_call_id=call["id"],
                name=tool_name,
            )
        )

    return {"messages": messages + tool_outputs}

# -------------------
# GRAPH DEFINITION
# -------------------
def build_graph():
    """Builds the agent graph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", agent_node)
    workflow.add_node("tool", tool_node)

    workflow.add_conditional_edges(
        "agent",
        lambda state: "tool" if state["messages"][-1].additional_kwargs.get("tool_calls") else END,
        {"tool": "tool", END: END}
    )

    workflow.add_edge("tool", "agent")
    workflow.set_entry_point("agent")

    return workflow.compile()

# -------------------
# MAIN EXECUTION
# -------------------
def main():
    """Main loop to run the agent."""
    graph = build_graph()
    print("--- Agent is ready! Type 'exit' or 'quit' to end the conversation. ---")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("--- Goodbye! ---")
            break

        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_input)]
        }

        try:
            result = graph.invoke(initial_state, config={"recursion_limit": 10})
            final_answer = result["messages"][-1].content
            print(f"Agent: {final_answer}")
        except Exception as e:
            print(f"--- An error occurred: {e} ---")
            print("Please try again.")

if __name__ == "__main__":
    main()
