# DrChord
DrChord is an AI-powered AMT app that makes it easier for any guitarist to obtain the tabs for their
favourite song from an audio recording. The app consists of an accessible and intuitive web client, 
connected to a Python backend, which manages the work with the AMT and tab transcription models.

The singer only needs to create an account and log in. To get the tabs, just upload songs and wait a bit for the
magic behind DrChord to take place. After the system is done transcribing, the guitarist will be able to
retrieve a MIDI file of the uploaded song or the tabs within it, in a clean and formatted text file, in the 
desired file format (.txt, .docx, .pdf and .odt). It's as easy as it sounds!

## DrChord audio-to-tabs transcription workflow
The audio file is received by the server and stored on the system. When the user decides so, the MIDI of one of the given
audio files will be created by DrChord's AMT model and stored on the server. The MIDI will then be available to the user to
download, until they decide to erase the song or to rerun the transcription.

If the guitarist requests the tabs in text format, the [tuttut](https://github.com/natecdr/tuttut/tree/main/tuttut) Python library comes in, helping with the transcription from 
the previously generated MIDI file to the tabs in text format. The text tabs are stored as well on the server until the song 
is deleted or the initial AMT transcription (audio to MIDI) is done again.

## DrChord's AMT Model

Generation of musical features is done by running:
>\>> python GenFeature.py Maestro "C:/Users/Cristian/Downloads/GAPS" --phase train --piece-per-file 10 -s "C:/Users/Cristian/Downloads/guitar_features_big/train"
>\>> python GenFeature.py Maestro "C:/Users/Cristian/Downloads/GAPS" --phase test --piece-per-file 10 -s "C:/Users/Cristian/Downloads/guitar_features_big/test"
unde --phase specifica tipul de feature-uri prelucrate (de antrenare sau de test)
        
Training the model using the Transfer Learning method is done by running:
>\>> python TrainModel.py Maestro model_gaps_transfer --dataset-path "C:/Users/Cristian/Downloads/guitar_features_big" --input-model "./CheckPoint/Maestro-Note" --label-type frame_onset --epochs 50 --train-batch-size 4 --val-batch-size 2 --timesteps 128

### Training output
Model loading phase (initial step in training the model):
>Model ./CheckPoint/Maestro-Note loaded\
Loading training data\
Loading validation data\
Creating/loading model\
Information about this model\
            Model name: Maestro-Note\
            Input feature type: CFP\
            Input channels: [1, 3]\
            Timesteps: 128\
            Label type: frame_onset\
            Thresholds:\
                Instrument: 1.1\
                Frame: 0.25\
                Onset: 3\
                Duration: 0\
            Training settings:\
                Previously trained on Maestro\
                Maximum epochs: 20\
                Steps per epoch: 3000\
                Training batch size: 8\
                Validation batch size: 8\
                Loss function type: smooth\
                Early stopping: 6\
Model saved to ./model/Maestro-Note.

Model training phase (transfer learning results):

>Start training\
Epoch 1/50\
2000/2000 [==============================] - 454s 221ms/step - loss: 0.0970 - accuracy: 0.9806 - val_loss: 0.0975 - val_accuracy: 0.9779\
Epoch 2/50\
2000/2000 [==============================] - 485s 242ms/step - loss: 0.0955 - accuracy: 0.9811 - val_loss: 0.1012 - val_accuracy: 0.9814\
Epoch 3/50\
2000/2000 [==============================] - 432s 216ms/step - loss: 0.0944 - accuracy: 0.9818 - val_loss: 0.1170 - val_accuracy: 0.9810\
Epoch 4/50\
2000/2000 [==============================] - 439s 220ms/step - loss: 0.0938 - accuracy: 0.9823 - val_loss: 0.0943 - val_accuracy: 0.9812\
Epoch 5/50\
2000/2000 [==============================] - 453s 226ms/step - loss: 0.0937 - accuracy: 0.9825 - val_loss: 0.0948 - val_accuracy: 0.9822\
Epoch 6/50\
2000/2000 [==============================] - 446s 223ms/step - loss: 0.0935 - accuracy: 0.9828 - val_loss: 0.0943 - val_accuracy: 0.9818\
Epoch 7/50\
2000/2000 [==============================] - 444s 222ms/step - loss: 0.0935 - accuracy: 0.9828 - val_loss: 0.0936 - val_accuracy: 0.9828\
Epoch 8/50\
2000/2000 [==============================] - 442s 221ms/step - loss: 0.0925 - accuracy: 0.9838 - val_loss: 0.0947 - val_accuracy: 0.9815\
Epoch 9/50\
2000/2000 [==============================] - 442s 221ms/step - loss: 0.0928 - accuracy: 0.9836 - val_loss: 0.0940 - val_accuracy: 0.9826\
Epoch 10/50\
2000/2000 [==============================] - 442s 221ms/step - loss: 0.0927 - accuracy: 0.9838 - val_loss: 0.0947 - val_accuracy: 0.9823\
Epoch 11/50\
2000/2000 [==============================] - 441s 221ms/step - loss: 0.0931 - accuracy: 0.9842 - val_loss: 0.0966 - val_accuracy: 0.9798
 
### Easy CLI Model Testing
After the training is done, the model can be run inside any terminal, using the [Omnizart](https://github.com/Music-and-Culture-Technology-Lab/omnizart) v0.1.0 Python framework, by running the following command:
>\>> omnizart music transcribe <path_audio_file> -m? <path_guitar_model> -o? <path_to_generated_midi>

Omnizart is used in its early form (Release 0.1.0) because future updates add a lot of new AMT functionalities to the library that would be useless for guitar AMT and for DrChord.
Even though Omnizart v0.1.0 comes with a plethora of compatibility issues, it provides a cleaner and less complex framework to use in the AMT phase of the DrChord tabs generation process.
This way, the server side of the app benefits of less unused dependencies and plugins or of clunky unused modern features. These features might slow the server down or fill its storage
with unused AMT models weight files, which usually have a non-negligible size.

## Drchord's tabs generation model
The tabs generation model consists in using the Python library tuttut, which provides a Hidden Markov Model (HMM) for tabs recognition (from MIDI
files to model features) and tabs generation (from model features to strings inside a text file). 

The text output of the tuttut library is formatted after generation, because the library creates, by default, 6 extremely long text (tabulature) lines, 
which would be impossible to read by guitarists.

## DrChord's accuracy and limitations
DrChord works the best if the audio files given as input contain pure Steel/Nylon Acoustic Guitar (codes 24 - 25 in MIDI official standards) sound waves. 
Background noise, other instruments or voice singing, over the targeted instrument, will reduce the accuracy of the MIDI transcriptions, which will 
negatively influence the quality of the tabs in text format.

**IMPORTANT:** The generated MIDI files and tabs files might not be perfect interpretations of the given audio, because the AMT model that DrChord uses
is, basically, a piano model repurposed by transfer learning, into a guitar AMT model. The guitar model's performance is heavily affected by the reduced 
amount of training data available for guitar, free of charge. The AMT model was configured so that it can generalize transcriptions the best, which is already
a great feat in the AMT domain because of the complexity and expresiveness of the guitar. That is the reason why the MIDIs and the tabs will be very rich in notes.
It is considered that, for a guitarist, erasing unwanted or noise notes from MIDIs and tabs is much more feasible than adding missing key-notes by hand, because by adding
notes, measures will change more and their complexity will grow, instead of shrinking.

## Mentions
The _test_audio.mp3_ and the _test.mid_ files are extracted from the [Classical Guitar Collection's](https://www.youtube.com/@ArtemRasskazov) guitar interpretation of a 
piece, named _Song of the Ancients_, that belongs to the NieR Replicant (Gestalt) video game soundtrack, published by Square Enix. Link to the source YouTube video for these testing 
samples (the samples taken start at exactly **1:28**): [Song of the Ancients](https://youtu.be/VAIGr5j_-w4). 
