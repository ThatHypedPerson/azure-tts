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

def genSSML(text, ssml = None):
	if ssml is None:
		ssml = "<speak version='1.0' xml:lang='en-US' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts'>"
		if text.find("(") != 0:
			# fill text with a random voice and style
			voice = random.choice(voices)
			style = random.choice(styles)
			text = f"({voice})({style}){text}"
		return ssml + genSSML(text, ssml) + "</speak>"
	
	# check if modifier is in front
	if text.find("(") != 0:
		if text.find(")") == -1: # no modifier
			return text
		else:
			return text[:text.find("(")] + genSSML(text[text.find("("):], ssml)
		
	# check for new voice/style
	modifier = text[1: text.find(")")]
	if modifier in voices:
		return genVoice(text[text.find(")") + 1:], ssml, modifier)
	elif modifier in styles:
		return genStyle(text[text.find(")") + 1:], ssml, modifier)
	else:
		if text.find("(", 1) == -1: # no more possible modifiers
			return text
		return text[:text.find("(", 1)] + genSSML(text[text.find("(", 1):], ssml)

def genVoice(text, ssml, voice): # possibly add current style if voice changes
	return f"<voice name='{f'en-US-{voice}Neural'}'>" + genSSML(text, ssml) + "</voice>"

def genStyle(text, ssml, style):
	return f"<mstts:express-as style='{style}'>" + genSSML(text, ssml) + "</mstts:express-as>"

ssml = genSSML("(Jenny)(angry)This is a simple test message.")

# Synthesize the SSML
print("SSML to synthesize: \r\n{}".format(ssml))
speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()

if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
	print("speech complete")
elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
	cancellation_details = speech_synthesis_result.cancellation_details
	print("Speech synthesis canceled: {}".format(cancellation_details.reason))
	if cancellation_details.reason == speechsdk.CancellationReason.Error:
		if cancellation_details.error_details:
			print("Error details: {}".format(cancellation_details.error_details))