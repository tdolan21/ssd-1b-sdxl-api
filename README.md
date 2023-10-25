# SSD-1B Interface


## Installation

```bash
git clone https://github.com/tdolan21/ssd-8b-ui
cd SSD-1B-UI
pip install -r requirements.txt
```

```bash
pip install git+https://github.com/huggingface/diffusers
```

## Usage

Linux:

```bash
chmod +x run.sh
./run.sh
```

Windows: 

```bash
run.bat
```

After running the startup script the UI will be available at:

```
127.0.0.1:8501
```

The API will be available at:

```
127.0.0.1:8000/docs
```

## Endpoints

Currently this just has a generate image endpoint to take the load off of the interface and decrease the time it takes for inference.
