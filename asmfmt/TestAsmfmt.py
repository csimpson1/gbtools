import argparse
import filecmp
import os
import shutil
import unittest

import asmfmt

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
            args = asmfmt.parse_args([inputFile, '-o', outputFile, '-g'])
        else:
            args = asmfmt.parse_args([inputFile, '-o', outputFile])
        
        self.formatter = asmfmt.AsmFormatter(args.input, args.output, args.global_indent)
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
    
    def test_block_comment(self):
        """
        Tests the formatting of block comments
        
        Input: Two lines with no code that contain only comments
        Output: The same two lines of text, but now in a block comment
        """
        
        inp = '2_1_block_comment.txt'
        self.run_single_file_case(inp)
        
    def test_two_block_comments(self):
        
        """
        Tests the formatting of multiple block comments, and the ability of the formatter
        to separate them
        
        Input: Two sets of comments, separated by a linebreak
        Output: Two properly formatted block comments
        """
        
        inp = '2_2_block_comment.txt'
        self.run_single_file_case(inp)
        
    def test_block_comment_whitespace_signature(self):
        """
        Tests the formating of multiple block comments when separated by different types of whitespace
        
        Input: Three sets of comments, each with a different amount of leading whitespace
        Output: Three properly formatted block comments
        """
        
        inp = '2_3_block_comment.txt'
        self.run_single_file_case(inp)
        
    def test_indented_block_comment(self):
        """
        Tests the formatting of a block comment that is already indented.
        Input: Some indented comment lines
        Output: A properly formatted block comment, that is also indented
        """
        
        inp = '2_4_block_comment.txt'
        self.run_single_file_case(inp)
        
    def test_already_formatted_block_comment(self):
        """
        Tests the formatting of an already formatted block comment
        
        Input: A formatted block comment
        Output: The same file
        """
        
        inp = '2_5_block_comment.txt'
        self.run_single_file_case(inp)
        
    def test_fmt_in_place(self):
        """
        Tests the formatting of a document in place. 
        
        Input: A file containing a mix of code and comments
        Output: The same file, modified and formatted properly
        
        """
        
        inp = '3_1_modify_in_place.txt'
        testFilePath = os.path.join(os.path.dirname(__file__), 'test_files')
        inpFile = os.path.join(testFilePath, inp)
        modInPlaceFile = os.path.join(testFilePath, '3_1_modify_in_place_work.txt')
        refFile = os.path.join(os.path.dirname(__file__), 'reference_files', inp[:-4] + '_ref' + inp[-4:])
        
        shutil.copy2(inpFile, modInPlaceFile)
        
        args = asmfmt.parse_args([modInPlaceFile])

        self.formatter = asmfmt.AsmFormatter(args.input, args.output, args.global_indent)
        self.formatter.format_files()
        
        self.compare_and_track_files(modInPlaceFile, refFile)
        
        
        
        
        
        

if __name__ == '__main__':
    unittest.main()
