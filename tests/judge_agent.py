from enum import Enum

from pydantic_ai import Agent

from pydantic import BaseModel, Field

from main import agent, run_agent_sync, format_output

import asyncio

class CheckName(str, Enum):
    answer_relevant = "answer_relevant"
    answer_clear = "answer_clear"
    completeness = "completeness"

CHECK_DESCRIPTIONS = {
    CheckName.answer_relevant: "The response directly addresses the user's question",
    CheckName.answer_clear: "The answer is clear and correct",
    CheckName.completeness: "The response is complete and covers all key aspects of the request",
} 

class EvaluationCheck(BaseModel):
    check_name: CheckName = Field(description="The type of evaluation check")
    reasoning: str = Field(description="The reasoning behind the check result")
    check_pass: bool = Field(description="Whether the check passed (True) or failed (False)")
    
class EvaluationChecklist(BaseModel):
    checklist: list[EvaluationCheck] = Field(description="List of all evaluation checks")
    summary: str = Field(description="Evaluation summary")

def generate_checklist_text():
    checklist_items = []
    for check_name in CheckName:
        description = CHECK_DESCRIPTIONS[check_name]
        checklist_items.append(f"- {check_name.value}: {description}")
    return "\n".join(checklist_items)

evaluation_instructions = """
Use this checklist to evaluate the quality of an AI agent’s answer (<ANSWER>) to a user question (<QUESTION>).

For each item, check if the condition is met. 

Checklist:

{generate_checklist_text()}

Output true/false for each check and provide a short explanation for your judgment.
"""

eval_agent = Agent(
    name='eval_agent',
    model='openai:gpt-5-mini',
    instructions=evaluation_instructions,
    output_type=EvaluationChecklist
)

user_prompt_format = """
<INSTRUCTIONS>{instructions}</INSTRUCTIONS>
<QUESTION>{question}</QUESTION>
<ANSWER>{answer}</ANSWER>
""".strip()

def format_prompt(rec):

    answer = format_output(rec.output)
    
    # logs = '\n'.join(json.dumps(l) for l in rec['messages'])
                     
    return user_prompt_format.format(
        instructions=agent._instructions,
        question=rec['question'],
        answer=answer,
    )

def evaluate_record(user_prompt):
    print("evaluate_record")
    result =  asyncio.run(eval_agent.run(user_prompt))
    return user_prompt, result

def main():
    result = run_agent_sync("Crea un repertorio que hable del amor de Dios")

    judge_prompt = user_prompt_format.format(
        instructions=agent._instructions,
        question="Crea un repertorio que hable del amor de Dios",
        answer=result.output
    )

    (_, result) = evaluate_record(judge_prompt)

    print(result.output)
    assert True

if __name__ == "__main__":
    main()