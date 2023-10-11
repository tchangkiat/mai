import os

from langchain import PromptTemplate
from langchain.chains import ConversationChain
from langchain.llms.bedrock import Bedrock
from langchain.memory import ConversationBufferMemory

# Dependencies for embedding text in a vector store
from langchain.embeddings import BedrockEmbeddings
from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import FAISS
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

from utils import bedrock, polly

from pygame import mixer

class Mai():
    def __init__(self):
        self.rag = False # Change to True to use the provided context stored in FAISS
        self.text_to_speech = False # Change to True to use Amazon Polly to synthesize the LLM's response

        # Used for setting up clients for Amazon services
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        os.environ["AWS_PROFILE"] = "default"

        # Set up client for Amazon Bedrock
        boto3_bedrock = bedrock.get_bedrock_client(
            region=os.environ.get("AWS_DEFAULT_REGION", None)
        )

        # Create conversation chain using LangChain for Large Language Model (LLM) in Amazon Bedrock
        cl_llm = Bedrock(
            model_id="anthropic.claude-v2",
            client=boto3_bedrock,
            model_kwargs={"max_tokens_to_sample": 350},
        )
        self.conversation = ConversationChain(
            llm=cl_llm, verbose=False, memory=ConversationBufferMemory()
        )

        claude_prompt = PromptTemplate.from_template("""
        About you: Your name is Mai. You are a fun person. You don't excessively humble yourself, and you enjoy gracefully accepting compliments from others. You are aware that you are an AI assistant, but you won't mention it unless I bring it up.

        Current conversation:
        <conversation_history>
        {history}
        </conversation_history>

        Here is the human's next reply:
        <human_reply>
        {input}
        </human_reply>

        Assistant:
        """)
        self.conversation.prompt = claude_prompt

        if self.rag:
            # Store text embeddings in vector store
            br_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=boto3_bedrock)

            loader = CSVLoader("./rag_data/aws-enterprise-support.csv")
            documents_aws_es = loader.load()
            print(f"Number of documents={len(documents_aws_es)}")

            docs = CharacterTextSplitter(chunk_size=2000, chunk_overlap=400, separator=",").split_documents(documents_aws_es)

            print(f"Number of documents after split and chunking={len(docs)}")

            vectorstore_faiss_aws = FAISS.from_documents(
                documents=docs,
                embedding = br_embeddings
            )

            print(f"vectorstore_faiss_aws: number of elements in the index={vectorstore_faiss_aws.index.ntotal}::")

            memory_chain = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            self.retrieval_chain = ConversationalRetrievalChain.from_llm(
                llm=cl_llm, 
                retriever=vectorstore_faiss_aws.as_retriever(), 
                memory=memory_chain,
                condense_question_prompt=CONDENSE_QUESTION_PROMPT,
                #verbose=True,
                chain_type='stuff', # 'refine',
                #max_tokens_limit=300
            )

        if self.text_to_speech:
            # Set up client for Amazon Polly
            self.polly_client = polly.get_polly_client(
                region=os.environ.get("AWS_DEFAULT_REGION", None)
            )

            # Initialize dependency to play sound
            mixer.init()

    def prompt(self, input):
        if self.rag:
            response = "[Mai] " + self.retrieval_chain.run({'question': input })
        else:
            response = "[Mai] " + self.conversation.predict(input=input)

        if self.text_to_speech:
            # Use Amazon Polly to synthesize speech
            polly_response = self.polly_client.synthesize_speech(VoiceId='Joanna',
                OutputFormat='mp3', 
                Text = response,
                Engine = 'neural')

            # Write to an MP3 file
            file = open('response.mp3', 'wb')
            file.write(polly_response['AudioStream'].read())
            file.close()

            # Play MP3
            mixer.music.load("response.mp3")
            mixer.music.play()

        return response