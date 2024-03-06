import os

from langchain.chains import ConversationChain
from langchain.llms.bedrock import Bedrock
from langchain.memory import ConversationBufferMemory

# Dependencies for embedding text in a vector store
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage

from utils import bedrock, polly, prompts

from pygame import mixer


class Mai:
    def __init__(self):
        self.rag = False  # Change to True to use the provided context stored in FAISS
        self.text_to_speech = (
            False  # Change to True to use Amazon Polly to synthesize the LLM's response
        )

        # Used for setting up clients for Amazon services
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        os.environ["AWS_PROFILE"] = "default"

        # Set up client for Amazon Bedrock
        boto3_bedrock = bedrock.get_bedrock_client(
            region=os.environ.get("AWS_DEFAULT_REGION", None)
        )

        # Selecting a large language model (LLM)
        cl_llm = Bedrock(
            model_id="anthropic.claude-v2:1",
            client=boto3_bedrock,
            model_kwargs={"max_tokens_to_sample": 500},
        )

        if self.rag:
            # Store text embeddings in vector store
            br_embeddings = BedrockEmbeddings(
                model_id="amazon.titan-embed-text-v1", client=boto3_bedrock
            )

            loader = CSVLoader("./rag_data/aws-enterprise-support.csv")
            documents_aws_es = loader.load()
            print(f"Number of documents={len(documents_aws_es)}")

            docs = CharacterTextSplitter(
                chunk_size=2000, chunk_overlap=400, separator=","
            ).split_documents(documents_aws_es)

            print(f"Number of documents after split and chunking={len(docs)}")

            vectorstore_faiss_aws = FAISS.from_documents(
                documents=docs, embedding=br_embeddings
            )

            print(
                f"vectorstore_faiss_aws: number of elements in the index={vectorstore_faiss_aws.index.ntotal}::"
            )

            # We are also providing a different chat history retriever which outputs the history as a Claude chat (ie including the \n\n)
            _ROLE_MAP = {"human": "\n\nHuman: ", "ai": "\n\nAssistant: "}

            def _get_chat_history(chat_history):
                buffer = ""
                for dialogue_turn in chat_history:
                    if isinstance(dialogue_turn, BaseMessage):
                        role_prefix = _ROLE_MAP.get(
                            dialogue_turn.type, f"{dialogue_turn.type}: "
                        )
                        buffer += f"\n{role_prefix}{dialogue_turn.content}"
                    elif isinstance(dialogue_turn, tuple):
                        human = "\n\nHuman: " + dialogue_turn[0]
                        ai = "\n\nAssistant: " + dialogue_turn[1]
                        buffer += "\n" + "\n".join([human, ai])
                    else:
                        raise ValueError(
                            f"Unsupported chat history format: {type(dialogue_turn)}."
                            f" Full chat history: {chat_history} "
                        )
                return buffer

            memory_chain = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )
            self.retrieval_chain = ConversationalRetrievalChain.from_llm(
                llm=cl_llm,
                retriever=vectorstore_faiss_aws.as_retriever(),
                # retriever=vectorstore_faiss_aws.as_retriever(search_type='similarity', search_kwargs={"k": 8}),
                memory=memory_chain,
                get_chat_history=_get_chat_history,
                # verbose=True,
                condense_question_prompt=prompts.CONDENSE_PROMPT,
                chain_type="stuff",  # 'refine',
                # max_tokens_limit=300
            )

            # the LLMChain prompt to get the answer. the ConversationalRetrievalChange does not expose this parameter in the constructor
            self.retrieval_chain.combine_docs_chain.llm_chain.prompt = (
                prompts.LLM_CHAIN_PROMPT
            )
        else:
            # Create conversation chain using LangChain for Large Language Model (LLM) in Amazon Bedrock
            self.conversation = ConversationChain(
                llm=cl_llm, verbose=False, memory=ConversationBufferMemory()
            )

            self.conversation.prompt = prompts.CONVERSATION

        if self.text_to_speech:
            # Set up client for Amazon Polly
            self.polly_client = polly.get_polly_client(
                region=os.environ.get("AWS_DEFAULT_REGION", None)
            )

            # Initialize dependency to play sound
            mixer.init()

    def prompt(self, input):
        if self.rag:
            response = "[Mai] " + self.retrieval_chain.run({"question": input})
        else:
            response = "[Mai] " + self.conversation.predict(input=input)

        if self.text_to_speech:
            # Use Amazon Polly to synthesize speech
            polly_response = self.polly_client.synthesize_speech(
                VoiceId="Joanna", OutputFormat="mp3", Text=response, Engine="neural"
            )

            # Write to an MP3 file
            file = open("response.mp3", "wb")
            file.write(polly_response["AudioStream"].read())
            file.close()

            # Play MP3
            mixer.music.load("response.mp3")
            mixer.music.play()

        return response
