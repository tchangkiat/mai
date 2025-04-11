import os
import faiss

from typing import Annotated

from langchain_aws import ChatBedrock
from langchain_core.messages import SystemMessage, HumanMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph

# Dependencies for RAG
from langchain_aws import BedrockEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain.text_splitter import CharacterTextSplitter
from langgraph.prebuilt import ToolNode, tools_condition, InjectedStore

import mai.constants as c
from mai.helpers import synthesizer, transcriber
from pyck.helpers.logging import Logging
from pyck.utils.styles import purple


class LLM:
    def __init__(self, rag=False, synth=False):
        self.rag = rag  # If True, use the provided context stored in FAISS
        self.synth = synth  # If True, synthesize the LLM's response

        self.log = Logging.get_instance()

        # Used for setting up clients for Amazon services
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        os.environ["AWS_PROFILE"] = "default"

        model_id = c.MODELS.ANTHROPIC.CLAUDE_3_7_SONNET
        self.llm = ChatBedrock(
            model=model_id,
            region=os.environ["AWS_DEFAULT_REGION"],
            max_tokens=1500,
            model_kwargs={
                "thinking": {"type": "enabled", "budget_tokens": 1024},
            },
        )
        self.log.debug(f"Using LLM: {model_id}")

        self.trimmer = trim_messages(
            max_tokens=65,
            strategy="last",
            token_counter=self.llm,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )

        self.messages = []
        graph = StateGraph(state_schema=MessagesState)
        memory = MemorySaver()

        if self.rag:
            # Store text embeddings in vector store
            embeddings = BedrockEmbeddings(
                model_id=c.MODELS.AMAZON.TITAN_TEXT_EMBEDDING
            )

            loader = CSVLoader("./rag_data/aws-enterprise-support.csv")
            documents_aws_es = loader.load()
            self.log.debug(f"Number of documents: {len(documents_aws_es)}")

            docs = CharacterTextSplitter(
                chunk_size=2000, chunk_overlap=400, separator=","
            ).split_documents(documents_aws_es)

            self.log.debug(f"Number of documents after split and chunking: {len(docs)}")

            embedding_dim = len(embeddings.embed_query("aws"))
            index = faiss.IndexFlatL2(embedding_dim)

            vector_store = FAISS(
                embedding_function=embeddings,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            )

            vector_store.add_documents(documents=docs)

            self.log.debug(
                f"Number of elements in the index: {vector_store.index.ntotal}"
            )

            tools = ToolNode([self.retrieve])

            graph = StateGraph(state_schema=MessagesState)

            graph.add_node(self.query_or_respond)
            graph.add_node(tools)
            graph.add_node(self.generate)

            graph.set_entry_point("query_or_respond")
            graph.add_conditional_edges(
                "query_or_respond",
                tools_condition,
                {END: END, "tools": "tools"},
            )
            graph.add_edge("tools", "generate")
            graph.add_edge("generate", END)

            self.app = graph.compile(checkpointer=memory, store=vector_store)
        else:
            graph.add_edge(START, "model")
            graph.add_node("model", self.call_model)

            self.app = graph.compile(checkpointer=memory)

        if self.synth:
            self.synthesizer = synthesizer.Synthesizer(
                region=os.environ.get("AWS_DEFAULT_REGION", None)
            )

    def prompt(self, user_input):
        result = self._prompt(user_input)
        print(purple("[Mai] " + result + "\n"))

        if self.synth:
            self.synthesizer.synthesize(result)

    def _prompt(self, input):
        trimmed_messages = self.trimmer.invoke(self.messages)
        output = self.app.invoke(
            {"messages": trimmed_messages + [HumanMessage(input)]},
            config={"configurable": {"thread_id": "1"}},
        )

        return output["messages"][-1].content

    # Define the function that calls the model
    def call_model(self, state: MessagesState):
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are Mai, an AI assistant for question-answering tasks. Use at maximum five sentences to answer the question.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        prompt = self.prompt_template.invoke(state)
        response = self.llm.invoke(prompt)
        return {"messages": response}

    # RAG - Retrieval function
    @tool(response_format="content_and_artifact")
    def retrieve(
        query: str,
        store: Annotated[FAISS, InjectedStore],
    ):
        """Retrieve information related to a query."""
        print("Retrieving from vector store ...")
        retrieved_docs = store.similarity_search(query, k=2)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs

    # RAG - Generate an AIMessage that may include a tool-call to be sent.
    def query_or_respond(self, state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = self.llm.bind_tools([self.retrieve])
        response = llm_with_tools.invoke(state["messages"])
        # MessagesState appends messages to state instead of overwriting
        return {"messages": [response]}

    # RAG - Generate a response using the retrieved content.
    def generate(self, state: MessagesState):
        """Generate answer."""
        # Get generated ToolMessages
        recent_tool_messages = []
        for message in reversed(state["messages"]):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        tool_messages = recent_tool_messages[::-1]

        # Format into prompt
        docs_content = "\n\n".join(doc.content for doc in tool_messages)
        system_message_content = (
            "You are Mai, an AI assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use five sentences maximum and keep the "
            "answer concise."
            "\n\n"
            f"{docs_content}"
        )
        conversation_messages = [
            message
            for message in state["messages"]
            if message.type in ("human", "system")
            or (message.type == "ai" and not message.tool_calls)
        ]
        prompt = [SystemMessage(system_message_content)] + conversation_messages

        response = self.llm.invoke(prompt)
        return {"messages": [response]}

    def listen(self):
        # Initiate the Transcriber and pass in the function to call back (i.e. to prompt the LLM)
        transcriber.Transcriber(callback_func=self.prompt)
