from .state import State


def create_poetry(state: State) -> State:
    """
    Creates initial poetry
    """
    pass

def is_finished(state:State) -> str:
    """
    Decides whether a poetry was acceped
    """
    pass

def create_follow_up_question(state: State) -> State:
    """
    If poetry wasnt accepted create a follow_up_question -> interrupt
    """
    pass

def history_rewriter(state: State) -> State:
    """
    Rephrase answer of user that its understandable without history
    """
    pass

def rephrase_poetry(state: State) -> State:
    """
    If poetry wasnt accepted rephrase poetry based on answer of user
    """
    pass
