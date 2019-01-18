import unittest
import Preprocessing_Annotations.ApneaPreprocessing as ap;
import numpy as np
import pprint
import csv

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

class DetectInvalildSignal(unittest.TestCase):
    def test_shhs_200002(self):
        path = 'D:\\GitRepositories\\DSDM\\Period1\\github_ecg\\db_shhs\\edfs\\shhs1\\shhs1-200002.edf'
        ecg,_,_ = ap.SHHS_ReadDataset(path, 100)

        sample_length = 6000
        num_samp = int(np.ceil(len(ecg) / sample_length))

        result = []
        for j in range(num_samp):
            l = j * sample_length
            h = (j + 1) * sample_length

            if j == (num_samp - 1):
                break

            sample = ecg[l:h]

            validity = ap.isValidECGChunk(sample)
            result.append(validity)

        expected = np.array([True] * num_samp)

        invalid_elements = [56, 57, 59, 60, 81, 82, 85, 155, 156, 159, 160, 198, 202, 205, 225, 226, 229, 230, 231, 232]
        for i in invalid_elements:
            expected[i] = False
        expected[232:num_samp-1] = False # rest of array is invalid
        for i in range(expected.size):
            print (str(i) + ': ' + str(expected[i]))

        with open('DetectInvalildSignal_test_shhs_200002.txt', mode='w+',
                  newline='') as csv_file:
            fieldnames = \
                ['expected',
                 'result',
                 ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='\t')
            for i in range(expected.size-1):
                writer.writerow({'expected': expected[i],
                                 'result': result[i],
                                 })
            number_errors = 0
            for i in range(expected.size - 1):
                if expected[i] != result[i]:
                    number_errors += 1
            writer.writerow({'expected': 'test_shhs_200002: '+ 'error_num=' + str(number_errors) + ', error[%]='+ str((number_errors/num_samp)*100),
                             'result': "",
                             })

        self.assertEqual(result, expected)


# run all test cases
if __name__ == '__main__':
    unittest.main()
