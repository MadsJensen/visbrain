"""
Interface customization
=======================

Use custom color, font size...

.. image:: ../../picture/picsignal/ex_custom_interface.png
"""
from visbrain import Signal
from visbrain.utils import generate_eeg

sf = 512.  # sampling frequency
n_pts = 4000  # number of time points
n_trials = 125  # number of trials in the dataset

"""Generate a random EEG vector of shape (n_trials, n_pts). This time, we
smooth signals and decrease the noise on it.
"""
data, _ = generate_eeg(sf=sf, n_pts=n_pts, n_trials=n_trials, smooth=200,
                       noise=1000)

"""Define a dictionary with interface customization entries
"""
kwargs = {'xlabel': 'xlabel', 'ylabel': 'ylabel', 'title': 'title',
          'color': 'lightgray', 'symbol': 'x', 'title_font_size': 20,
          'axis_font_size': 18, 'tick_font_size': 8, 'axis_color': 'white',
          'bgcolor': (.1, .1, .1), 'form': 'marker'}

Signal(data, sf=sf, axis=-1, **kwargs).show()