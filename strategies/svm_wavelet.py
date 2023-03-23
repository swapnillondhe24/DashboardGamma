
import backtrader as bt
import pandas as pd
from sklearn.svm import SVR
import pywt


class svm_wavelet(bt.Strategy):
    params = (('period', 10),
              ('num_periods', 3),
              ('svm_kernel', 'rbf'),
              ('svm_c', 1.0),
              ('svm_epsilon', 0.1))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.svm_model = None
        self.wavelet_coeffs = None
        self.predicted_values = []
        self.predicted_index = 0

    def next(self):
        if len(self) % self.params.period == 0:
            self.wavelet_coeffs = pywt.wavedec(self.dataclose.get(ago=0, size=self.params.period), 'db1', level=self.params.num_periods)

            input_features = []
            for coeff in self.wavelet_coeffs:
                input_features += coeff.tolist()

            if self.svm_model is None:
                self.svm_model = SVR(kernel=self.params.svm_kernel, C=self.params.svm_c, epsilon=self.params.svm_epsilon)
                X = pd.DataFrame(input_features).transpose()
                y = self.dataclose.get(ago=0, size=self.params.period).tolist()
                self.svm_model.fit(X, y)
            else:
                input_features.append(self.predicted_values[-1])
                X = pd.DataFrame(input_features).transpose()
                predicted_value = self.svm_model.predict(X)
                self.predicted_values.append(predicted_value[0])
                self.predicted_index = len(self.predicted_values) - 1

    def buy_signal(self):
        if self.predicted_index == len(self.predicted_values) - 1:
            return self.dataclose[0] < self.predicted_values[-1] and self.dataclose[1] > self.predicted_values[-2]
        return False

    def sell_signal(self):
        if self.predicted_index == len(self.predicted_values) - 1:
            return self.dataclose[0] > self.predicted_values[-1] and self.dataclose[1] < self.predicted_values[-2]
        return False
    
class SVMWaveletBacktest(bt.Strategy):
    def __init__(self):
        self.strategy = svm_wavelet(self.params.period, self.params.num_periods, self.params.svm_kernel, self.params.svm_c, self.params.svm_epsilon)

    def next(self):
        if self.strategy.buy_signal():
            self.buy()
        elif self.strategy.sell_signal():
            self.sell()