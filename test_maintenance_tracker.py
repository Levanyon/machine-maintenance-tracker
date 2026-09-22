import tempfile
import unittest
from pathlib import Path

from maintenance_tracker import (
    Machine,
    add_machine,
    complete_maintenance,
    find_machine,
    load_machines,
    log_hours,
    save_machines,
)


class MaintenanceTrackerTests(unittest.TestCase):
    def test_machine_status_before_and_after_interval(self):
        machine = Machine("CNC-01", 800.0, 1000.0)
        self.assertFalse(machine.maintenance_due)
        self.assertEqual(machine.remaining_hours, 200.0)

        log_hours(machine, 250.0)
        self.assertTrue(machine.maintenance_due)
        self.assertEqual(machine.remaining_hours, -50.0)

    def test_add_machine_rejects_duplicate_name(self):
        machines = [Machine("Pump-01", 0.0, 500.0)]

        with self.assertRaises(ValueError):
            add_machine(machines, "pump-01", 600.0)

    def test_find_machine_is_case_insensitive(self):
        machines = [Machine("Motor-A", 10.0, 100.0)]
        self.assertIs(find_machine(machines, "motor-a"), machines[0])

    def test_complete_maintenance_resets_hours(self):
        machine = Machine("Conveyor-01", 350.0, 300.0)
        complete_maintenance(machine)
        self.assertEqual(machine.hours_since_maintenance, 0.0)
        self.assertFalse(machine.maintenance_due)

    def test_save_and_load_round_trip(self):
        machines = [
            Machine("CNC-01", 120.5, 1000.0),
            Machine("Pump-02", 40.0, 250.0),
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "machines.json"
            save_machines(machines, path)
            loaded = load_machines(path)

        self.assertEqual(loaded, machines)

    def test_invalid_values_are_rejected(self):
        with self.assertRaises(ValueError):
            add_machine([], "", 100.0)
        with self.assertRaises(ValueError):
            add_machine([], "Motor", 0.0)

        machine = Machine("Motor", 0.0, 100.0)
        with self.assertRaises(ValueError):
            log_hours(machine, 0.0)


if __name__ == "__main__":
    unittest.main()
