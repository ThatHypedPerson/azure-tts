#!/usr/bin/env python3

import os
import re

from dotenv import load_dotenv
load_dotenv()

# Load usable voices (make into a key-pair for more choices?)
import random
voices = [f"({voice.lower()})" for voice in open("reference/voices.txt").read().splitlines()]
styles = [f"({style})" for style in open("reference/styles.txt").read().splitlines()]

import azure.cognitiveservices.speech as speechsdk

# Inititalize Speech Synthesizer
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

def playMessage(ssml):
	speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()

	if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
		print("speech complete")
	elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
		cancellation_details = speech_synthesis_result.cancellation_details
		print("Speech synthesis canceled: {}".format(cancellation_details.reason))
		if cancellation_details.reason == speechsdk.CancellationReason.Error:
			if cancellation_details.error_details:
				print("Error details: {}".format(cancellation_details.error_details))
	return

def generateMessage(text):
	ssml = "<speak version='1.0' xml:lang='en-US' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts'>\n"
	split = splitMessage(text)

	for i in range(len(split) - 1):
		if type(split[i]) == str and split[i].lower() in voices and len(split[i+1]) > 1:
			ssml += processVoice(split[i], split[i+1])
	
	ssml += "</speak>"

	playMessage(ssml)

	# return only for debugging
	return ssml

# many parts here provided by ChatGPT, but it works so ¯\_(ツ)_/¯
def splitMessage(text):
	split_text = re.findall(r'\([^)]+\)|\w+', text) # ChatGPT regex
	
	# check if any "voice" is found in the message
	if any(any(voice in word.lower() for voice in voices) for word in split_text):
		# check if the first element is a voice, otherwise move first voice to front
		if split_text[0].lower() not in voices:
			for word in split_text:
				if word.lower() in voices:
					split_text.remove(word)
					split_text.insert(0, word)
					break
	# add random voice to front if none are found
	else:
		split_text.insert(0, random.choice(voices))
	return splitVoice(split_text)

# split list into segments based on "voice"
def splitVoice(split_text):
	temp = []
	new_split = []
	
	for word in split_text:
		if word.lower() in voices:
			if new_split:
				temp = splitStyle(temp)
				new_split.append(temp)
				temp = []
			new_split.append(word)
		else:
			temp.append(word)
	if temp:
		temp = splitStyle(temp)
		new_split.append(temp)
	
	return new_split

# split smaller list into segments based on "style"
def splitStyle(split_text):
	temp = ""
	new_split = []

	# add random style if first element isn't a style
	if split_text[0] not in styles:
		split_text.insert(0, random.choice(styles))

	for word in split_text:
		if word.lower() in styles:
			if new_split:
				new_split.append(temp)
				temp = ""
			new_split.append(word)
		else:
			temp += " " + word # space doesn't matter in audio request
	if temp:
		new_split.append(temp)
	
	return new_split

def processVoice(voice, text):
	voice = voice[1:-1].title()
	voice = f"en-US-{voice}Neural"
	return processStyle(voice, text) 

def processStyle(voice, text):
	ssml = ""
	for i in range(len(text) - 1):
		if text[i] in styles and text[i+1] not in styles:
			# add voice element (weird azure interaction if added before)
			ssml += f"\t<voice name='{voice}'>\n"
			
			# add style element
			ssml += f"\t\t<mstts:express-as style='{text[i][1:-1]}'>\n"
			ssml += f"\t\t\t{text[i+1]}\n"
			ssml += "\t\t</mstts:express-as>\n"

			ssml += "\t</voice>\n"
	return ssml

# debug testing of some cases (testing doesn't exist to me :])
if __name__ == "__main__":
	print(generateMessage("(excited)test(Jenny)(sad)test (Davis) test(Jane)"))
	print(generateMessage("this is a normal message"))