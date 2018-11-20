import unittest
import ApneaPreprocessing as ap; # functions to be tested

class IsFirstApneaOverlapInterval(unittest.TestCase):
    def test_NoOverlapInterval_1(self):
        input = [0, 1, 1, 1, 0];
        expected_output = False;
        output = ap.IsFirstApneaOverlapInterval(input);
        self.assertEqual(expected_output, output);

    def test_NoOverlapInterval_2(self):
        input = [0, 0, 1, 0, 1];
        expected_output = False;
        output = ap.IsFirstApneaOverlapInterval(input);
        self.assertEqual(expected_output, output);

    def test_NoOverlapInterval_3(self):
        input = [1, 0, 0, 0, 1];
        expected_output = False;
        output = ap.IsFirstApneaOverlapInterval(input);
        self.assertEqual(expected_output, output);

    def test_NoOverlapInterval_4(self):
        input = [0, 1, 1, 0, 1];
        expected_output = False;
        output = ap.IsFirstApneaOverlapInterval(input);
        self.assertEqual(expected_output, output);

    def test_NoOverlapInterval_5(self):
        input = [1, 1, 0, 0, 1];
        expected_output = False;
        output = ap.IsFirstApneaOverlapInterval(input);
        self.assertEqual(expected_output, output);

    def test_NoOverlapInterval_6(self):
        input = [1, 1, 1, 1, 1];
        expected_output = False;
        output = ap.IsFirstApneaOverlapInterval(input);
        self.assertEqual(expected_output, output);

    def test_OverlapInterval_1(self):
        input = [0, 1, 1, 1, 1];
        expected_output = True;
        output = ap.IsFirstApneaOverlapInterval(input);
        self.assertEqual(expected_output, output);

    def test_OverlapInterval_2(self):
        input = [0, 0, 0, 0, 1];
        expected_output = True;
        output = ap.IsFirstApneaOverlapInterval(input);
        self.assertEqual(expected_output, output);

    def test_OverlapInterval_3(self):
        input = [0, 0, 0, 0, 1];
        expected_output = True;
        output = ap.IsFirstApneaOverlapInterval(input);
        self.assertEqual(expected_output, output);

    def test_OverlapInterval_4(self):
        input = [0, 1, 1, 1, 1];
        expected_output = True;
        output = ap.IsFirstApneaOverlapInterval(input);
        self.assertEqual(expected_output, output);

