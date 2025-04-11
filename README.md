# Example IOC for Archiver

IOC with example PVs to demonstrate the difference between the archiving policies.

Creates PVs of the type:

```
ARCH:PERIOD-1Hz:METHOD-SCAN:5Hz
```
then you can make a chart like:

![alt text](image.png)

## Running the example

```bash
docker compose up
```

## Installation

Install the dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```