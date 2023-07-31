import re
from pathlib import Path
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechConfig

from src import Utils


class Mp3Creator:

    speech_config: SpeechConfig

    def __init__(self):
        """
        There are demos of the voices in the 'Speech Studio' where your service is
        Maybe here: https://speech.microsoft.com/portal/291e8d14e04944b7a4a4289dab276a45/voicegallery
        """
        speech_key = Utils.loadFileAsString(Path("./azureApiKey"), f"Failed to load ./azureApiKey").strip()
        service_region = "germanywestcentral"
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_language = "zh-CN"
        speech_config.speech_synthesis_voice_name = "zh-CN-XiaoxiaoNeural"
        self.speech_config = speech_config

    def create(self, sentence: str, outputDir: Path):
        mp3Path = outputDir.joinpath(Mp3Creator.createFileName(sentence))
        if mp3Path.exists():
            print(f"Skipping, because file already exists: {mp3Path}")
            return

        audio_output_config = speechsdk.audio.AudioOutputConfig(filename=str(mp3Path))
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_output_config)
        result = speech_synthesizer.speak_text_async(sentence).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            with open(str(mp3Path), "wb") as audio:
                audio.write(result.audio_data)
                print(f"{sentence} written to {mp3Path}")

        elif result.reason == speechsdk.ResultReason.Canceled:
            if mp3Path.exists():
                mp3Path.unlink()
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
            exit(1)

    @staticmethod
    def createFileName(sentence: str):
        return re.sub(r'[^\u4e00-\u9fff]', '', sentence) + ".mp3"
