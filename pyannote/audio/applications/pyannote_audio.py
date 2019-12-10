#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2019 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


"""
Neural building blocks for speaker diarization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage:
  pyannote-audio (sad | scd | ovl | emb | dom) train    [options] <root>     <protocol>
  pyannote-audio (sad | scd | ovl | emb | dom) validate [options] <train>    <protocol>
  pyannote-audio (sad | scd | ovl | emb | dom) apply    [options] <validate> <protocol>
  pyannote-audio -h | --help
  pyannote-audio --version

This command line tool can be used to train, validate, and apply neural networks
for the following blocks of a speaker diarization pipeline:

    * (sad) speech activity detection consists in detecting speech regions in
            an audio recording.
    * (scd) speaker change detection consists in detecting timestamps of
            speaker change point.
    * (ovl) overlapped speech detection consists in detection regions with two
            or more simultaneous speakers.
    * (emb) speaker embedding consists in projecting audio chunk into a
            (usually high-dimensional) vector space where same speaker
            embeddings are close to each other, and different speaker embeddings
            are not.
    * (dom) domain classification consists in predicting the domain of an
            audio recording

Running a complete speech activity detection experiment on the provided
"debug" dataset would go like this:

    * Blah balh
      $ export DATABASE=Debug.SpeakerDiarization.Debug

    * This directory will contain experiments artifacts:
      $ mkdir my_experiment && cd my_experiment

    * A unique configuration file describes the experiment hyper-parameters
      (see "Configuration file" below for details):
      $ edit config.yml

    * This will train the model on the training set:
      $ pyannote-audio sad train ${PWD} ${DATABASE}

    * Training artifacts (including model weights) are stored in a sub-directory
      whose name makes it clear which dataset and subset (train, by default)
      were used for training the model.
      $ cd train/${DATABASE}.train

    * This will validate the model on the development set:
      $ pyannote-audio sad validate ${PWD} ${DATABASE}

    * Validation artifacts (including the selection of the best epoch) are
      stored in a sub-directory named after the dataset and subset (development,
      by default) used for validating the model.
      $ cd validate/${DATABASE}.development

    * This will apply the best model (according to the validation step) to the
      test set:
      $ pyannote-audio sad apply ${PWD} ${DATABASE}

    * Inference artifacts are stored in a sub-directory whose name makes it
      clear which epoch has been used (e.g. apply/0125). Artifacts include:
        * raw output of the best model (one numpy array per file  than can be
          loaded with pyannote.audio.features.Precomputed API and handled with
          pyannote.core.SlidingWindowFeature API)
        * (depending on the task) a file "${DATABASE}.test.rttm" containing the
          post-processing of raw output.
        * (depending on the task) a file "${DATABASE}.test.eval" containing the
          evaluation result computed with pyannote.metrics.

pyannote.database support
~~~~~~~~~~~~~~~~~~~~~~~~~

PYANNOTE_DATABASE_CONFIG=

Configuration file <root>/config.yml
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Reproducible research is facilitated by the systematic use of configuration
    files stored in <root>/config.yml in YAML format.

    .......................... <root>/config.yml ..........................
    task:
        name:
        params:

    feature_extraction:
        name:
        params:

    data_augmentation:
        name:
        params:

    architecture:
        name:
        params:

    scheduler:
        name:
        params:

    preprocessors:

    callbacks:
    ...................................................................

Tensorboard support
~~~~~~~~~~~~~~~~~~~

    A bunch of metrics are logged during training and validation (e.g. loss,
    learning rate, computation time, validation metric). They can be visualized
    using tensorboard:

        $ tensorboard --logdir=<root>

Common options
~~~~~~~~~~~~~~

  <root>                  Experiment root directory. Should contain config.yml
                          configuration file.

  <protocol>              Name of protocol to use for training, validation, or
                          inference. Have a look at pyannote.database
                          documentation for instructions on how to define a
                          protocol with your own dataset:
                          https://github.com/pyannote/pyannote-database#custom-protocols

  <train>                 Path to <root> sub-directory containing training
                          artifacts (e.g. <root>/train/<protocol>.train)

  <validate>              Path to <train> sub-directory containing validation
                          artifacts (e.g. <train>/validate/<protocol>.development)

  --subset=<subset>       Subset to use for training (resp. validation,
                          inference). Defaults to "train" (resp. "development",
                          "test") for strict enforcement of machine learning
                          good practices.

  --gpu                   Run on GPUs. Defaults to using CPUs.

  --from=<epoch>          Start training (resp. validating) at epoch <epoch>.
                          Not used for inference [default: 0].

  --to=<epoch>            End training (resp. validating) at epoch <epoch>.
                          [default: 100].

  --batch=<size>          Set batch size used for validation and inference.
                          Has no effect when training as this parameter should
                          be defined in the configuration file [default: 32].

  --step=<ratio>          Ratio of audio chunk duration used as step between
                          two consecutive audio chunks [default: 0.25]

Speaker embedding
~~~~~~~~~~~~~~~~~

  --duration=<duration>   Use audio chunks with that duration. Defaults to the
                          fixed duration used during training, when available.

   --metric=<metric>      Use this metric (e.g. "cosine" or "euclidean") to
                          compare embeddings. Defaults to the metric defined in
                          <root>/config.yml configuration file.

Training options
~~~~~~~~~~~~~~~~

  --pretrained=<model>    Warm start training with pre-trained model. Can be
                          either a path to an existing checkpoint (e.g.
                          <train>/weights/0050.pt) or the name of a model
                          available in torch.hub.list('pyannote/pyannote.audio')

Validation options
~~~~~~~~~~~~~~~~~~

  --every=<epoch>         Validate model every <epoch> epochs [default: 1].

  --evergreen             Prioritize validation of most recent epoch.

  --parallel=<n_jobs>     Process that many files in parallel. Defaults to
                          using all CPUs.

  For speaker change detection, validation consists in looking for the value of
  the peak detection threshold that maximizes segmentation coverage, given that
  segmentation purity is greater than a target value:

  --purity=<value>        Set target purity [default: 0.9].

  --diarization           Use diarization purity and coverage instead of
                          segmentation purity and coverage.

  For overlapped speech detection, validation consists in looking for the value
  of the detection threshold that maximizes recall, given that precision is
  greater than a target value:

  --precision=<value>     Set target precision [default: 0.8].

  For speaker embedding,
    * validation of speaker verification protocols runs the actual speaker
      verification experiment (representing each recording by its average
      embedding) and reports equal error rate.
    * validation of speaker diarization protocols runs a speaker diarization
      pipeline based on oracle segmentation and "median-linkage" agglomerative
      clustering of speech turns (represented by their average embedding), and
      looks for the threshold that maximizes coverage, given that purity is
      greater than a target value.

"""


