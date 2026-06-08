"""
Provider-agnostic Base Agent configuration.
Allows initializing agents with any LangChain ChatModel (e.g. ChatOpenAI, AzureChatOpenAI, ChatAnthropic),
abstracting prompting and invocation to prevent vendor lock-in.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from services.telemetry.logger import telemetry_logger

class BaseAgent(ABC):
    """
    Abstract Base Class for all specialized agents in the league.
    Initialized with a provider-agnostic language model and custom system prompts.
    """

    def __init__(
        self,
        name: str,
        llm: BaseChatModel,
        system_prompt: str,
        temperature: float = 0.0,
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.temperature = temperature
        
        # Build prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("placeholder", "{messages}")
        ])

    def get_chain(self):
        """
        Returns a compiled chain that pipes prompt template to the LLM.
        """
        return self.prompt_template | self.llm

    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent node logic within LangGraph.
        Must be implemented by specialized subclasses.
        Returns state update dictionary.
        """
        pass

    def run_telemetry_start(self, task_id: str, state: Dict[str, Any]) -> float:
        return telemetry_logger.log_agent_start(self.name, task_id, state)

    def run_telemetry_end(
        self, 
        task_id: str, 
        start_time: float, 
        outputs: Dict[str, Any], 
        tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        return telemetry_logger.log_agent_end(self.name, task_id, start_time, outputs, tokens)
