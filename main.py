#!/usr/bin/env python3

# read local environment variables
import os
from dotenv import load_dotenv
load_dotenv()

# Load usable voices (make into a key-pair for more choices?)
import random
voices = open("voices.txt").read().splitlines()
styles = open("styles.txt").read().splitlines()

import azure.cognitiveservices.speech as speechsdk

# Inititalize Speech Synthesizer
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

# Choose a random voice and style for that voice.
speech_synthesis_voice_name=f"en-US-{random.choice(voices)}Neural"
speech_synthesis_style_name=random.choice(styles)

ssml = """
<speak version='1.0' xml:lang='en-US' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts'>
	<voice name='{}'>
		<mstts:express-as style="{}">
            This is a simple test message.
        </mstts:express-as>
	</voice>
</speak>
""".format(speech_synthesis_voice_name, speech_synthesis_style_name)

# Synthesize the SSML
print("SSML to synthesize: \r\n{}".format(ssml))
print("Voice chosen:", speech_synthesis_voice_name)
print("Style chosen:", speech_synthesis_style_name)
speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()

if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
	print("speech complete")
elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
	cancellation_details = speech_synthesis_result.cancellation_details
	print("Speech synthesis canceled: {}".format(cancellation_details.reason))
	if cancellation_details.reason == speechsdk.CancellationReason.Error:
		if cancellation_details.error_details:
			print("Error details: {}".format(cancellation_details.error_details))