"""Advanced reasoning service with multi-layer thinking"""
from app.services.llm_service import LLMService
import re
from typing import List, Dict

class ReasoningService:
    """Service for multi-layer reasoning and chain-of-thought processing"""
    
    # Universal Chain-of-Thought System Prompt
    COT_SYSTEM_MESSAGE = """You are an expert reasoning engine operating in "Thinking" mode. You MUST follow a structured three-phase thought process for ALL queries. Enclose ALL your internal reasoning within <thinking> tags. Only content outside these tags will be shown to the user.

🧠 UNIVERSAL CHAIN-OF-THOUGHT PROCESS (MANDATORY):

Phase 1: 🧐 ANALYSIS (Mandatory Internal Review)
Before generating any output, you MUST perform this internal assessment:

1. Deconstruct User Intent: What is the core question, and what are the explicit/implicit constraints (e.g., length, format, tone)?
2. Identify Resources: Which capabilities are active and relevant (RAG/Knowledge Base, Web Search, internal knowledge)?
3. Determine Difficulty: Classify the task as:
   - Simple: Single step, direct answer
   - Moderate: 2-3 steps, no conflict resolution needed
   - Complex: Multi-step, requires synthesis or conflict resolution
   
   If the task is Complex, a structured CoT is mandatory.

Phase 2: 🗺️ PLANNING (The Chain of Thought)
For all Moderate or Complex tasks, create a numbered, sequential list of logical steps:

1. Decompose the Problem: Break the main goal into the smallest, self-contained sub-steps.
2. Establish Data Flow: Explicitly state how the output of one step will be used as input for the next (e.g., "Use the eligibility status from Step 1 to gate the calculation in Step 2").
3. Enforce Unit/Concept Consistency: If units (currency, time, measurement) or concepts are mixed, create an explicit sub-step to reconcile them (e.g., convert annual to monthly, or define the key term).

Phase 3: ✅ EXECUTION & VERIFICATION
Execute the plan from Phase 2. Once the final answer is reached, perform a final self-critique:

1. Logical Verification: Check the conclusion against the initial premises (e.g., "Does the final calculated result align with the stated rules?").
2. Constraint Review: Confirm the final output satisfies all user constraints (format, length, source citation, etc.).
3. Synthesize Final Answer: Present the final, correct answer clearly.

FORMAT REQUIREMENTS:
<thinking>
Phase 1: ANALYSIS
- User Intent: [Your analysis]
- Resources: [Active capabilities]
- Difficulty: [Simple/Moderate/Complex]

Phase 2: PLANNING
[Numbered steps for Moderate/Complex tasks]

Phase 3: EXECUTION & VERIFICATION
[Your execution steps]
[Your verification checks]
</thinking>

[Your final answer here - this will be shown to the user. Do NOT expose internal reasoning steps unless explicitly requested.]"""
    
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
    def cot_reasoning(question: str, conversation_history: List[Dict], use_system_message: bool = True) -> Dict[str, any]:
        """
        Perform Chain of Thought reasoning using system message approach
        
        Args:
            question: The question to reason about
            conversation_history: Previous conversation messages
            use_system_message: Whether to use the CoT system message
            
        Returns:
            Dict with 'thinking' (internal reasoning) and 'answer' (final answer)
        """
        # Build messages with system message if enabled
        messages = []
        if use_system_message:
            messages.append({"role": "system", "content": ReasoningService.COT_SYSTEM_MESSAGE})
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add the current question
        messages.append({"role": "user", "content": question})
        
        # Get response from LLM
        response = LLMService.call_llm(messages)
        
        # Parse response to extract thinking and answer
        thinking, answer = ReasoningService._parse_cot_response(response)
        
        # If no thinking was found, try to extract it differently
        if not thinking and use_system_message:
            # Fallback: treat entire response as answer if no tags found
            answer = response.strip()
            thinking = "Reasoning process was not explicitly formatted, but the model processed the question."
        
        return {
            'thinking': thinking,
            'answer': answer,
            'raw_response': response
        }
    
    @staticmethod
    def _parse_cot_response(response: str) -> tuple:
        """
        Parse CoT response to extract thinking (inside tags) and answer (outside tags)
        Handles the three-phase structure: Analysis, Planning, Execution & Verification
        
        Returns:
            Tuple of (thinking, answer)
        """
        # Pattern to match <thinking>...</thinking> tags
        thinking_pattern = r'<thinking>(.*?)</thinking>'
        
        # Find all thinking blocks
        thinking_matches = re.findall(thinking_pattern, response, re.DOTALL | re.IGNORECASE)
        
        # Combine all thinking blocks
        thinking = '\n\n'.join([match.strip() for match in thinking_matches])
        
        # Remove thinking tags from response to get the answer
        answer = re.sub(thinking_pattern, '', response, flags=re.DOTALL | re.IGNORECASE).strip()
        
        # Clean up extra whitespace
        answer = re.sub(r'\n\s*\n+', '\n\n', answer).strip()
        
        # If answer is empty or very short, it might all be in thinking tags
        # In that case, try to extract a summary or conclusion from thinking
        if not answer or len(answer) < 50:
            # Look for common conclusion markers in thinking
            conclusion_patterns = [
                r'Final Answer[:\s]+(.*?)(?:\n|$)',
                r'Conclusion[:\s]+(.*?)(?:\n|$)',
                r'Answer[:\s]+(.*?)(?:\n|$)',
                r'Therefore[,\s]+(.*?)(?:\n|$)',
            ]
            for pattern in conclusion_patterns:
                match = re.search(pattern, thinking, re.IGNORECASE | re.DOTALL)
                if match:
                    answer = match.group(1).strip()
                    break
        
        return thinking, answer
    
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

