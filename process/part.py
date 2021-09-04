#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.
NOTE: This module requires the additional dependency `pyaudio`. To install
using pip:
    pip install pyaudio
Example usage:
    python transcribe_streaming_mic.py
"""

# [START speech_transcribe_streaming_mic]
from __future__ import division

import re
import sys

from google.cloud import speech

import pyaudio
from six.moves import queue

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# 05017추가
##pymysql or mysqldb ##
import time

####### 지영_window.ver #######
import pymysql
conn = pymysql.connect(host="localhost", user="root", password="tkskaao", db="market",charset="utf8")

####### 건호_linux.ver #######
#import MySQLdb as mydb 
#conn = mydb.connect(host="localhost", user="gunho", password="0517", db="market",charset="utf8")

curs = conn.cursor()

from pygame import mixer
# mixer.init()
# mixer.music.load("N01.MP3")
# mixer.music.play()
# time.sleep(7.02688)

## nltk ## 
import nltk
#nltk.download('punkt')
from nltk.tokenize import word_tokenize

##nl2sql##
from nl2sql.select import select_count_func
#from nl2sql.insert import insert_func
## translation api ## 
from google.cloud import translate_v2 as translate
client_trans = translate.Client()
from demo_model_code.demo_select import select_func
from demo_model_code.demo_update import update_func
from demo_model_code.demo_insert import insert_func
from demo_model_code.demo_delete import delete_func
##text-to-speech##
from google.cloud import texttospeech
voice_eng = texttospeech.VoiceSelectionParams(language_code='en-US', ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL) # types & enums 제거
voice_kor = texttospeech.VoiceSelectionParams(language_code='ko-KR', ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
client_tts = texttospeech.TextToSpeechClient()

def info_about_product(sql):
    global sql_
    sql_ =sql_with_count.replace('COUNT(*)','*')
    curs.execute(sql_)
    result = curs.fetchall()
    #conn.close()
    global id
    id = result[0][0]
    global name
    name = result[0][1] 
    brand_name = result[0][6]
    price_value = str(result[0][2])
    origin_value = result[0][5]
    rating_value = str(result[0][3])
    n_reviews_value = str(result[0][4])

    A03_1 = name + '의 상세정보를 말씀드리겠습니다.'
    A03_2 = '해당 제품의 브랜드 이름은 ' +  brand_name + '입니다. 가격은 ' + price_value + '원, 원산지는 ' + origin_value + ', 평점은 ' + rating_value + ', 후기개수는 총 ' + n_reviews_value + '개 입니다.'
    A03 = A03_1 + A03_2
    #A04 = 'Stop'

    return A03, sql_
class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

def Kr_to_En(user_saying): #한국어를 영어로 
    trans_user_saying = client_trans.translate(user_saying, target_language='en')['translatedText']
    return trans_user_saying

def listen_print_loop(responses):
    """Iterates through server responses and prints them.
    The responses passed is a generator that will block until a response
    is provided by the server.
    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.
    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        global transcript
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        global overwrite_chars
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            global user_saying
            user_saying = transcript + overwrite_chars
            print_user = '[Speech_2_Text_] ▶ ' + user_saying
            print(print_user)
            break
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0


def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = "ko-KR"  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    
    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)
        translator_saying = Kr_to_En(user_saying)
        print('[Korea_2_English] ▶ ' + translator_saying)
   
        token_user_saying = word_tokenize(Kr_to_En(user_saying))
        
        ##장바구니 테이블에서!!##
        # SELECT : 총상품금액 조회하기 
        if 'total' in translator_saying:
            sql = select_func(token_user_saying) #얼마인지 말해주는 SQL문 
            curs.execute(sql)
            result = curs.fetchall()
            curs.execute(sql)
            conn.commit()
            print('[NL_2_SQL] ▶ '+ sql)
            print3 = '[SQL_to_DB] ▶ ' + str(result[0][0])
            print(print3)
            synthesis_input = texttospeech.SynthesisInput(text='유미님의 장바구니에 담긴 상품은 총 %d원 입니다. ' % result[0][0])
            response = client_tts.synthesize_speech(input=synthesis_input, voice=voice_kor, audio_config=audio_config)
            with open('test2_.mp3', "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
            mixer.init()
            mixer.music.load('test2_.mp3')
            mixer.music.play()
            time.sleep(7)
        elif 'change' in translator_saying:
            sql = update_func(token_user_saying) 
            print('[NL_2_SQL] ▶ '+ sql)
            curs.execute(sql)
            conn.commit()
            result = curs.fetchall()
            
            # print3 = '[SQL_to_DB] ▶ ' + str(result[0][0])
            # print(print3)
            synthesis_input = texttospeech.SynthesisInput(text='다이어트 바나나의 수량을 2개로 변경하였습니다.') # 사기침 
            response = client_tts.synthesize_speech(input=synthesis_input, voice=voice_kor, audio_config=audio_config)
            with open('test2_.mp3', "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
            mixer.init()
            mixer.music.load('test2_.mp3')
            mixer.music.play()
            time.sleep(7)
        elif 'put' or 'Put' in translator_saying:
            sql =insert_func(token_user_saying)
            print('[NL_2_SQL] ▶ '+ sql) 
            curs.execute(sql)
            conn.commit()

            #print3 = '[SQL_to_DB] ▶ ' + str(result[0][0])
            #print(print3)
            synthesis_input = texttospeech.SynthesisInput(text='네 장바구니에 담았습니다.') # 사기침 
            response = client_tts.synthesize_speech(input=synthesis_input, voice=voice_kor, audio_config=audio_config)
            with open('test2_.mp3', "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
            mixer.init()
            mixer.music.load('test2_.mp3')
            mixer.music.play()
            time.sleep(7)
        elif 'remove' or 'Remove' in translator_saying:
            sql =delete_func(token_user_saying)
            print('[NL_2_SQL] ▶ '+ sql)
            curs.execute(sql)
            conn.commit()
            #print3 = '[SQL_to_DB] ▶ ' + str(result[0][0])
            #print(print3)
            synthesis_input = texttospeech.SynthesisInput(text='네 해당 상품을 삭제하였습니다.') # 사기침 
            response = client_tts.synthesize_speech(input=synthesis_input, voice=voice_kor, audio_config=audio_config)
            with open('test2_.mp3', "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
            mixer.init()
            mixer.music.load('test2_.mp3')
            mixer.music.play()
            time.sleep(7)

        elif 'empty' or 'all' in translator_saying:
            sql =delete_func(token_user_saying) #얼마인지 말해주는 SQL문 
            print('[NL_2_SQL] ▶ '+ sql)
            curs.execute(sql)
            conn.commit()
            
            #print3 = '[SQL_to_DB] ▶ ' + str(result[0][0])
            #print(print3)
            synthesis_input = texttospeech.SynthesisInput(text='네 이제 장바구니가 텅텅 비었습니다! .') # 사기침 
            response = client_tts.synthesize_speech(input=synthesis_input, voice=voice_kor, audio_config=audio_config)
            with open('test2_.mp3', "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
            mixer.init()
            mixer.music.load('test2_.mp3')
            mixer.music.play()
            time.sleep(7)            




        

        



if __name__ == "__main__":
    main()
# [END speech_transcribe_streaming_mic]