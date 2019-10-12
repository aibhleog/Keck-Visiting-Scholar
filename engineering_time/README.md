# Code used to analyze engineering data
You will want to make sure the `image_registration` package is installed in your working environment. Find the package and installation instructions [here](https://github.com/keflavich/image_registration). If you want to see how it works, check out `investigate_cross_correlation_shifts.ipynb` to see how I looked at different scenarios (using fake and real data) to make sure I understood how it worked.

In addition, to make sure the package was installed correctly, you can run 

```pytest test_cross_correlations.py```

in the terminal (make sure you're in the correct environment with the `image_registration` package).
