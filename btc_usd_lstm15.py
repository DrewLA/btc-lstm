# -*- coding: utf-8 -*-
"""btc_usd_lstm15.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1j58Cj7_4dF47M8scqwQh8yEMUVN_V5GT
"""

# Author: Andrew Lewis
# Description: This is an attempt to use an LSTM RNN to predict the next 4 BTC
#              15 minute candle stick closes using training data from the last 460
#              closes as rolling features

# Import dependencies
!pip install python-binance
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from binance.client import Client

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import Dense, LSTM
plt.style.use('fivethirtyeight')
from matplotlib.dates import DateFormatter

import matplotlib.dates as mdates

import math
import tensorflow.keras as k
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import Dense, LSTM

# Initialize data feed client

client = Client()
# btc_usd = client.get_recent_trades(symbol="BTCUSDT")
candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_15MINUTE)

# Load data

data = pd.DataFrame().from_records(candles)
data.rename({0: 'time', 1 : 'open', 2 : 'high', 3: 'low', 4: 'close'}, axis=1, inplace=True)

data['date'] = pd.to_datetime(data['time'],unit='ms')
data['close'] = pd.to_numeric(data['close'])
data['high'] = pd.to_numeric(data['high'])
data['low'] = pd.to_numeric(data['low'])
data.set_index('date', inplace=True)
data.index = data.index.tz_localize('UTC').tz_convert('US/Eastern')
data

# Visualize data closing price history


fig, ax = plt.subplots()
myFmt = DateFormatter("%D %H %M %S")
ax.plot(data['close'])
ax.plot(data['high'])
ax.plot(data['low'])
ax.set_title('BTC 15 minute closing Price History')
# plt.plot(data['close'])
ax.set_xlabel('time', fontsize = 14)
ax.set_ylabel('Price $USD', fontsize=17)
ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=240))
ax.xaxis.set_major_formatter(myFmt)

## Rotate date labels automatically
fig.autofmt_xdate()
fig.set_size_inches(25,10)
plt.show()

# Filter to get just the close price dataframe
closeDf = data.filter(['close'])
highDf = data.filter(['high'])
lowDf = data.filter(['low'])

# convert the dataframe to a numpy array
dataset = closeDf.values
datahigh = highDf.values
datalow = lowDf.values
# get training data length: 90% of data
training_data_len = math.ceil(len(dataset) * .99)

# Preprocess data by scaling
scaler = MinMaxScaler(feature_range=(0,1))

scaled_data = scaler.fit_transform(dataset)
scaled_high_data = scaler.fit_transform(highDf)
scaled_low_data = scaler.fit_transform(lowDf)
scaled_data.shape

# split training data from scaled dataset
train_data = scaled_data[0:training_data_len]
train_high_data = scaled_high_data[0:training_data_len]
train_low_data = scaled_low_data[0:training_data_len]

# split features on 40 15 minute price closes where features are 15 minute 
# rolling values across 40 intervals and predictions are the next value after each window

x_train = []
y_train = []

for i in range(40, training_data_len):
    x_train.append((train_data[i-40:i]))#, train_high_data[i-40:i], train_low_data[i-40:i]))
    y_train.append(train_data[i])

# Convert the x and y train values into numpy arrays
x_train, y_train = np.array(x_train), np.array(y_train)

x_train.shape

# x_train = np.reshape(x_train, newshape=(x_train.shape[0], x_train.shape[2], x_train.shape[1]))

# x_train.shape

# Build model layers
model = k.Sequential()
layer1 = k.layers.LSTM(40, return_sequences=True, input_shape=(40, 1))
model.add(layer=layer1)
layer2 = k.layers.LSTM(40, return_sequences=False, input_shape=(40, 1))
model.add(layer=layer2)
model.add(k.layers.Dense(10))
# model.add(k.layers.Dense(5))
model.add(k.layers.Dense(1))

# Compile model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train model
model.fit(x_train, y_train, batch_size=1, epochs=2)

# Create testing dataset for x_train and y_train
test_data = scaled_data[training_data_len - 40:]
test_high_data = scaled_high_data[training_data_len - 40:]
test_low_data = scaled_low_data[training_data_len - 40:]
x_test = []
y_test = dataset[training_data_len : ]

for i in range(40 , len(test_data)):
  x_test.append((test_data[i - 40 : i])) #,test_high_data[i - 40 : i],test_low_data[i - 40 : i]))

# convert x_test to numpy array
x_test = np.array(x_test)
x_test.shape

# x_test = np.reshape(x_test, newshape=(x_test.shape[0], x_test.shape[2], x_test.shape[1]))
# x_test.shape

# get predictions for x_test
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

validation = pd.DataFrame()
validation = closeDf[training_data_len:]
validation['predictions'] = predictions
validation['high'] = data.filter(['high'])[training_data_len:]
validation['low'] = data.filter(['low'])[training_data_len:]
validation.head

# get RMSE
rmse = np.sqrt(np.mean((predictions - y_test))**2)
rmse

# Print arbitrary predictions
print(predictions[3], predictions[4])
print(y_test[3], y_test[4])

closeDf[-5:]

# predict latest 15 close
predict = scaled_data[-40:]
predict = np.array(predict)
predict = np.reshape(predict, newshape=(1,40,1))

future = model.predict(predict)
future = scaler.inverse_transform(future)
print(future[0])