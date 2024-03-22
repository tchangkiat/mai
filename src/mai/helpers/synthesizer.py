# Python Built-Ins:
import os
from typing import Optional

# External Dependencies:
import boto3
from botocore.config import Config

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from pygame import mixer
import keyboard

from mai.helpers import styles


class Synthesizer:
    def __init__(
        self,
        region: Optional[str] = None,
    ):
        if region is None:
            target_region = os.environ.get(
                "AWS_REGION", os.environ.get("AWS_DEFAULT_REGION")
            )
        else:
            target_region = region

        session_kwargs = {"region_name": target_region}
        client_kwargs = {**session_kwargs}

        profile_name = os.environ.get("AWS_PROFILE")
        if profile_name:
            # print(f"  Using profile: {profile_name}")
            session_kwargs["profile_name"] = profile_name

        retry_config = Config(
            region_name=target_region,
            retries={
                "max_attempts": 10,
                "mode": "standard",
            },
        )
        session = boto3.Session(**session_kwargs)

        self.polly_client = session.client(
            service_name="polly", config=retry_config, **client_kwargs
        )
        # print(polly_client._endpoint)

        mixer.init()

    def synthesize(self, result):
        # Use Amazon Polly to synthesize speech
        polly_response = self.polly_client.synthesize_speech(
            VoiceId="Joanna",
            OutputFormat="mp3",
            Text=result,
            Engine="neural",
        )
        # Write to an MP3 file
        file = open("response.mp3", "wb")
        file.write(polly_response["AudioStream"].read())
        file.close()

        # Play response
        mixer.music.load("response.mp3")
        mixer.music.play()
        print(
            styles.grey("Press 'esc' to stop playing the synthesized response.") + "\n"
        )
        keyboard.on_press_key("esc", lambda _: mixer.music.stop())
