from drift import *

# masking out skylines in one raw frame
test = Drift()

test.date = '2018nov25'
test.mask = 'UDS_2018B_J'
test.dither = 1.5
test.band = 'J'

test.row_start = 92
test.row_end = 173
test.col_start = 0
test.col_end = -1

home = '/home/aibhleog/Desktop/observing/'
filename = 'm181125'