# Python Built-Ins:
import os
from typing import Optional

# External Dependencies:
import boto3
from botocore.config import Config

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from pygame import mixer
import keyboard
import pyttsx4

from mai import constants as c
from mai.helpers import styles


class Synthesizer:
    def __init__(
        self,
        type: Optional[str] = c.Synthesizer.Amazon_Polly,
        region: Optional[str] = None,
    ):
        self.type = type
        if type == c.Synthesizer.Amazon_Polly:
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

            self.engine = session.client(
                service_name="polly", config=retry_config, **client_kwargs
            )
            # print(polly_client._endpoint)

            mixer.init()
        else:
            self.engine = pyttsx4.init()
            self.engine.setProperty(
                "voice", "com.apple.speech.synthesis.voice.samantha"
            )
            self.engine.setProperty("rate", 175)

    def synthesize(self, result):
        if self.type == c.Synthesizer.Amazon_Polly:
            # Use Amazon Polly to synthesize speech
            polly_response = self.engine.synthesize_speech(
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
                styles.grey("Press 'esc' to stop playing the synthesized response.")
                + "\n"
            )
            keyboard.on_press_key("esc", lambda _: mixer.music.stop())
        else:
            self.engine.say(result)
            self.engine.runAndWait()
            keyboard.on_press_key("esc", lambda _: self.engine.stop())
