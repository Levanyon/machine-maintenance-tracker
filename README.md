# Machine Maintenance Tracker

A small Python CLI for tracking machine operating hours and preventive maintenance intervals.

## Why this project?

Industrial equipment is often serviced after a defined number of operating hours. This project models that workflow with a local JSON file and a simple command-line interface.

## Features

- Register machines with a maintenance interval
- Record additional operating hours
- Show remaining hours until maintenance
- Flag overdue maintenance
- Mark maintenance as completed
- Persist data in JSON
- Validate invalid and duplicate input
- Automated tests with `unittest`
- GitHub Actions test workflow

## Example

Add a machine with a 1000-hour maintenance interval:

```bash
python maintenance_tracker.py add CNC-01 1000
```

Record 842 operating hours:

```bash
python maintenance_tracker.py log CNC-01 842
```

List machines:

```bash
python maintenance_tracker.py list
```

Example output:

```text
CNC-01: 842.0/1000.0 h | 158.0 h remaining | OK
```

After the interval is exceeded:

```text
CNC-01: 1050.0/1000.0 h | 50.0 h overdue | MAINTENANCE DUE
```

Mark maintenance as completed:

```bash
python maintenance_tracker.py service CNC-01
```

## Run tests

```bash
python -m unittest -v
```

## Concepts practiced

Python dataclasses, JSON persistence, pathlib, validation, exceptions, `argparse`, unit testing, and GitHub Actions.

The project uses only Python's standard library.
