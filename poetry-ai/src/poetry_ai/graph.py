import os
from dotenv import load_dotenv
load_dotenv()

from poetry_ai.tool import collaboration_assistance
from poetry_ai.output_format import PoetryOutput
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from poetry_ai.nodes import create_poetry, create_follow_up_question, history_rewriter, rephrase_poetry, is_finished
from poetry_ai.state import State

from langgraph.graph import START, END, StateGraph

def get_agent_graph_builder():
    graph_builder = StateGraph(State)

    graph_builder.add_node("create_poetry", create_poetry)
    graph_builder.add_node("create_follow_up_question", create_follow_up_question)
    graph_builder.add_node("history_rewriter", history_rewriter)
    graph_builder.add_node("rephrase_poetry", rephrase_poetry)

    graph_builder.add_edge(START, "create_poetry")
    graph_builder.add_edge("create_poetry", "create_follow_up_question")
    graph_builder.add_conditional_edges(
        "create_follow_up_question",
        is_finished,
        {
            "history_rewriter": "history_rewriter",
            END: END
        }
    )
    graph_builder.add_edge("history_rewriter", "rephrase_poetry")
    graph_builder.add_edge("rephrase_poetry", "create_follow_up_question")
    return graph_builder

# Prebuilt react agent since of simple hitl structure
_agent = get_agent_graph_builder().compile(checkpointer=InMemorySaver())

def start_chat(user_msg, thread_id):
    thread_config = {"configurable": {"thread_id": thread_id}}
    state = {
        "messages": [HumanMessage(user_msg)],
        "last_poetry" : AIMessage(""),
        "last_criticism" : "",
        "history_rewritten_criticism": "" 
    }
    answer = _agent.invoke(state, thread_config)
    return answer

def resume_chat(user_response, thread_id):
    thread_config = {"configurable": {"thread_id": thread_id}}
    answer = _agent.invoke(
        Command(resume=user_response), thread_config)
    return answer

