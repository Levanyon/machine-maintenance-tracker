from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_DATA_FILE = Path("machines.json")


@dataclass
class Machine:
    name: str
    hours_since_maintenance: float
    maintenance_interval: float

    @property
    def remaining_hours(self) -> float:
        return self.maintenance_interval - self.hours_since_maintenance

    @property
    def maintenance_due(self) -> bool:
        return self.remaining_hours <= 0


def load_machines(path: str | Path = DEFAULT_DATA_FILE) -> list[Machine]:
    data_path = Path(path)
    if not data_path.exists():
        return []

    raw = json.loads(data_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Machine data must contain a JSON list.")

    machines: list[Machine] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("Each machine entry must be a JSON object.")

        machines.append(
            Machine(
                name=str(item["name"]),
                hours_since_maintenance=float(item["hours_since_maintenance"]),
                maintenance_interval=float(item["maintenance_interval"]),
            )
        )

    return machines


def save_machines(
    machines: list[Machine],
    path: str | Path = DEFAULT_DATA_FILE,
) -> None:
    data_path = Path(path)
    payload = [asdict(machine) for machine in machines]
    data_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def find_machine(machines: list[Machine], name: str) -> Machine:
    for machine in machines:
        if machine.name.casefold() == name.casefold():
            return machine
    raise ValueError(f"Machine not found: {name}")


def add_machine(
    machines: list[Machine],
    name: str,
    maintenance_interval: float,
    initial_hours: float = 0.0,
) -> Machine:
    if not name.strip():
        raise ValueError("Machine name cannot be empty.")
    if maintenance_interval <= 0:
        raise ValueError("Maintenance interval must be greater than zero.")
    if initial_hours < 0:
        raise ValueError("Initial hours cannot be negative.")

    try:
        find_machine(machines, name)
    except ValueError:
        pass
    else:
        raise ValueError(f"Machine already exists: {name}")

    machine = Machine(
        name=name.strip(),
        hours_since_maintenance=initial_hours,
        maintenance_interval=maintenance_interval,
    )
    machines.append(machine)
    return machine


def log_hours(machine: Machine, hours: float) -> None:
    if hours <= 0:
        raise ValueError("Logged hours must be greater than zero.")
    machine.hours_since_maintenance += hours


def complete_maintenance(machine: Machine) -> None:
    machine.hours_since_maintenance = 0.0


def format_machine(machine: Machine) -> str:
    status = "MAINTENANCE DUE" if machine.maintenance_due else "OK"
    remaining = machine.remaining_hours

    if remaining >= 0:
        remaining_text = f"{remaining:.1f} h remaining"
    else:
        remaining_text = f"{abs(remaining):.1f} h overdue"

    return (
        f"{machine.name}: "
        f"{machine.hours_since_maintenance:.1f}/{machine.maintenance_interval:.1f} h | "
        f"{remaining_text} | {status}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Track machine operating hours and preventive maintenance intervals."
    )
    parser.add_argument(
        "--data-file",
        default=str(DEFAULT_DATA_FILE),
        help="JSON data file path (default: machines.json)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a machine")
    add_parser.add_argument("name")
    add_parser.add_argument("interval", type=float, help="Maintenance interval in hours")
    add_parser.add_argument(
        "--initial-hours",
        type=float,
        default=0.0,
        help="Existing hours since last maintenance",
    )

    log_parser = subparsers.add_parser("log", help="Add operating hours")
    log_parser.add_argument("name")
    log_parser.add_argument("hours", type=float)

    service_parser = subparsers.add_parser(
        "service",
        help="Mark maintenance as completed",
    )
    service_parser.add_argument("name")

    subparsers.add_parser("list", help="Show all machines")

    return parser


def main() -> None:
    args = build_parser().parse_args()

    try:
        machines = load_machines(args.data_file)

        if args.command == "add":
            machine = add_machine(
                machines,
                args.name,
                args.interval,
                args.initial_hours,
            )
            save_machines(machines, args.data_file)
            print(f"Added: {format_machine(machine)}")

        elif args.command == "log":
            machine = find_machine(machines, args.name)
            log_hours(machine, args.hours)
            save_machines(machines, args.data_file)
            print(format_machine(machine))

        elif args.command == "service":
            machine = find_machine(machines, args.name)
            complete_maintenance(machine)
            save_machines(machines, args.data_file)
            print(f"Maintenance completed: {format_machine(machine)}")

        elif args.command == "list":
            if not machines:
                print("No machines registered.")
            for machine in machines:
                print(format_machine(machine))

    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main()
