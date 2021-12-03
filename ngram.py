from music21 import *
from glob import glob
import pdb
from collections import defaultdict
from types import MethodType
import random
from copy import deepcopy
from time import sleep

def load_files(filepath):
    all_notes = []
    for file in glob(filepath):
        abc = converter.parse(file)
        notes = list(abc.flat.notesAndRests)
        all_notes.append(notes)
    return all_notes


def note_hash(note):
    print(note.duration.quarterLength)
    return (note.pitch.nameWithOctave)
    #return (note.pitch.nameWithOctave, note.duration.fullName)

def gen_bigram(filepath):
    """Use C##0 as note to denote end"""
    corpus = load_files(filepath)
    ngram = defaultdict(list)
    for corp in corpus:
        i = 0
        for i in range(len(corp)-1):
            key = corp[i].pitch.nameWithOctave
            key = note_hash(corp[i])
            ngram[key].append(corp[i+1])
        key = note_hash(corp[i+1])
        ngram[key].append(note.Note('C##0'))
    return ngram

def gen_sequence(ngrams):
    start = random.choice(list(ngrams.keys()))
    start = random.choice(ngrams[start])

    seq = [start]
    count = 1

    nex = start
    nex_key = note_hash(nex)

    last_count = 1
    last_pitch = nex.pitch.nameWithOctave

    while count < 30:
        if len(ngrams[nex_key]) < 1:
            break
        nex = random.choice(ngrams[nex_key])
        nex_key = note_hash(nex)

        # Prevent more than 4 of the same note from appearing in a row
        if nex.pitch == last_pitch:
            last_count += 1
            if last_count > 4:
                while nex.pitch == last_pitch:
                    nex = random.choice(ngrams[nex_key])
                    nex_key = note_hash(nex)
        else:
            last_pitch = nex.pitch
            last_count = 1

        # Exit loop on hitting end marker
        if nex.pitch.name == 'C##':
            break

        # music21 bitches about adding notes with the same ID twice
        seq.append(deepcopy(nex))
        count += 1

    return seq

res = gen_bigram('prog/*.abc')
bpm = 126

for i in range(1):
    mstream = stream.Stream()
    mm = tempo.MetronomeMark(number=bpm, referent='quarter')
    mstream.append(mm)

    for n in gen_sequence(res):
        mstream.append(n)
        print(n.pitch, n.duration.quarterLength, end=', ')
    print('')

    sp = midi.realtime.StreamPlayer(mstream)
    sp.play()
