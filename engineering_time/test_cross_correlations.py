#!/usr/bin/env python

import image_registration as ir # github.com/keflavich/image_registration
import astropy.io.fits as fits
d0 = fits.getdata('test.fits')

# this test just makes sure that the cross_correlation_shifts is working
# correctly for the MOSFIRE data
def test_cross_correlation_shifts():
	corr = ir.cross_correlation_shifts(d0,d0)
	assert round(corr[0]) == 0 and round(corr[1]) == 0, "Running cross-correlation on the same object should return an xshift and yshift that are essentially zero."
