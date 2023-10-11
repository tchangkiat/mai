import os

from langchain import PromptTemplate
from langchain.chains import ConversationChain
from langchain.llms.bedrock import Bedrock
from langchain.memory import ConversationBufferMemory

from utils import bedrock, polly

from pygame import mixer

class Mai():
    def __init__(self):
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

        # Set up client for Amazon Polly
        self.polly_client = polly.get_polly_client(
            region=os.environ.get("AWS_DEFAULT_REGION", None)
        )

        # Initialize dependency to play sound
        mixer.init()

    def prompt(self, input):
        return "[Mai] " + self.conversation.predict(input=input)

    def synthesize(self, text):
        # Use Amazon Polly to synthesize speech
        response = self.polly_client.synthesize_speech(VoiceId='Joanna',
            OutputFormat='mp3', 
            Text = text,
            Engine = 'neural')

        # Write to an MP3 file
        file = open('response.mp3', 'wb')
        file.write(response['AudioStream'].read())
        file.close()

        # Play MP3
        mixer.music.load("response.mp3")
        mixer.music.play()