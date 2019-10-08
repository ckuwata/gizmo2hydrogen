# gizmo2hydrogen

Create a hydrogen's drumkit from a drumgizmo's drumkit

## Dependencies

* scipy

## Usage

```
python3 gizmo2hydrogen.py CONFIGFILE
```

## Config File Example

```
[drumkit]
name = SomeDrumkit
license = CC BY-SA
basedir = /path/to/drumgizmo/SomeDrumKit
mididef = midimap.xml
kitdef = drumkit.xml
destdir = /path/to/outdir
[mic_settings]
mics = Amb L, Amb R, Hihat, Kick L, Kick R, Overhead L, Overhead R, Ride, SnareBottom, SnareTop, Tom1, Tom2, Floor Tom1, Floor Tom2
Amb L = 1.0 # Pan to left
Amb R = -1.0 # Pan to right
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
```
