import numpy as np

def activity(indata):
    resamp_data = []
    data_length = int(np.floor(len(indata) / 10))
    for i in xrange(data_length):
        resamp_data.append(np.mean(indata[i*10:(i+1)*10]))
    resamp_data = np.subtract(resamp_data[1:-1], resamp_data[0:-2])
    return np.mean(np.abs(resamp_data)) if len(resamp_data) > 0 else 0

