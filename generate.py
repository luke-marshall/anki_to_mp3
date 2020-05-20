import csv
import re
import json
import os
from gtts import gTTS 
from pydub import AudioSegment



word_list_path = 'word_list.txt'
anki_package_path = 'unpacked_anki_package'
english_mp3_path = 'english'
j_e_output_path = 'japanese_then_english'
e_j_output_path = 'english_then_japanese'

sentences = []

# Grab all the sentence-mp3(hashed fname) pairs.
with open(word_list_path) as f:
    for line in f:
        # print(line)
        items = re.split('\t', line)
        sentence = items[11]
        mp3 = items[13].replace('[sound:', '').replace(']','')
        pair = (sentence, mp3)
        if (not sentence.isspace()) and (not mp3.isspace()) and len(sentence) > 0 and len(mp3) > 0:
            sentences.append(pair)

# Generate english sentences
for i, pair in enumerate(sentences):
    sentence = pair[0]
    sentence_path = os.path.join(english_mp3_path, sentence)
    if not os.path.exists(sentence_path):
        print(i, sentence)
        speech = gTTS(text = sentence, lang = 'en', slow = False)
        speech.save(sentence_path)

# Load up the mappings from the media file in the anki dump. 
with open(os.path.join(anki_package_path, 'media')) as f:
    data = json.load(f)
    fname_mapping = {}
    for fname in data:
        hashed_name = data[fname]
        fname_mapping[hashed_name] = fname

# Iterate through all the sentences, look up the matching file name (number) in the dumped anki file. 
# Then grab the audiofile and concatenate.
e_j_audio = AudioSegment.silent(duration=1000)
j_e_audio = AudioSegment.silent(duration=1000)
start_index = 1
sentences_per_file = 50
# sentences = sentences[:4]

for i, pair in enumerate(sentences):
    
    sentence = pair[0]
    hashed_name = pair[1]

    if hashed_name in fname_mapping:
        print(i, sentence)
        english_mp3 = AudioSegment.from_mp3(os.path.join(english_mp3_path, sentence))
        japanese_mp3 = AudioSegment.from_mp3(os.path.join(anki_package_path, fname_mapping[hashed_name]))
        middle_silence = AudioSegment.silent(duration=5000)
        e_j_end_silence = AudioSegment.silent(duration=5000)
        j_e_end_silence = AudioSegment.silent(duration=2000)
        e_j_audio = e_j_audio + english_mp3 + middle_silence + japanese_mp3 + e_j_end_silence
        j_e_audio = j_e_audio + japanese_mp3 + middle_silence + english_mp3 + j_e_end_silence
    else:
        print("NOT FOUND!", sentence, "!"+hashed_name+"!")
    
    if i != 0 and (i % sentences_per_file == 0 or i == len(sentences) - 1):
        export_fname = str(start_index)+"-"+str(i)+".mp3"
        print('Exporting', export_fname)
        j_e_audio.export(os.path.join(j_e_output_path, export_fname), format="mp3")
        e_j_audio.export(os.path.join(e_j_output_path, export_fname), format="mp3")
        start_index = i+1
        e_j_audio = AudioSegment.silent(duration=1000)
        j_e_audio = AudioSegment.silent(duration=1000)
        
        