from docopt import docopt
from pathlib import Path
import multiprocessing


import torch
from .speech_detection import SpeechActivityDetection
from .change_detection import SpeakerChangeDetection
from .overlap_detection import OverlapDetection
from .speaker_embedding import SpeakerEmbedding
from .domain_classification import DomainClassification


def main():

    # TODO: update version automatically
    arg = docopt(__doc__, version='pyannote-audio 2.0')

    params = {}

    if arg['sad']:
        Application = SpeechActivityDetection

    elif arg['scd']:
        Application = SpeakerChangeDetection

    elif arg['ovl']:
        Application = OverlapDetection

    elif arg['emb']:
        Application = SpeakerEmbedding

    elif arg['dom']:
        Application = DomainClassification

    params['device'] = torch.device('cuda') if arg['--gpu'] else \
                       torch.device('cpu')

    # "book" GPU as soon as possible
    _ = torch.Tensor([0]).to(params['device'])

    protocol = arg['<protocol>']
    subset = arg['--subset']

    if arg['train']:
        root_dir = Path(arg['<root>']).expanduser().resolve(strict=True)
        app = Application(root_dir, training=True)

        params['subset'] = 'train' if subset is None else subset

        # start training at this epoch (defaults to 0)
        warm_start = int(arg['--from'])

        # or start from pretrained model
        pretrained = arg['--pretrained']
        if pretrained is not None:

            # start from an existing model checkpoint
            # (from a different experiment)
            if Path(pretrained).exists():
                warm_start = Path(pretrained)

            else:
                try:
                    warm_start = torch.hub.load('pyannote/pyannote-audio:v2',
                                                pretrained, return_path=True)
                except Exception as e:
                    msg = (
                        f'Could not load "{warm_start}" model from torch.hub.'
                        f'The following exception was raised:\n\n{e}\n\n')
                    sys.exit(msg)

        params['warm_start'] = warm_start

        # stop training at this epoch (defaults to never stop)
        params['epochs'] = int(arg['--to'])

        app.train(protocol, **params)

    if arg['validate']:

        train_dir = Path(arg['<train>']).expanduser().resolve(strict=True)
        app = Application.from_train_dir(train_dir, training=False)

        params['subset'] = 'development' if subset is None else subset
        params['start'] = int(arg['--from'])
        params['end'] = int(arg['--to'])
        params['every'] = int(arg['--every'])
        params['chronological'] = not arg['--evergreen']
        params['batch_size'] = int(arg['--batch'])

        n_jobs = arg['--parallel']
        if n_jobs is None:
            n_jobs = multiprocessing.cpu_count()
        params['n_jobs'] = int(n_jobs)

        params['purity'] = float(arg['--purity'])
        params['diarization'] = arg['--diarization']
        params['precision'] = float(arg['--precision'])

        duration = arg['--duration']
        if duration is None:
            duration = getattr(app.task_, 'duration', None)
            if duration is None:
                msg = ("Task has no 'duration' defined. "
                       "Use '--duration' option to provide one.")
                raise ValueError(msg)
        else:
            duration = float(duration)
        params['duration'] = duration

        params['step'] = float(arg['--step'])

        if arg['emb']:

            metric = arg['--metric']
            if metric is None:
                metric = getattr(app.task_, 'metric', None)
                if metric is None:
                    msg = ("Approach has no 'metric' defined. "
                           "Use '--metric' option to provide one.")
                    raise ValueError(msg)
            params['metric'] = metric

        app.validate(protocol, **params)

    if arg['apply']:
        validate_dir = Path(arg['<validate>']).expanduser().resolve(strict=True)
        app = Application.from_validate_dir(validate_dir, training=False)

        params['subset'] = 'test' if subset is None else subset
        params['batch_size'] = int(arg['--batch'])

        duration = arg['--duration']
        if duration is None:
            duration = getattr(app.task_, 'duration', None)
            if duration is None:
                msg = ("Task has no 'duration' defined. "
                       "Use '--duration' option to provide one.")
                raise ValueError(msg)
        else:
            duration = float(duration)
        params['duration'] = duration

        params['step'] = float(arg['--step'])

        app.apply(protocol, **params)