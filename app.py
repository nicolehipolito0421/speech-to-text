import pathlib
import sys
sys.path.append(str(pathlib.Path().absolute()).split("/src")[0] + "/src")
import os
from pyannote.audio import Pipeline
from pydub import AudioSegment
import streamlit as st
import whisper
import numpy as np
import random
import string
import datetime
import tempfile
class Transcribe:
    def __init__(self,source):
        self.source = source
        self.folder ='transcripts'+'-'+str(datetime.datetime.today().date())+'-'+''.join(random.choice(string.digits) for i in range(5))
        os.makedirs(self.folder,exist_ok=True)
    def load_pipeline(self):
        '''
        Load the diarization pipeline
        '''
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token='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', )
    def load_model (self,name):
        self.model = whisper.load_model(name)

    def read(self,k):
        y = np.array(k.get_array_of_samples())
        return np.float32(y) / 32768

    def millisec(self,timeStr):
        spl = timeStr.split(":")
        spl = [i.strip(']') for i in spl]
        return (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2])) * 1000)
    def for_segment(self,file):
        if file.name.split('.')[-1].lower() == "wav":
          audio = AudioSegment.from_wav(file)
        elif file.name.split('.')[-1].lower() == "mp3":
          audio = AudioSegment.from_mp3(file)
        audio = audio.set_frame_rate(16000)
        return audio

    def process(self,files):
      for file in files:
        # file = self.folder_path + path
        audio = self.for_segment(file)
        if self.source == 'nextiva':
          date,agent,code,call_type = file.name.split('-')
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, file.name)
        with open(path, "wb") as f:
            f.write(file.getvalue())
        diarization =  str(self.pipeline(path)).split('\n')

        for l in range(len(diarization)):
          j = diarization[l].split(" ")
          start = int(self.millisec(j[1]))
          end = int(self.millisec(j[4]))
          tr = self.read(audio[start:end])
          result = self.model.transcribe(tr, fp16=False)
          if file.name.split('.')[-1].lower() == "wav":
            f = open(self.folder + f'/{file.name.replace("wav", "txt")}', "a")
          elif file.name.split('.')[-1].lower() == "mp3":
            f = open(self.folder +  f'/{file.name.replace("mp3", "txt")}', "a")

          if l == 0 and self.source == 'nextiva':
            f.write(f'Date:{date[0:3]}-{date[4:6]}-{date[6:]}   Agent:{agent[:8]}   Call Type:{call_type}')
          f.write(f'\n[ {j[1]} -- {j[3]} ] {j[6]} : {result["text"]}')
          f.close()
          del j
          del result
          del tr
        st.success(f'✅ Transcription Successful: {file}')

def app():
    st.title('Speech to text Converter')
    uploaded_file = st.file_uploader("Upload an audio file", type=["mp3",'wav'], accept_multiple_files=True)
    st.info('✨ Supports audio formats - WAV, MP3')
    if uploaded_file is not None:
        col1,col2 = st.columns(2)
        with col1:
            src = st.radio("Please choose the source of the audios", ('myhostednumbers','nextiva'))
        with col2:
            model = st.radio("Please choose the type of model", ('small','medium','large'))

        if st.button("Generate Transcript"):
            run = Transcribe(source=src)
            with st.spinner(f"Generating Transcript... 💫"):
                run.load_pipeline()
                run.load_model(name=model)
                run.process(uploaded_file)
    else:
        st.warning('⚠ Please upload your audio files')

app()