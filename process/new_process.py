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
mixer.init()
mixer.music.load("N01.MP3")
mixer.music.play()
time.sleep(7.02688)

## nltk ## 
import nltk
#nltk.download('punkt')
from nltk.tokenize import word_tokenize

##nl2sql##
from nl2sql.select import select_count_func
from nl2sql.insert import insert_func
## translation api ## 
from google.cloud import translate_v2 as translate
client_trans = translate.Client()

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
def select_new(sql_with_count):
    delete_star = sql_with_count.replace('COUNT(*)','*')
    return delete_star

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
    while(True):
    
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            responses = client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.
            listen_print_loop(responses)
        ##리얼 코드 시작###
        global sql_with_count
        print1 = '[Korea_2_English] ▶ ' + Kr_to_En(user_saying)
        print(print1)
        token_user_saying = word_tokenize(Kr_to_En(user_saying))
        sql_with_count = select_count_func(token_user_saying)
        print2 = '[NL_2_SQL] ▶ '+sql_with_count
        
        print2_not_all = '[NL_2_SQL] ▶ ' + select_new(sql_with_count)
        print(print2) 
        print(print2_not_all)
        #print(sql_with_count)
        if  sql_with_count == 'error':
            print('error')
            mixer.music.load('N19.mp3')
            mixer.music.play()
            time.sleep(3.08064)
            continue
        else:            
            sql_with_count = select_count_func(token_user_saying)
            curs.execute(sql_with_count)
            result = curs.fetchall()
            
            select_num = result[0][0]
            if ('ORDER' in sql_with_count):
                select_num = 1
                print('[SQL_2_DB] ▶ ' + str(select_num) )
            else:    
                print3 = '[SQL_2_DB] ▶ ' + str(select_num)
                print(print3)         
            
            if(select_num != 0):
                synthesis_input = texttospeech.SynthesisInput(text='조건에 맞는 %d개의 상품이 조회되었습니다.' % select_num)
                response = client_tts.synthesize_speech(input=synthesis_input, voice=voice_kor, audio_config=audio_config)                
                if(( select_num != 1) and ('ORDER' not in sql_with_count)):
                    
                        
                    #추천 
                    import random
                    li_random = [1,2,3]
                    rand = random.choice(li_random)
                    synthesis_input = texttospeech.SynthesisInput(text='조건에 맞는 %d개의 상품중에서 ' % select_num)
                    response = client_tts.synthesize_speech(input=synthesis_input, voice=voice_kor, audio_config=audio_config)
                    with open('test2_.mp3', "wb") as out:
                        # Write the response to the output file.
                        out.write(response.audio_content)
                       # print('Audio content written to file')

                    #from playsound import playsound
                    #playsound("test2_.mp3")
                    mixer.music.load('test2_.mp3')
                    mixer.music.play()
                    time.sleep(2.4)
                    if (rand == 1):
                        #playsound('N04.mp3')
                        mixer.music.load('N04.mp3')
                        mixer.music.play()
                        time.sleep(2.46848)
                    elif (rand == 2):
                        #playsound('N05.mp3')
                        mixer.music.load('N05.mp3')
                        mixer.music.play()
                        time.sleep(3.034560)
                    elif (rand == 3):
                        #playsound('N06.mp3')
                        mixer.music.load('N06.mp3')
                        mixer.music.play()
                        time.sleep(3.14976)
                    
                    #★input
                    with MicrophoneStream(RATE, CHUNK) as stream:
                        audio_generator = stream.generator()
                        requests = (
                            speech.StreamingRecognizeRequest(audio_content=content)
                            for content in audio_generator
                        )
                   

                        responses = client.streaming_recognize(streaming_config, requests)
                        # Now, put the transcription responses to use.
                        listen_print_loop(responses)

                    if 'yeah' or 'yes' in Kr_to_En(user_saying) :
                        if rand == 1:
                            sql_with_count = sql_with_count + ' ORDER BY price ASC'
                        elif rand == 2 :
                            sql_with_count = sql_with_count + ' ORDER BY rating DESC'
                        else: 
                            sql_with_count = sql_with_count + ' ORDER BY number_of_reviews DESC'

                #else:
                #   #상품1개 -> 상세정보를 확인하시겠습니까?
                mixer.music.load('N07.mp3')
                mixer.music.play()
                time.sleep(4.192)
                # ★input
                with MicrophoneStream(RATE, CHUNK) as stream:
                    audio_generator = stream.generator()
                    requests = (
                        speech.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator
                    )

                    responses = client.streaming_recognize(streaming_config, requests)

                    # Now, put the transcription responses to use.
                    listen_print_loop(responses)
                                  

                if 'Yes' or 'Yeah' in Kr_to_En(user_saying)  :
                    
                    text_spe, sql_with_count = info_about_product(sql_with_count)
                    print( '[NL_2_SQL] ▶ '+sql_with_count )
                    print2_not_all = '[NL_2_SQL] ▶ ' + select_new(sql_with_count)
                    print(print2_not_all)
                    #print(sql_with_count)
                   
                    print('[Test_2_Speech] '+ text_spe)
                    #print(sql_with_count)
                    synthesis_input = texttospeech.SynthesisInput(text=text_spe)
                    response = client_tts.synthesize_speech(input=synthesis_input, voice=voice_kor, audio_config=audio_config)

                    #상세정보 output
                    with open('test_1.mp3', "wb") as out:
                        # Write the response to the output file.
                        out.write(response.audio_content)
                        #print('Audio content written to file')
                    mixer.init()
                    mixer.music.load('test_1.mp3')
                    mixer.music.play()
                    time.sleep(16.5) # 고쳐야함

                    mixer.music.load('N08.mp3')
                    mixer.music.play()
                    time.sleep(2.07680)

                    # ★input
                    with MicrophoneStream(RATE, CHUNK) as stream:
                        audio_generator = stream.generator()
                        requests = (
                            speech.StreamingRecognizeRequest(audio_content=content)
                            for content in audio_generator
                        )

                        responses = client.streaming_recognize(streaming_config, requests)

                        # Now, put the transcription responses to use.
                        listen_print_loop(responses)
                        #print(user_saying)  

                    if 'Yes' or 'Yeah' in Kr_to_En(user_saying):
                        print(Kr_to_En(user_saying))
                        token_user_saying = word_tokenize(Kr_to_En(user_saying))
                        sql1, sql2, quantity_val = insert_func(token_user_saying, id)
                        print('[NL_2_SQL] ▶ ' + sql1)
                        print('[NL_2_SQL] ▶ ' + sql2)
                        curs.execute(sql1)
                        conn.commit()
                        curs.execute(sql2)
                        conn.commit()
                        synthesis_input = texttospeech.SynthesisInput(text='네 선택하신 %s %d개가 담겼습니다.' %(name,int(quantity_val)))
                        response = client_tts.synthesize_speech(input=synthesis_input, voice=voice_kor, audio_config=audio_config)
                        with open('A07.mp3', "wb") as out:
                            # Write the response to the output file.
                            out.write(response.audio_content)
                            #print('Audio content written to file')
                        mixer.music.load('A07.mp3')
                        mixer.music.play()
                        time.sleep(4)
                        mixer.music.load('N10.mp3')
                        mixer.music.play()
                        time.sleep(2.26112)
                        # ★input
                        with MicrophoneStream(RATE, CHUNK) as stream:
                            audio_generator = stream.generator()
                            requests = (
                                speech.StreamingRecognizeRequest(audio_content=content)
                                for content in audio_generator
                            )

                            responses = client.streaming_recognize(streaming_config, requests)

                            # Now, put the transcription responses to use.
                            listen_print_loop(responses)
                            #print(user_saying)
                            print7 = Kr_to_En(user_saying)
                            #print(print7)
                            
                        
                            if 'no' == print7:
                                #print('no했을때')
                                mixer.music.load('N11.mp3')
                                mixer.music.play()
                                time.sleep(1.7)
                                
                            else:                        
                                #print('yes했을때')
                                mixer.music.load("N02.MP3") #네라고 하면 -> 어떤 상품을 주문하시겠어요 
                                mixer.music.play()
                                time.sleep(2.03)
                                continue

                        


            else: 
                mixer.music.load('N10.mp3')
                mixer.music.play()
                time.sleep(5.34176) 
 

        print("쇼핑을 종료합니다.")
        break
                


        



if __name__ == "__main__":
    main()
# [END speech_transcribe_streaming_mic]