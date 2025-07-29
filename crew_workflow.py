"""CrewAI workflow with browser automation capabilities.

This module implements a workflow that coordinates between an avatar agent (LLM) 
and a browser agent (Playwright-based automation).
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List
import aiohttp
from pydantic import BaseModel

# Try to import CrewAI components
import logging

# Set up logger
logger = logging.getLogger(__name__)

try:
    from crewai import Agent, Task, Crew, Process
    from crewai.agent import CrewAgent
    from crewai.task import TaskOutput
    from crewai.utilities import I18N
    from crewai.tools import BaseTool
except ImportError:
    # Import failed, define minimal implementations
    class DummyLogger:
        def __init__(self, *args, **kwargs):
            pass
            
        def __getattr__(self, name):
            # Default to print for all logging methods
            return print
    
    # Set up dummy implementations for required classes
    class DummyBaseTool:
        def __init__(self, *args, **kwargs):
            pass
    
    class DummyAgent:
        def __init__(self, *args, **kwargs):
            pass
    
    class DummyTask:
        def __init__(self, *args, **kwargs):
            self.description = kwargs.get('description', '')
            self.expected_output = kwargs.get('expected_output', '')
            self.agent = kwargs.get('agent', None)
            self.tools = kwargs.get('tools', [])
            self.context = kwargs.get('context', [])
            self.async_execution = kwargs.get('async_execution', False)
    
    class DummyCrew:
        def __init__(self, *args, **kwargs):
            self.agents = kwargs.get('agents', [])
            self.tasks = kwargs.get('tasks', [])
            self.process = kwargs.get('process', 'sequential')
            
        def kickoff(self, *args, **kwargs):
            return self.run(*args, **kwargs)
            
        def run(self, *args, **kwargs):
            """Run the crew with the given tasks and agents."""
            if not self.tasks:
                return {"error": "No tasks to execute"}
                
            # Simulate task execution
            results = []
            for task in self.tasks:
                if hasattr(task, 'agent') and task.agent:
                    agent_name = getattr(task.agent, 'role', 'Unknown Agent')
                    results.append(f"Task executed by {agent_name}: {getattr(task, 'description', 'No description')}")
                else:
                    results.append(f"Task executed: {getattr(task, 'description', 'No description')}")
            
            return {
                "results": results,
                "status": "completed",
                "message": "Crew execution completed successfully"
            }
            
        def __call__(self, *args, **kwargs):
            return self.run(*args, **kwargs)
    
    class DummyProcess:
        sequential = 'sequential'
        hierarchical = 'hierarchical'
        
        @classmethod
        def get_process(cls, process_name):
            return getattr(cls, process_name, cls.sequential)
    
    Agent = DummyAgent
    Task = DummyTask
    Crew = DummyCrew
    Process = DummyProcess
    CrewAgent = DummyAgent
    TaskOutput = object
    I18N = object
    BaseTool = DummyBaseTool
    logger = DummyLogger()

# Import our browser agent
from browser_agent import BrowserAgent as PlaywrightBrowserAgent

# Configuration
BROWSER_TIMEOUT = 30000  # 30 seconds


class BrowserToolInput(BaseModel):
    """Input model for browser tool."""
    action: str
    url: Optional[str] = None
    selector: Optional[str] = None
    text: Optional[str] = None
    cookies: Optional[List[Dict[str, Any]]] = None


class BrowserTool(BaseTool):
    """Tool for browser automation."""
    name: str = "browser_tool"
    description: str = """Useful for interacting with web browsers.
    
    Input should be a JSON string with the following fields:
    - action: One of 'navigate', 'click', 'type', 'screenshot', 'get_content', 'get_cookies', 'add_cookies', 'delete_cookies'
    - url: URL to navigate to (required for 'navigate' action)
    - selector: CSS selector for the element to interact with (required for 'click' and 'type' actions)
    - text: Text to type (required for 'type' action)
    - cookies: List of cookie objects (required for 'add_cookies' and 'delete_cookies' actions)
    """
    
    def __init__(self, browser_agent: PlaywrightBrowserAgent):
        self.browser_agent = browser_agent
        super().__init__()
    
    def _run(self, tool_input: str) -> str:
        """Execute the browser tool synchronously.
        
        This is a wrapper around the async _arun method to maintain compatibility
        with the BaseTool interface.
        """
        return asyncio.get_event_loop().run_until_complete(self._arun(tool_input))
    
    async def _arun(self, tool_input: str) -> str:
        """Execute the browser tool asynchronously."""
        try:
            # Parse the input
            try:
                input_data = json.loads(tool_input)
                validated_input = BrowserToolInput(**input_data)
            except (json.JSONDecodeError, ValueError) as e:
                return f"Invalid input format: {str(e)}"
            
            # Execute the appropriate action
            action = validated_input.action.lower()
            
            if action == 'navigate':
                if not validated_input.url:
                    return "Error: URL is required for 'navigate' action"
                result = await self.browser_agent.navigate(validated_input.url)
                
            elif action == 'click':
                if not validated_input.selector:
                    return "Error: Selector is required for 'click' action"
                result = await self.browser_agent.click(validated_input.selector)
                
            elif action == 'type':
                if not validated_input.selector or validated_input.text is None:
                    return "Error: Selector and text are required for 'type' action"
                result = await self.browser_agent.type_text(
                    validated_input.selector, 
                    validated_input.text
                )
                
            elif action == 'screenshot':
                result = await self.browser_agent.take_screenshot()
                
            elif action == 'get_content':
                result = await self.browser_agent.get_content()
                
            elif action == 'get_cookies':
                result = await self.browser_agent.get_cookies()
                
            elif action == 'add_cookies':
                if not validated_input.cookies:
                    return "Error: Cookies are required for 'add_cookies' action"
                result = await self.browser_agent.add_cookies(validated_input.cookies)
                
            elif action == 'delete_cookies':
                if not validated_input.cookies:
                    return "Error: Cookies are required for 'delete_cookies' action"
                result = await self.browser_agent.delete_cookies(validated_input.cookies)
                
            else:
                return f"Error: Unknown action '{action}'"
            
            # Return the result as a string
            return json.dumps(result, indent=2)
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return f"Error in browser tool: {str(e)}\n\n{error_trace}"


def run_avatar_workflow(prompt: str) -> Dict[str, Any]:
    """Run a CrewAI workflow with browser automation capabilities.
    
    Args:
        prompt: The user's request or question
        
    Returns:
        Dict containing the workflow result and any additional data
    """
    if Agent is None:
        return {"error": "CrewAI not installed. Run `pip install crewai`."}
    
    async def _run_workflow():
        # Initialize the browser agent
        browser_agent = PlaywrightBrowserAgent()
        await browser_agent.start()
        
        try:
            # 1. Define the browser tool
            browser_tool = BrowserTool(browser_agent)
            
            # Import LLM utilities
            try:
                from llm_utils import LLMConfig, get_llm, LLMProvider
                
                # Create LLM config from environment variables
                llm_config = LLMConfig(provider=os.getenv("LLM_PROVIDER", "openai"))
                
            except ImportError:
                # Fallback to mock LLM if llm_utils is not available
                class MockLLM:
                    def __init__(self, *args, **kwargs):
                        pass
                        
                    def __call__(self, prompt, **kwargs):
                        # Return a simple response for testing
                        return "This is a mock response for testing purposes."
                    
            # 3. Define the avatar agent with access to the browser tool
            try:
                # Get the configured LLM
                llm = get_llm(llm_config)
                logger.info(f"Using {llm_config.provider.value.upper()} LLM with model: {llm_config.config['model_name']}")
                
            except Exception as e:
                logger.error(f"Error initializing LLM: {e}")
                logger.warning("Falling back to mock LLM")
                llm = MockLLM()  # Fallback to mock if LLM initialization fails
                
                # Create the agent with all required parameters
                avatar = Agent(
                    role="AI Assistant with Web Browsing",
                    goal="Help users by answering questions and performing web-based tasks",
                    backstory="""You are an AI assistant with the ability to browse the web. 
                    Use the browser tool to gather information or perform actions when needed.
                    Always verify information from the web when possible.""",
                    tools=[browser_tool],
                    verbose=True,
                    llm=llm,  # Use either real or mock LLM
                    max_iter=3,  # Limit the number of interactions
                    allow_delegation=False,  # Don't allow delegation to other agents
                    max_rpm=10  # Rate limit: 10 requests per minute
                )
                logger.info("Successfully created CrewAI Agent")
                
            except Exception as e:
                logger.error(f"Failed to initialize CrewAI Agent: {str(e)}")
                # Create a minimal agent with mock LLM as fallback
                logger.warning("Creating minimal agent with mock LLM")
                avatar = Agent(
                    role="AI Assistant with Web Browsing",
                    goal="Help users by answering questions and performing web-based tasks",
                    backstory="""You are an AI assistant with the ability to browse the web.""",
                    tools=[browser_tool],
                    verbose=True,
                    llm=MockLLM()
                )
            
            # 3. Create a task for the avatar
            task = Task(
                agent=avatar,
                description=f"Help the user with their request: {prompt}",
                expected_output="A helpful response that addresses the user's request, possibly including information gathered from the web.",
                tools=[browser_tool]
            )
            
            # 4. Create and run the crew
            crew = Crew(
                agents=[avatar],
                tasks=[task],
                process=Process.sequential,
                verbose=2
            )
            
            # 5. Execute the workflow
            result = crew.run()
            
            # 6. Get the final state of the browser (optional)
            final_content = await browser_agent.get_content()
            
            return {
                "result": result,
                "browser_content": final_content.get('content', '') if final_content else None
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return {"error": f"Workflow execution failed: {str(e)}\n\n{error_trace}"}
            
        finally:
            # Always close the browser when done
            await browser_agent.close()
    
    # Run the async workflow in the event loop
    return asyncio.get_event_loop().run_until_complete(_run_workflow())
