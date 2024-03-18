# Mai

## Prerequisites

Install the following dependencies (if not done yet):

1. `git` and `python` installed on your machine
2. AWS CLI set up with a default profile. Profile must have access to Amazon Bedrock
3. Requested access to "Anthropic Claude" and "Amazon Titan Embeddings G1 - Text" base models in Amazon Bedrock (us-east-1)
4. For macOS, install ffmpeg and portaudio with `brew install ffmpeg portaudio`

## Setup

1. Clone this repository

2. Change directory with `cd mai`

3. Run the following commands to set up.

   - MacOS: `sh setup.sh`
   - Windows: `.\setup.ps1`

## Usage

1. Activate virtual environment.

   - MacOS: `source mai-env/bin/activate`
   - Windows: `.\mai-env\Scripts\activate`

2. Run the following command to start the Command Line Interface (CLI) or User Interface (UI).

   - CLI: `mai`
   - UI: `python3 src/mai/ui.py`
