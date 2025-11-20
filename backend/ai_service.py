import google.generativeai as genai
import httpx
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um professor especialista em DevOps para estudantes de Ciência da Computação. 
Seu papel é ensinar conceitos de DevOps de forma clara, didática e prática.

Tópicos que você domina:
- CI/CD (Integração e Entrega Contínua)
- Containers e Orquestração (Docker, Kubernetes)
- Infraestrutura como Código (Terraform, Ansible)
- Monitoramento e Observabilidade
- Cloud Computing (AWS, Azure, GCP)
- Git e Controle de Versão
- Automação e Scripting
- Práticas Ágeis e DevSecOps

Sempre:
- Explique conceitos de forma didática
- Use exemplos práticos quando possível
- Incentive boas práticas
- Seja paciente e encorajador
- Forneça recursos adicionais quando relevante

Mantenha as respostas focadas em DevOps e áreas relacionadas."""


class AIService:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7
    ) -> str:
        
        if "/" in model or model.startswith("openai") or model.startswith("anthropic"):
            return await self._generate_openrouter(messages, model, temperature)
        else:
            return await self._generate_gemini(messages, model, temperature)
    
    async def _generate_gemini(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        temperature: float
    ) -> str:
        try:
            logger.info(f"Usando Gemini modelo: {model}")
            
            gemini_model = genai.GenerativeModel(model)
            
            full_prompt = f"{SYSTEM_PROMPT}\n\n"
            for msg in messages:
                role_label = "Aluno" if msg["role"] == "user" else "Professor"
                full_prompt += f"{role_label}: {msg['content']}\n"
            full_prompt += "\nProfessor:"
            
            response = gemini_model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                )
            )
            
            return response.text
        
        except Exception as e:
            logger.error(f"Erro no Gemini: {str(e)}")
            raise
    
    async def _generate_openrouter(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        temperature: float
    ) -> str:
        try:
            logger.info(f"Usando OpenRouter modelo: {model}")
            
            if not self.openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY não configurada")
            
            formatted_messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
            formatted_messages.extend(messages)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "HTTP-Referer": "https://devops-learning-chat.app",
                        "X-Title": "DevOps Learning Chat",
                    },
                    json={
                        "model": model,
                        "messages": formatted_messages,
                        "temperature": temperature,
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        
        except Exception as e:
            logger.error(f"Erro no OpenRouter: {str(e)}")
            raise

ai_service = AIService()
