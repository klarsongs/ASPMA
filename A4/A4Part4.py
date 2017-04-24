import os
import sys
import numpy as np
from scipy.signal import get_window
import matplotlib.pyplot as plt
import math

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../software/models/'))
import stft
import utilFunctions as UF

from A4Part3 import compute_eng_env


eps = np.finfo(float).eps

"""
A4-Part-4: Computing onset detection function (Optional)

Write a function to compute a simple onset detection function (ODF) using the STFT. Compute two ODFs 
one for each of the frequency bands, low and high. The low frequency band is the set of all the 
frequencies between 0 and 3000 Hz and the high frequency band is the set of all the frequencies 
between 3000 and 10000 Hz (excluding the boundary frequencies in both the cases). 

A brief description of the onset detection function can be found in the pdf document (A4-STFT.pdf, 
in Relevant Concepts section) in the assignment directory (A4). Start with an initial condition of 
ODF(0) = 0 in order to make the length of the ODF same as that of the energy envelope. Remember to 
apply a half wave rectification on the ODF. 

The input arguments to the function are the wav file name including the path (inputFile), window 
type (window), window length (M), FFT size (N), and hop size (H). The function should return a numpy 
array with two columns, where the first column is the ODF computed on the low frequency band and the 
second column is the ODF computed on the high frequency band.

Use stft.stftAnal() to obtain the STFT magnitude spectrum for all the audio frames. Then compute two 
energy values for each frequency band specified. While calculating frequency bins for each frequency 
band, consider only the bins that are within the specified frequency range. For example, for the low 
frequency band consider only the bins with frequency > 0 Hz and < 3000 Hz (you can use np.where() to 
find those bin indexes). This way we also remove the DC offset in the signal in energy envelope 
computation. The frequency corresponding to the bin index k can be computed as k*fs/N, where fs is 
the sampling rate of the signal.

To get a better understanding of the energy envelope and its characteristics you can plot the envelopes 
together with the spectrogram of the signal. You can use matplotlib plotting library for this purpose. 
To visualize the spectrogram of a signal, a good option is to use colormesh. You can reuse the code in
sms-tools/lectures/4-STFT/plots-code/spectrogram.py. Either overlay the envelopes on the spectrogram 
or plot them in a different subplot. Make sure you use the same range of the x-axis for both the 
spectrogram and the energy envelopes.

NOTE: Running these test cases might take a few seconds depending on your hardware.

Test case 1: Use piano.wav file with window = 'blackman', M = 513, N = 1024 and H = 128 as input. 
The bin indexes of the low frequency band span from 1 to 69 (69 samples) and of the high frequency 
band span from 70 to 232 (163 samples). To numerically compare your output, use loadTestCases.py
script to obtain the expected output.

Test case 2: Use piano.wav file with window = 'blackman', M = 2047, N = 4096 and H = 128 as input. 
The bin indexes of the low frequency band span from 1 to 278 (278 samples) and of the high frequency 
band span from 279 to 928 (650 samples). To numerically compare your output, use loadTestCases.py
script to obtain the expected output.

Test case 3: Use sax-phrase-short.wav file with window = 'hamming', M = 513, N = 2048 and H = 256 as 
input. The bin indexes of the low frequency band span from 1 to 139 (139 samples) and of the high 
frequency band span from 140 to 464 (325 samples). To numerically compare your output, use 
loadTestCases.py script to obtain the expected output.

In addition to comparing results with the expected output, you can also plot your output for these 
test cases. For test case 1, you can clearly see that the ODFs have sharp peaks at the onset of the 
piano notes (See figure in the accompanying pdf). You will notice exactly 6 peaks that are above 
10 dB value in the ODF computed on the high frequency band. 
"""

def computeODF(inputFile, window, M, N, H):
    """
    Inputs:
            inputFile (string): input sound file (monophonic with sampling rate of 44100)
            window (string): analysis window type (choice of rectangular, triangular, hanning, hamming, 
                blackman, blackmanharris)
            M (integer): analysis window size (odd integer value)
            N (integer): fft size (power of two, bigger or equal than than M)
            H (integer): hop size for the STFT computation
    Output:
            The function should return a numpy array with two columns, where the first column is the ODF 
            computed on the low frequency band and the second column is the ODF computed on the high 
            frequency band.
            ODF[:,0]: ODF computed in band 0 < f < 3000 Hz 
            ODF[:,1]: ODF computed in band 3000 < f < 10000 Hz
    """
    
    fs, mX, env = compute_eng_env(inputFile, window, M, N, H)

    num_frames = env.shape[0]
    odf = np.zeros(shape=(num_frames, 2))

    for frame in range(1, num_frames):
        odf[frame, 0] = rectify(env[frame, 0] - env[frame - 1, 0])
        odf[frame, 1] = rectify(env[frame, 1] - env[frame - 1, 1])

    plot_spectrogram_with_odf(mX, odf, M, N, H, fs, 'mX ({}), M={}, N={}, H={}'.format(inputFile, M, N, H))

    return odf


def plot_spectrogram_with_odf(mX, odf, M, N, H, fs, title):
    assert mX.shape[0] == odf.shape[0]
    num_frames = mX.shape[0]

    frmTime = H * np.arange(num_frames) / float(fs)
    binFreq = np.arange(N / 2 + 1) * float(fs) / N

    # plt.suptitle(title)
    #
    # plt.subplot(2, 1, 1)
    # plt.title("Spectrogram")
    # plt.pcolormesh(frmTime, binFreq, np.transpose(mX), cmap='jet')
    # plt.autoscale(tight=True)
    # plt.ylim([0, 10000])
    # # plt.xlabel("Time (sec)")
    # plt.ylabel("Frequency (Hz)")

    plt.subplot(3, 1, 3)
    plt.title("Onset Detection Function")
    plt.plot(frmTime, odf[:, 0], 'b', label='Low')
    plt.plot(frmTime, odf[:, 1], 'g', label='High')
    plt.xlabel("Time (sec)")
    plt.ylabel("Magnitude (dB)")
    plt.legend(loc='best')

    # plt.subplots_adjust(hspace=0.5)


def rectify(x):
    return x if x > 0 else 0


def get_test_case(part_id, case_id):
    import loadTestCases
    testcase = loadTestCases.load(part_id, case_id)
    return testcase


def test_case_1():
    testcase = get_test_case(4, 1)
    odf = computeODF(**testcase['input'])
    #plt.show()
    assert np.allclose(testcase['output'], odf, atol=1e-6, rtol=0)


def test_case_2():
    testcase = get_test_case(4, 2)
    odf = computeODF(**testcase['input'])
    #plt.show()
    assert np.allclose(testcase['output'], odf, atol=1e-6, rtol=0)


def test_case_3():
    testcase = get_test_case(4, 3)
    odf = computeODF(**testcase['input'])
    #plt.show()
    assert np.allclose(testcase['output'], odf, atol=1e-6, rtol=0)
