#!/usr/bin/env python

import image_registration as ir # github.com/keflavich/image_registration
import astropy.io.fits as fits
import numpy as np
d0 = fits.getdata('test.fits')

# this test just makes sure that the cross_correlation_shifts is working
# correctly for the MOSFIRE data
def test_cross_correlation_shifts():
	corr = ir.cross_correlation_shifts(d0,d0)
	assert round(corr[0],1) == 0.0 and round(corr[1],1) == 0.0, "Running cross-correlation on the same object should return an xshift and yshift that are essentially zero."


# NEXT TEST
# making fake data with NaNs and a stationary star
fake = np.zeros((50,50))
fake[10:14] = np.nan    # simulating row of masked out signal
fake[40:43,40:43] = 3   # stationary star

fake1 = np.zeros((50,50))
fake1[12:16] = np.nan   # simulating row of masked out signal
fake1[40:43,40:43] = 3   # stationary star
    
def test_NaNs_not_counted():
    corr = ir.cross_correlation_shifts(fake,fake1)
    assert round(corr[0],1) == 0.0 and round(corr[1],1) == 0.0, "Running cross-correlation on fake data with different rows of NaNs has no effect. NaNs should not have an impact."

    
# NEXT TEST
# making fake data with NaNs and a shifted star
fake2 = np.zeros((50,50))
fake2[10:14] = np.nan       # simulating row of masked out signal
fake2[40:43,40:43] = 3      # shifted star

fake3 = np.zeros((50,50))
fake3[10:14] = np.nan       # simulating row of masked out signal
fake3[38:41,35:38] = 3      # shifted star

def test_star_NaNs():
    corr = ir.cross_correlation_shifts(fake2,fake3)
    assert round(corr[0]) == -5 and round(corr[1]) == -2, "Running cross-correlation on fake data with same rows of NaNs and shifted star should have an effect. NaNs should not have an impact."