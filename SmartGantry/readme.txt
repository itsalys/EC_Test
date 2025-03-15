Installation

MTD1: Automated Set Up

1. Run setup.sh 

chmod +x setup.sh
./setup.sh

MTD2: Manual Set Up

1. Create venv 

python3 -m venv smartgantry

2. Activate venv

Linux:      source smartgantry/bin/activate
Windows:    smartgantry\Scripts\activate

3. Install dependencies

sudo apt update
sudo apt install portaudio19-dev
sudo apt install cmake
pip install -r requirements.txt

4. Start application

python3 main.py