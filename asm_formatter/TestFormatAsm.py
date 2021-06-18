import argparse
import filecmp
import os
import unittest

import FormatAsm

class TestFormatMethods(unittest.TestCase):
    
    successfulTestFiles = []
    
    @classmethod
    def tearDownClass(cls):
        for file in cls.successfulTestFiles:
            os.remove(file)
    
    
    def get_output_names(self, inputFile):
        """
        Get the name of the output file, and the reference file for a test.
        Output files can be stored in the same dir as the input, and reference files will in a different dir
        
        """
        
        dir = os.path.dirname(__file__)
        newInputFile = os.path.join(dir, 'test_files', inputFile)
        outputFile = os.path.join(dir, 'test_files', inputFile[:-4] + '_result' + inputFile[-4:])
        
        #[:4] removes the .txt from the end of the filename below
        refFile = inputFile[:-4]
        ref = os.path.join(dir, 'reference_files', refFile + '_ref.txt')
        
        return (newInputFile, outputFile, ref)
    
    def compare_and_track_files(self, output, ref):
        """
        Compare the output file created by the formatter and the reference file. If they match, make note of it so that this file gets
        cleaned up after the test is run.
        """
        result = filecmp.cmp(output, ref)
        
        if result:
            self.successfulTestFiles.append(output)
        
        self.assertTrue(result)
    
    def run_single_file_case(self, fName, globalIndent = False):
        """
        Get the proper file names, parse the arguments, and run the formatter
        """
        inputFile, outputFile, refFile = self.get_output_names(fName)
        
        if globalIndent:
            args = FormatAsm.parse_args([inputFile, '-o', outputFile, '-g'])
        else:
            args = FormatAsm.parse_args([inputFile, '-o', outputFile])
        
        self.formatter = FormatAsm.AsmFormatter(args.input, args.output, args.global_indent)
        self.formatter.format_files()
        
        self.compare_and_track_files(outputFile, refFile)
    
    def test_code_comment_positive(self):
        """
        Tests formatting of code comments. Input is two lines of code with comments. Output should
        have the comments now at the same indent level
        """     
        
        inp = '1_1_code_comment.txt'
        self.run_single_file_case(inp)
        
    def test_code_comment_negative(self):
        """
        Tests non-formatting of already formatted code comments. Input is two lines of code with comments at the same indent level
        Output should be identical to the input.
        """
        
        inp = '1_2_code_comment.txt'
        self.run_single_file_case(inp)
    
    def test_code_comment_global_indent_off(self):
        """
        Tests formatting of code comments with global indent turned off.
        
        Input: File contains two groups of code, separated by a comment (to force the creation of two code groups). 
        Neither group has the same indent level
        
        Output: Comments are formatted based on the maximum indent level in each group.
        """
        
        inp = '1_3_code_comment.txt'
        self.run_single_file_case(inp)
        
    def test_code_comment_global_indent_on(self):
        """
        Tests formatting of code comments with global indent turned on.
        
        Input: File contains two groups of code, separated by a comment (to force the creation of two code groups). 
        Neither group has the same indent level
        
        Output: Comments are formatted based on the maximum indent level in the file.
        """
        
        inp = '1_4_code_comment.txt'
        self.run_single_file_case(inp, globalIndent=True)
        
    def test_indented_code_comment(self):
        """
        Tests that formatting of code comments is not affected when the lines of code themselves are indented
        
        Input: Two lines of indented code
        Output: The comments should be indented to match the maximum indent level in the group
        """
        
        inp = '1_5_code_comment.txt'
        self.run_single_file_case(inp)
    
    def test_format_in_place(self):
        """
        Test formatting a document in place. We want to be able to run multiple tests, so create a copy of 
        the file to be formatted first.
        """
        pass
    
    def test_multiple_format_in_place(self):
        """
        Test formating multiple documents in place. Want to be able to run multiple tests, so create
        copies of the files to be formatted first
        """
        pass
    
    def test_multiple_format(self):
        """
        Test formatting multiple documents in one pass
        """
        pass
    
    def test_multiple_format_combined(self):
        """
        Test formatting multiple documents, some in place and some not, in a single pass
        """
        
        pass
        
    def test_global_indent(self):
        """
        Test the global indent feature
        """
        
        pass

if __name__ == '__main__':
    unittest.main()