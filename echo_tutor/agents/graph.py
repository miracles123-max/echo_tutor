from langgraph.graph import StateGraph, END
from echo_tutor.agents.reader_agent import DocumentReaderAgent, AgentState
from echo_tutor.agents.tutor_agent import PronunciationTutorAgent

def create_learning_graph():
    """
    Create the LangGraph workflow for the multi-agent system
    """
    # Initialize agents
    reader_agent = DocumentReaderAgent()
    tutor_agent = PronunciationTutorAgent()
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("read_document", reader_agent.process_document)
    workflow.add_node("provide_tutoring", tutor_agent.provide_pronunciation)
    
    # Define edges
    workflow.set_entry_point("read_document")
    workflow.add_edge("read_document", "provide_tutoring")
    workflow.add_edge("provide_tutoring", END)

    
    return workflow.compile()
