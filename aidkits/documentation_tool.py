from typing import Dict, Optional, List

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import BaseOutputParser, StrOutputParser

from aidkits.storage.opensearch_retriever import OpenSearchRetriever

# Default documentation prompt
DOCUMENTATION_PROMPT = """You are an assistant that helps users with documentation questions.

Use the following documentation to answer the user's query:
{documentation}

User query: {query}

Answer:
"""

class TokensCounter:
    """Simple tokens counter for tracking token usage."""
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
    
    def add_prompt_tokens(self, count: int):
        self.prompt_tokens += count
        self.total_tokens += count
    
    def add_completion_tokens(self, count: int):
        self.completion_tokens += count
        self.total_tokens += count


class AgentLogger:
    """Simple logger for agent actions."""
    def log(self, message: str):
        print(message)


class BaseLLMTool:
    """Base class for LLM-powered tools."""
    def __init__(
        self,
        name: str,
        description: str,
        llm: BaseChatModel,
        prompt: str,
        parser: BaseOutputParser,
        tokens_counter: Optional[TokensCounter] = None,
        agent_logger: Optional[AgentLogger] = None,
    ):
        self.name = name
        self.description = description
        self._llm = llm
        self._prompt = prompt
        self._parser = parser
        self._tokens_counter = tokens_counter
        self._agent_logger = agent_logger
        
        # Create a chain with the LLM and parser
        self._chain = self._llm | self._parser
    
    def _invoke(self, input: Dict) -> str:
        """Invoke the tool with the given input."""
        raise NotImplementedError("Subclasses must implement this method")
    
    def invoke(self, input: Dict) -> str:
        """Invoke the tool with the given input and log the action."""
        if self._agent_logger:
            self._agent_logger.log(f"Invoking tool: {self.name}")
        
        result = self._invoke(input)
        
        if self._agent_logger:
            self._agent_logger.log(f"Tool {self.name} returned result")
        
        return result


class DocumentationTool(BaseLLMTool):
    """Tool for answering questions using documentation stored in OpenSearch."""
    def __init__(
        self,
        llm: BaseChatModel,
        retriever: OpenSearchRetriever,
        collection_name: str,
        top_k: int = 5,
        name: str = "documentation_tool",
        description: str = "Answer question with documentation knowledge",
        prompt: str = DOCUMENTATION_PROMPT,
        parser: BaseOutputParser = StrOutputParser(),
        tokens_counter: Optional[TokensCounter] = None,
        agent_logger: Optional[AgentLogger] = None,
    ):
        super().__init__(name, description, llm, prompt, parser, tokens_counter, agent_logger)
        self._retriever = retriever
        self._top_k = top_k
        self._collection_name = collection_name
    
    def _invoke(self, input: Dict) -> str:
        """Retrieve relevant documentation and answer the question.
        
        Args:
            input: Dictionary containing the question
            
        Returns:
            The answer to the question
        """
        question = input.get("question")
        examples = self._retriever.search(
            question=question,
            collection_name=self._collection_name,
            top_k=self._top_k,
        )
        
        answer = self._chain.invoke(
            {
                "query": question,
                "documentation": "\n\n".join([item.markdown for item in examples]),
            }
        )
        
        print("QUESTION:", question)
        print("ANSWER:", answer)
        
        return answer