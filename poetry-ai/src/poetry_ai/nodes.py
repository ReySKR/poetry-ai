from .state import State
from .prompt import sys_prompts_arch_1 as sys_prompts
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.types import interrupt
from langgraph.graph import END
import os


_llm_type = os.getenv("LLM_TYPE")
_model = os.getenv("MODEL_NAME")
_inference_server = os.getenv("INFERENCE_SERVER")
_temp = os.getenv("TEMPERATURE")

_llm = None
if _llm_type == "OLLAMA":
    from langchain_ollama import ChatOllama
    _llm = ChatOllama(
        model=_model,
        base_url=_inference_server,
        temperature=_temp
        )
elif _llm_type == "VLLM":
    from langchain_openai import ChatOpenAI
    _llm = ChatOpenAI(
    model=_model,
    openai_api_key="EMPTY",
    openai_api_base=_inference_server,
    temperature=_temp
)
else:
    from langchain_google_genai import ChatGoogleGenerativeAI
    _llm = ChatGoogleGenerativeAI(
        model=_model,
    temperature=_temp,
        max_tokens=None,
        timeout=None,
        max_retries=2,
)

def create_poetry(state: State) -> State:
    """
    Creates initial poetry
    """
    sys_prompt = sys_prompts["create_poetry"][0][0]
    message_stack = [
        SystemMessage(sys_prompt),
        HumanMessage(state["messages"][0].content)
    ]
    poetry = _llm.invoke(message_stack)
    state["messages"].append(poetry)
    state["last_poetry"] = poetry
    return state

def create_follow_up_question(state: State) -> State:
    """
    If poetry create a follow_up_question -> interrupt
    """
    sys_prompt = sys_prompts["create_follow_up_question"][0][0]
    message_stack = [
        SystemMessage(sys_prompt),
        HumanMessage(state["last_poetry"].content)
    ]
    follow_up_question = _llm.invoke(message_stack)
    state["messages"].append(follow_up_question)

    raw_criticism = interrupt(follow_up_question.content)

    criticism = HumanMessage(raw_criticism)
    state["messages"].append(criticism)
    state["last_criticism"] = criticism

    return state

def is_finished(state:State) -> str:
    """
    Decides whether a poetry was accepted
    """
    sys_prompt = sys_prompts["is_finished"][0][0]

    history = ""

    for message in state["messages"]:
        history += "\n" + message.pretty_repr()
    
    message_stack = [
        SystemMessage(sys_prompt),
        HumanMessage(history)
    ]

    finished = _llm.invoke(message_stack).content

    # Hard this for invalid outputs
    if "0" in finished:
        return "history_rewriter"
    else:
        return END

def history_rewriter(state: State) -> State:
    """
    Rephrase answer of user that its understandable without history
    """
    sys_prompt = sys_prompts["history_rewriter"][0][0]
    message_stack = [
        SystemMessage(sys_prompt),
        HumanMessage(state["last_criticism"].content)
    ]

    state["last_criticism"] = _llm.invoke(message_stack).content
    return state

def rephrase_poetry(state: State) -> State:
    """
    If poetry wasnt accepted rephrase poetry based on answer of user
    """
    sys_prompt = sys_prompts["rephrase_poetry"][0][0]
    message_stack = [
        SystemMessage(sys_prompt),
        HumanMessage(
            f"""
             # Das Gedicht:
            {state["last_poetry"].content}

            # Die Kritik:
            {state["last_criticism"]}
            """
        )
    ]
    rephrased_poetry = _llm.invoke(message_stack)
    state["messages"].append(rephrased_poetry)
    state["last_poetry"] = rephrased_poetry
    return state