# test cases for function
class ResampleAnnotations(unittest.TestCase):
    def test_NoOverlaps_5Hz_To_1Hz_DontPreserveSize(self):
        input_apnea_signal = [];
        expected_apnea_signal = [];

        # create input signal (in 5 element blocks (5Hz) for better visibility)
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([1, 0, 0, 0, 0]);
        input_apnea_signal.extend([0, 1, 0, 0, 0]);
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([0, 0, 1, 0, 0]);
        input_apnea_signal.extend([0, 0, 0, 1, 0]);
        input_apnea_signal.extend([0, 0, 0, 0, 1]);
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([1, 1, 1, 1, 1]);
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([0, 1, 1, 1, 0]);
        input_apnea_signal.extend([1, 0, 1, 0, 1]);

        # create expected signal (in 1 element blocks (1Hz) for better visibility)
        expected_apnea_signal.extend([0]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([0]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([0]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([0]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);

        output_apnea_signal = ap.ResampleAnnotations(input_apnea_signal, 5, 1, False, False, False);

        self.assertEqual(expected_apnea_signal, output_apnea_signal)

    def test_NoOverlaps_5Hz_To_1Hz_PreserveSize(self):
        input_apnea_signal = [];
        expected_apnea_signal = [];

        # create input signal (in 5 element blocks (5Hz) for better visibility)
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([1, 0, 0, 0, 0]);
        input_apnea_signal.extend([0, 1, 0, 0, 0]);
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([0, 0, 1, 0, 0]);
        input_apnea_signal.extend([0, 0, 0, 1, 0]);
        input_apnea_signal.extend([0, 0, 0, 0, 1]);
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([1, 1, 1, 1, 1]);
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([0, 1, 1, 1, 0]);
        input_apnea_signal.extend([1, 0, 1, 0, 1]);

        # create expected signal (in 5 element blocks (still 5Hz, because preserve_size = TRUE ) for better visibility)
        expected_apnea_signal.extend([0, 0, 0, 0, 0]);
        expected_apnea_signal.extend([1, 1, 1, 1, 1]);
        expected_apnea_signal.extend([1, 1, 1, 1, 1]);
        expected_apnea_signal.extend([0, 0, 0, 0, 0]);
        expected_apnea_signal.extend([1, 1, 1, 1, 1]);
        expected_apnea_signal.extend([1, 1, 1, 1, 1]);
        expected_apnea_signal.extend([1, 1, 1, 1, 1]);
        expected_apnea_signal.extend([0, 0, 0, 0, 0]);
        expected_apnea_signal.extend([1, 1, 1, 1, 1]);
        expected_apnea_signal.extend([0, 0, 0, 0, 0]);
        expected_apnea_signal.extend([1, 1, 1, 1, 1]);
        expected_apnea_signal.extend([1, 1, 1, 1, 1]);

        output_apnea_signal = ap.ResampleAnnotations(input_apnea_signal, 5, 1, True, False, False);

        self.assertEqual(expected_apnea_signal, output_apnea_signal)

    def test_withOverlaps_5Hz_To_1Hz_DontPreserveSize(self):
        input_apnea_signal = [];
        expected_apnea_signal = [];

        # create input signal (in 5 element blocks (5Hz) for better visibility)
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([1, 0, 0, 0, 0]);
        input_apnea_signal.extend([0, 1, 0, 0, 0]);
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([0, 0, 1, 0, 0]);
        input_apnea_signal.extend([0, 0, 0, 1, 0]);
        input_apnea_signal.extend([0, 0, 0, 0, 1]); # this time-frame must be seen as "no apnea"
        input_apnea_signal.extend([1, 1, 1, 1, 1]);
        input_apnea_signal.extend([0, 1, 1, 1, 0]);
        input_apnea_signal.extend([1, 0, 1, 0, 1]);

        # create expected signal (in 1 element blocks (1Hz) for better visibility)
        expected_apnea_signal.extend([0]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([0]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([0]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);

        output_apnea_signal = ap.ResampleAnnotations(input_apnea_signal, 5, 1, False, True, False);

        self.assertEqual(expected_apnea_signal, output_apnea_signal)

    def test_withOverlaps_5Hz_To_1Hz_DontPreserveSize_LongApnea(self):
        input_apnea_signal = [];
        expected_apnea_signal = [];

        # create input signal (in 5 element blocks (5Hz) for better visibility)
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([0, 0, 1, 1, 1]);
        input_apnea_signal.extend([1, 1, 1, 0, 0]);
        input_apnea_signal.extend([0, 0, 0, 0, 0]);
        input_apnea_signal.extend([0, 1, 1, 1, 1]);
        input_apnea_signal.extend([1, 1, 1, 1, 1]);
        input_apnea_signal.extend([1, 1, 1, 1, 1]);
        input_apnea_signal.extend([1, 1, 1, 1, 1]);
        input_apnea_signal.extend([1, 1, 1, 1, 1]);
        input_apnea_signal.extend([1, 0, 0, 0, 0]);

        # create expected signal (in 1 element blocks (1Hz) for better visibility)
        expected_apnea_signal.extend([0]);
        expected_apnea_signal.extend([0]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([0]);
        expected_apnea_signal.extend([0]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);
        expected_apnea_signal.extend([1]);

        output_apnea_signal = ap.ResampleAnnotations(input_apnea_signal, 5, 1, False, True, False);

        self.assertEqual(expected_apnea_signal, output_apnea_signal)

# run all test cases
if __name__ == '__main__':
    unittest.main()
