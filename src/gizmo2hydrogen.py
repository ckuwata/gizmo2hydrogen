#!/usr/bin/python3
import sys
import xml.dom.minidom as dom
from scipy.io.wavfile import read, write
import configparser
import numpy as np
import os

basstemplate = '''
<drumkit_info>
    <name>{name}</name>
    <author>kwt</author>
    <info>&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.0//EN&quot; &quot;http://www.w3.org/TR/REC-html40/strict.dtd&quot;&gt;&#x0A;&lt;html&gt;&lt;head&gt;&lt;meta name=&quot;qrichtext&quot; content=&quot;1&quot; /&gt;&lt;style type=&quot;text/css&quot;&gt;&#x0A;p, li {{ white-space: pre-wrap; }}&#x0A;&lt;/style&gt;&lt;/head&gt;&lt;body style=&quot; font-family:&apos;Lucida Grande&apos;; font-size:10pt; font-weight:400; font-style:normal;&quot;&gt;&#x0A;&lt;p style=&quot;-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</info>
    <license>{license}</license>
    <instrumentList>{content}
    </instrumentList>
</drumkit_info>
'''

template = '''
        <instrument>
            <id>{id}</id>
            <name>{instr}</name>
            <volume>1</volume>
            <isMuted>false</isMuted>
            <pan_L>1</pan_L>
            <pan_R>1</pan_R>
            <randomPitchFactor>0</randomPitchFactor>
            <gain>1</gain>
            <filterActive>false</filterActive>
            <filterCutoff>1</filterCutoff>
            <filterResonance>0</filterResonance>
            <Attack>0</Attack>
            <Decay>0</Decay>
            <Sustain>1</Sustain>
            <Release>100256</Release>
            <muteGroup>-1</muteGroup>
           <midiOutChannel>0</midiOutChannel>
           <midiOutNote>{id2}</midiOutNote>
            <layer>
                <filename>{instr}.wav</filename>
                <min>0</min>
                <max>1</max>
                <gain>1</gain>
                <pitch>0</pitch>
            </layer>
        </instrument>
'''

def writehydrogen(config):
    print(config.get('drumkit', 'name'))
    basedir = config.get('drumkit', 'basedir')
    midi = basedir + '/' + config.get('drumkit', 'mididef')
    kit = basedir + '/' + config.get('drumkit', 'kitdef')
    destdir = config.get('drumkit', 'destdir')
    midimap = dom.parseString(open(midi).read())
    drumkit = dom.parseString(open(kit).read())
    maps = midimap.getElementsByTagName('map')
    items = []
    for e in maps:
        ins = e.getAttribute('instr')
        items.append((e.getAttribute('note'), template.format(id=e.getAttribute('note'), id2=e.getAttribute('note'),instr=ins)))
        insfile = None
        for i in drumkit.getElementsByTagName('instrument'):
          if i.getAttribute('name') == ins:
            insfile = i.getAttribute('file')
            break
        assert insfile is not None
        instrdef = '{}/{}'.format(basedir, insfile)
        generatesample(instrdef, ins, insfile.rsplit('/', 1)[0], config)
    items.sort(key=lambda x:x[0])
    out = basstemplate.format(content='\n'.join([i[1] for i in items]), name=config.get('drumkit', 'name'), license=config.get('settings', 'license'))
    open(destdir + '/drumkit.xml', 'w').write(out)

def generatesample(instrdef, instr, insdir, config):
    print ('generating {}'.format(instr))
    destdir = config.get('drumkit', 'destdir')
    basedir = config.get('drumkit', 'basedir')
    xml = dom.parseString(open(instrdef).read())
    samples = xml.getElementsByTagName('sample')
    assert len(samples) >= 1
    sample = samples[-1]
    audiofile = sample.getElementsByTagName('audiofile')[0].getAttribute('file')
    wavfile = '{}/{}/{}'.format(basedir, insdir, audiofile)
    rate, data = read(wavfile)
    mics = [k.strip() for k in config.get('mic_settings', 'mics').split(',')]
    samplemap = {}
    leftchannel = []
    rightchannel = []
    for i, k in enumerate(mics):
        samplemap[k] = data[:, i]


    for i in range(len(samplemap[mics[0]])):
        leftchannel.append(0.0)
        rightchannel.append(0.0)

    for mic in mics:
        pan = float(config.get('mic_settings', mic))
        wav = samplemap[mic]
        if pan == 0:
          left = 0.5
          right = 0.5
        elif pan > 0.0:
          left = pan
          right = 1 - pan
        else:
          left = 1 + pan
          right = -pan
        for i, d in enumerate(wav):
            leftchannel[i] += d * left
            rightchannel[i] += d * right

    outdata = []
    result = np.transpose(np.array([leftchannel, rightchannel]))
    path = destdir + '/' + instr + '.wav'
    write(path, rate, result)

if len(sys.argv) < 2:
    print('Usage: {} CONFIGFILE'.format(sys.argv[0]))
    print('''Example:
[drumkit]
name = SomeDrumkit
license = CC BY-SA
basedir = /path/to/drumgizmo/SomeDrumKit
mididef = midimap.xml
kitdef = drumkit.xml
destdir = /path/to/outdir
[mic_settings]
mics = Amb L, Amb R, Hihat, Kick L, Kick R, Overhead L, Overhead R, Ride, SnareBottom, SnareTop, Tom1, Tom2, Floor Tom1, Floor Tom2
Amb L = 1.0
Amb R = -1.0
Hihat = -0.7
Kick L = 0.0
Kick R = 0.0
Overhead L = 1.0
Overhead R = -1.0
Ride = 0.7
Snare Bottom = 0.0
Snare Top = 0.0
Tom1 = -0.2
Tom2 = 0.2
Floor Tom1 = 0.3
Fllor Tom2 = 0.4
''')
else:
    config = configparser.ConfigParser()
    config.read(sys.argv[1])
    writehydrogen(config)
