import unittest
from unittest.mock import patch
from io import StringIO
from test_base import captured_io
from code_clinic import check_volunteer_slot_conflict


class TestFunctions(unittest.TestCase):

    # Test the check_volunteer_slot_conflict function.
    # TDD RED - Make it FAIL.
    def test_check_volunteer_slot_conflict(self):
        with captured_io(StringIO('14 dec 2030 14:45\n')) as (out, err):
            check_volunteer_slot_conflict(
                'patient.json', '14 dec 2030 14:45')

        output = out.getvalue().strip()
        self.assertEqual("""Please enter your volunteer slots DATE and START-TIME.
Note, the duration of the volunteer slot will be 90-minutes.
Day Month Time - [14 dec 14:30]: 14 dec 2030 14:45
'Python TDD' event time conflict found.
The events end-time is in your volunteer slots proposed 90-minute time range.
    -> 'Python TDD' event info: [Saturday]  [14-12-2030]    [14:30 - 15:00].
Please select a different time for your volunteer slot.""", output)