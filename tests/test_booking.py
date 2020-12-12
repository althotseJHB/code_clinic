import sys
import unittest
from io import StringIO
from unittest.mock import patch
from code_clinic import get_calendar_service, book_slot, view_available_slots, check_calendar_conflict


class TestBooking(unittest.TestCase):

    def test_booking_slot(self):
        service = get_calendar_service()
        with patch('sys.stdin', StringIO('wrong event id')):
            temp_out = StringIO()
            sys.stdout = temp_out
            book_slot(service)
            output = temp_out.getvalue().strip()
        service.close()
        table = view_available_slots()
        self.assertEqual(
            output, f'{table} \n\nPlease copy the event id that you want to book: You have entered an incorrect event_id')

    def test_check_calendar_conflict(self):
        self.assertFalse(check_calendar_conflict(' '))


# if __name__ == "__main__":
#     unittest.TestLoader()