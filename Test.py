import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# ==================================
# Define the form of the function
# ==================================
def model(x, A=190, k=1):
    return A * np.exp(-k*x/50)

# ==================================
# How many data points are generated
# ==================================
num_samples = 15

# ==================================
# Create data for plots
# ==================================
x_model = np.linspace(0, 130, 200)

x_data1 = np.random.rand(num_samples) * 130
x_data1.sort()

x_data2 = np.random.rand(num_samples) * 130
x_data2.sort()

data1 = model(x_data1, k=1) * (1 + np.random.randn(num_samples) * 0.2)
data2 = model(x_data2, k=2) * (1 + np.random.randn(num_samples) * 0.15)

model1 = model(x_model, k=1)
model2 = model(x_model, k=2)

# ==================================
# Plot everything normally
# ==================================
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x_data1, data1, 'ok', markerfacecolor='none', label='Data (k=1)')
ax.plot(x_data2, data2, 'sk', markeredgecolor='0.5', markerfacecolor='0.5', label='Data (k=2)')
ax.plot(x_model, model1, '-k', label='Model (k=1)')
ax.plot(x_model, model2, '--k', label='Model (k=2)')

# ==================================
# Format plot
# ==================================
ax.set_xlabel('Distance from heated face($10^{-2}$ m)')
ax.set_ylabel('Temperature ($^\circ$C)')
ax.set_xlim((0, 130))
ax.set_title('Normal way to plot')
ax.legend()
fig.tight_layout()

plt.show()


# ==================================
# ==================================
# Do it again, but with custom
# legend
# ==================================
# ==================================
class AnyObject(object):
    pass


class data_handler(object):
    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        scale = fontsize / 22
        x0, y0 = handlebox.xdescent, handlebox.ydescent
        width, height = handlebox.width, handlebox.height
        patch_sq = mpatches.Rectangle([x0, y0 + height/2 * (1 - scale) ], height * scale, height * scale, facecolor='0.5',
                edgecolor='0.5', transform=handlebox.get_transform())
        patch_circ = mpatches.Circle([x0 + width - height/2, y0 + height/2], height/2 * scale, facecolor='none',
                edgecolor='black', transform=handlebox.get_transform())

        handlebox.add_artist(patch_sq)
        handlebox.add_artist(patch_circ)
        return patch_sq

# ==================================
# Plot everything
# ==================================
fig = plt.figure()
ax = fig.add_subplot(111)
d1 = ax.plot(x_data1, data1, 'ok', markerfacecolor='none', label='Data (k=2)')
d2 = ax.plot(x_data2, data2, 'sk', markeredgecolor='0.5', markerfacecolor='0.5', label='Data (k=1)')
m1 = ax.plot(x_model, model1, '-k', label='Model (k=1)')
m2 = ax.plot(x_model, model2, '-k', label='Model (k=2)')

# ax.legend([d1], handler_map={ax.plot: data_handler()})
ax.legend([AnyObject(), m1[0]], ['Data', 'Model'], handler_map={AnyObject: data_handler()})

# ==================================
# Format plot
# ==================================
ax.set_xlabel('Distance from heated face($10^{-2}$ m)')
ax.set_ylabel('Temperature ($^\circ$C)')
ax.set_xlim((0, 130))
ax.set_title('Custom legend')
fig.tight_layout()

plt.show()



#Lowpass filter

    T = df[Time_s].iloc[-1] # sample period
    print(df[Time_s].iloc[-1])
    fs = 10 # sample rate, Hz
    cutoff = 20 # desired cutoff frequency, Hz
    nyq = 0.5 * fs # nyquist frequency
    order = 2 # order of sine wave approximation 
    n = int(T*fs)
    def butter_lowpass_filter(data, cutoff, fs, order):
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, 'lowpass', fs)
        y = filtfilt(b, a, data)
        return y

    data = df[Force_N]
    filteredData = butter_lowpass_filter(data, cutoff, fs, order)
    df[Force_N] = filteredData
    data = df[Globe_Disp_1_mm]
    filteredData = butter_lowpass_filter(data, cutoff, fs, order)
    df[Globe_Disp_1_mm] = filteredData