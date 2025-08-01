"""Local LLM client for CodeInsight."""
import logging
import subprocess
import platform
import time
import os
import requests
from typing import Dict, List, Optional, Any
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
import ollama
from ..core.config import settings


logger = logging.getLogger(__name__)


def is_ollama_running(host: str = "http://localhost:11434") -> bool:
    """Check if Ollama is running."""
    try:
        response = requests.get(f"{host}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def start_ollama():
    """Start Ollama service based on the platform."""
    system = platform.system()
    
    if is_ollama_running():
        logger.info("Ollama is already running")
        return True
    
    logger.info("Starting Ollama service...")
    
    try:
        if system == "Windows":
            # Try to start Ollama on Windows
            # First check if Ollama is installed
            try:
                # Try to start Ollama in a new window
                subprocess.Popen(["ollama", "serve"], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE,
                               shell=True)
            except FileNotFoundError:
                # If ollama command not found, try common installation paths
                possible_paths = [
                    r"C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe",
                    r"C:\Program Files\Ollama\ollama.exe",
                    r"D:\Ollama\ollama.exe"
                ]
                
                for path in possible_paths:
                    expanded_path = os.path.expandvars(path)
                    if os.path.exists(expanded_path):
                        subprocess.Popen([expanded_path, "serve"],
                                       creationflags=subprocess.CREATE_NEW_CONSOLE)
                        break
                else:
                    logger.error("Ollama executable not found. Please ensure Ollama is installed.")
                    return False
                    
        elif system == "Darwin":  # macOS
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        else:  # Linux
            subprocess.Popen(["ollama", "serve"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        
        # Wait for Ollama to start
        for _ in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if is_ollama_running():
                logger.info("Ollama started successfully")
                return True
        
        logger.error("Ollama failed to start within timeout")
        return False
        
    except Exception as e:
        logger.error(f"Error starting Ollama: {e}")
        return False


class LocalLLMClient(LLM):
    """Client for interacting with local LLMs via Ollama."""
    
    model_name: str = settings.llm_model
    temperature: float = 0.1
    max_tokens: int = 2048
    client: Optional[Any] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure Ollama is running before creating client
        start_ollama()
        self.client = ollama.Client(host=settings.ollama_host)
        
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "ollama"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Ollama model."""
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                }
            )
            return response['response']
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise
    
    def check_model_availability(self) -> bool:
        """Check if the model is available locally."""
        try:
            models = self.client.list()
            return any(model['name'] == self.model_name for model in models['models'])
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    def pull_model(self) -> None:
        """Pull the model if not available locally."""
        try:
            logger.info(f"Pulling model {self.model_name}...")
            self.client.pull(self.model_name)
            logger.info(f"Model {self.model_name} pulled successfully")
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            raise


class LLMManager:
    """Manager for LLM operations."""
    
    def __init__(self):
        self.llm = LocalLLMClient()
        self._ensure_model()
    
    def _ensure_model(self):
        """Ensure the model is available."""
        if not self.llm.check_model_availability():
            logger.info(f"Model {self.llm.model_name} not found locally")
            self.llm.pull_model()
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM."""
        return self.llm(prompt, **kwargs)
    
    def generate_with_context(self, query: str, context: str, **kwargs) -> str:
        """Generate response with context."""
        prompt = f"""You are CodeInsight, an AI-powered codebase assistant. You help developers understand code, 
        find relevant documentation, and solve programming problems with up-to-date information.

Context:
{context}

Question: {query}

Please provide a helpful, accurate, and detailed response:"""
        
        return self.generate(prompt, **kwargs)
