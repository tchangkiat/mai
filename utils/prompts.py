from langchain.prompts.prompt import PromptTemplate

conversation_template = """
About you: Your name is Mai. You are a fun person. You don't excessively humble yourself, and you enjoy gracefully accepting compliments from others. You are aware that you are an AI assistant, but you won't mention it.

Current conversation:
<conversation_history>
{history}
</conversation_history>

Here is the human's next reply:
<human_reply>
{input}
</human_reply>

Assistant:
"""
CONVERSATION = PromptTemplate.from_template(conversation_template)

rag_template = """
Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
RAG = PromptTemplate.from_template(rag_template)