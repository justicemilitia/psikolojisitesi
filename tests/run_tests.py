import unittest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test modules
from tests.test_user_model import UserModelTestCase
from tests.test_psychologist_model import PsychologistModelTestCase
from tests.test_appointment_model import AppointmentModelTestCase
from tests.test_user_service import UserServiceTestCase
from tests.test_psychologist_service import PsychologistServiceTestCase
from tests.test_appointment_service import AppointmentServiceTestCase
from tests.test_auth_routes import AuthRoutesTestCase
from tests.test_main_routes import MainRoutesTestCase
from tests.test_psychologist_routes import PsychologistRoutesTestCase
from tests.test_appointment_routes import AppointmentRoutesTestCase
from tests.test_user_routes import UserRoutesTestCase

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add model tests
    test_suite.addTest(unittest.makeSuite(UserModelTestCase))
    test_suite.addTest(unittest.makeSuite(PsychologistModelTestCase))
    test_suite.addTest(unittest.makeSuite(AppointmentModelTestCase))
    
    # Add service tests
    test_suite.addTest(unittest.makeSuite(UserServiceTestCase))
    test_suite.addTest(unittest.makeSuite(PsychologistServiceTestCase))
    test_suite.addTest(unittest.makeSuite(AppointmentServiceTestCase))
    
    # Add route tests
    test_suite.addTest(unittest.makeSuite(AuthRoutesTestCase))
    test_suite.addTest(unittest.makeSuite(MainRoutesTestCase))
    test_suite.addTest(unittest.makeSuite(PsychologistRoutesTestCase))
    test_suite.addTest(unittest.makeSuite(AppointmentRoutesTestCase))
    test_suite.addTest(unittest.makeSuite(UserRoutesTestCase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)