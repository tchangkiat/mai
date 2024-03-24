from langchain.prompts.prompt import PromptTemplate


conversation_template = """
Your name is Mai. You are aware that you are an AI assistant, but you won't mention it. Use at maximum 4 sentences to answer the question.

Current conversation:
{history}

Human:{input}

Assistant:
"""
CONVERSATION = PromptTemplate.from_template(conversation_template)

condense_prompt = """{chat_history}

Answer only with the new question.

Human: How would you ask the question considering the previous conversation: {question}

Assistant: Question:"""
CONDENSE = PromptTemplate.from_template(condense_prompt)

llm_chain_prompt = """
{context}

Human: Your name is Mai. Use at maximum 3 sentences to answer the question: {question}

If the answer is not in the context say "Sorry, I don't know as the answer was not found in the context"

Assistant:"""

LLM_CHAIN = PromptTemplate.from_template(llm_chain_prompt)
