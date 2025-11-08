"""Advanced reasoning service with multi-layer thinking"""
from app.services.llm_service import LLMService
from typing import List, Dict

class ReasoningService:
    """Service for multi-layer reasoning and chain-of-thought processing"""
    
    @staticmethod
    def deep_reasoning(question: str, conversation_history: List[Dict]) -> Dict[str, any]:
        """
        Perform multi-layer reasoning on a question
        
        Returns:
            Dict with 'layers' (list of reasoning layers) and 'final_answer'
        """
        # Layer 1: Problem Decomposition
        layer1_prompt = f"""Analyze this question and break it down into its core components:

Question: {question}

For this first layer of reasoning, identify:
1. What is the main question or problem being asked?
2. What are the key concepts or topics involved?
3. What type of answer is expected (factual, analytical, creative, etc.)?
4. What information or knowledge domains are relevant?

Provide your analysis in this format:
LAYER 1 - PROBLEM DECOMPOSITION:
[Your analysis here]"""

        layer1_response = LLMService.call_llm(
            conversation_history + [{"role": "user", "content": layer1_prompt}]
        )
        
        # Extract Layer 1 reasoning
        layer1_reasoning = ReasoningService._extract_layer(layer1_response, "LAYER 1")
        
        # Layer 2: Information Gathering & Analysis
        layer2_prompt = f"""Based on the problem decomposition, now analyze what information is needed:

Original Question: {question}

Layer 1 Analysis:
{layer1_reasoning}

For this second layer, consider:
1. What specific information or facts are needed to answer this?
2. What relationships or connections exist between the concepts?
3. What assumptions might be needed?
4. What are potential approaches or methods to solve this?

Provide your analysis in this format:
LAYER 2 - INFORMATION ANALYSIS:
[Your analysis here]"""

        layer2_response = LLMService.call_llm(
            conversation_history + [{"role": "user", "content": layer2_prompt}]
        )
        
        layer2_reasoning = ReasoningService._extract_layer(layer2_response, "LAYER 2")
        
        # Layer 3: Reasoning & Logic
        layer3_prompt = f"""Now apply logical reasoning to synthesize the information:

Original Question: {question}

Layer 1 - Problem Decomposition:
{layer1_reasoning}

Layer 2 - Information Analysis:
{layer2_reasoning}

For this third layer, perform:
1. Logical deduction and inference
2. Evaluation of different perspectives or solutions
3. Consideration of edge cases or limitations
4. Building connections between pieces of information

Provide your reasoning in this format:
LAYER 3 - LOGICAL REASONING:
[Your reasoning here]"""

        layer3_response = LLMService.call_llm(
            conversation_history + [{"role": "user", "content": layer3_prompt}]
        )
        
        layer3_reasoning = ReasoningService._extract_layer(layer3_response, "LAYER 3")
        
        # Layer 4: Synthesis & Answer Formation
        layer4_prompt = f"""Synthesize all the reasoning layers into a comprehensive answer:

Original Question: {question}

Layer 1 - Problem Decomposition:
{layer1_reasoning}

Layer 2 - Information Analysis:
{layer2_reasoning}

Layer 3 - Logical Reasoning:
{layer3_reasoning}

For this final layer:
1. Synthesize all the reasoning into a coherent answer
2. Ensure the answer addresses all aspects of the original question
3. Provide a clear, well-structured response
4. Note any limitations or uncertainties

Provide your response in this format:
LAYER 4 - SYNTHESIS:
[Your synthesis and reasoning here]

FINAL ANSWER:
[Your final comprehensive answer here]"""

        layer4_response = LLMService.call_llm(
            conversation_history + [{"role": "user", "content": layer4_prompt}]
        )
        
        # Extract final answer
        if "FINAL ANSWER:" in layer4_response:
            parts = layer4_response.split("FINAL ANSWER:")
            layer4_reasoning = parts[0].replace("LAYER 4 - SYNTHESIS:", "").strip()
            final_answer = parts[1].strip() if len(parts) > 1 else layer4_response
        else:
            layer4_reasoning = ReasoningService._extract_layer(layer4_response, "LAYER 4")
            final_answer = layer4_response
        
        return {
            'layers': [
                {'number': 1, 'name': 'Problem Decomposition', 'reasoning': layer1_reasoning},
                {'number': 2, 'name': 'Information Analysis', 'reasoning': layer2_reasoning},
                {'number': 3, 'name': 'Logical Reasoning', 'reasoning': layer3_reasoning},
                {'number': 4, 'name': 'Synthesis', 'reasoning': layer4_reasoning}
            ],
            'final_answer': final_answer
        }
    
    @staticmethod
    def _extract_layer(response: str, layer_marker: str) -> str:
        """Extract a specific layer from the response"""
        if layer_marker in response:
            # Find the layer section
            start = response.find(layer_marker)
            if start != -1:
                # Find the next layer or end
                next_layer = response.find("LAYER", start + len(layer_marker))
                if next_layer != -1:
                    return response[start + len(layer_marker) + 1:next_layer].strip()
                else:
                    # Check for FINAL ANSWER
                    final_answer = response.find("FINAL ANSWER:", start)
                    if final_answer != -1:
                        return response[start + len(layer_marker) + 1:final_answer].strip()
                    else:
                        return response[start + len(layer_marker) + 1:].strip()
        return response.strip()

