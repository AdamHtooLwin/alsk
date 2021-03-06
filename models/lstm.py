import torch
import torch.nn as nn


class EEGLSTM_V3(nn.Module):
    def __init__(self, hidden_size1, hidden_size2, hidden_size3, batch_size, channels):
        super(EEGLSTM_V3, self).__init__()

        self.hidden_size1 = hidden_size1  # 64
        self.hidden_size2 = hidden_size2  # 32
        self.hidden_size3 = hidden_size3  # 32
        self.batch_size = batch_size
        self.channels = channels

        self.conv = nn.Conv1d(self.channels, int(self.channels/2), kernel_size=1)

        self.lstm1 = nn.LSTM(int(self.channels/2), self.hidden_size1, batch_first=True)
        self.dropout = nn.Dropout(p=0.2)
        self.lstm2 = nn.LSTM(self.hidden_size1, self.hidden_size2, batch_first=True)
        self.lstm3 = nn.LSTM(self.hidden_size2, self.hidden_size3, batch_first=True)

        self.relu = nn.ReLU()

        # self.fc = nn.Linear(8064 * self.hidden_size2, 4) # It should
        self.fc = nn.Linear(self.hidden_size2, 2)

    # Do 1 cnn dimensional << Let's try
    # increase number of layer

    def forward(self, x, hidden):
        x = self.conv(x)

        x = torch.transpose(x, 1, 2)

        # Input Size (1, 8064, 40), Hidden/Cell Size (1, 1, hidden_size1) (1 eeg sequence for 1 video)
        x, _ = self.lstm1(x, (hidden[0], hidden[1]))  # Mem_inc [1st: 500MB]
        x = self.dropout(x)

        # (1, 8064, hidden_size1), (1, 1, hidden_size2)
        x, _ = self.lstm2(x, (hidden[2], hidden[3]))  # Mem_inc [1st: 200MB, 2nd: 200MB]
        x = self.dropout(x)

        #
        x, _ = self.lstm3(x, (hidden[4], hidden[5]))
        x = self.dropout(x)

        x = self.fc(x)
        output = self.relu(x)

        return output  # , next_hidden

    def initHidden(self):
        return [torch.zeros(1, self.batch_size, self.hidden_size1), torch.zeros(1, self.batch_size, self.hidden_size1),
                torch.zeros(1, self.batch_size, self.hidden_size2), torch.zeros(1, self.batch_size, self.hidden_size2),
                torch.zeros(1, self.batch_size, self.hidden_size3), torch.zeros(1, self.batch_size, self.hidden_size3)]



class EEGLSTM_V2(nn.Module):
    def __init__(self, hidden_size1, hidden_size2, hidden_size3, batch_size):
        super(EEGLSTM_V2, self).__init__()

        self.hidden_size1 = hidden_size1  # 64
        self.hidden_size2 = hidden_size2  # 32
        self.hidden_size3 = hidden_size3  # 32
        self.batch_size = batch_size

        self.lstm1 = nn.LSTM(32, self.hidden_size1, batch_first=True)
        self.dropout = nn.Dropout(p=0.2)
        self.lstm2 = nn.LSTM(self.hidden_size1, self.hidden_size2, batch_first=True)
        self.lstm3 = nn.LSTM(self.hidden_size2, self.hidden_size3, batch_first=True)

        self.relu = nn.ReLU()

        # self.fc = nn.Linear(8064 * self.hidden_size2, 4) # It should
        self.fc = nn.Linear(self.hidden_size2, 2)

    # Do 1 cnn dimensional << Let's try
    # increase number of layer

    def forward(self, x, hidden):
        x = torch.transpose(x, 1, 2)
        # Input Size (1, 8064, 40), Hidden/Cell Size (1, 1, hidden_size1) (1 eeg sequence for 1 video)
        x, _ = self.lstm1(x, (hidden[0], hidden[1]))  # Mem_inc [1st: 500MB]
        x = self.dropout(x)

        # (1, 8064, hidden_size1), (1, 1, hidden_size2)
        x, _ = self.lstm2(x, (hidden[2], hidden[3]))  # Mem_inc [1st: 200MB, 2nd: 200MB]
        x = self.dropout(x)

        #
        x, _ = self.lstm3(x, (hidden[4], hidden[5]))
        x = self.dropout(x)

        x = self.fc(x)
        output = self.relu(x)
        return output  # , next_hidden

    def initHidden(self):
        return [torch.zeros(1, self.batch_size, self.hidden_size1), torch.zeros(1, self.batch_size, self.hidden_size1),
                torch.zeros(1, self.batch_size, self.hidden_size2), torch.zeros(1, self.batch_size, self.hidden_size2),
                torch.zeros(1, self.batch_size, self.hidden_size3), torch.zeros(1, self.batch_size, self.hidden_size3)]


class EEGLSTM(nn.Module):
    def __init__(self, input_size, hidden_size1, hidden_size2, batch_size):
        super(EEGLSTM, self).__init__()

        self.hidden_size1 = hidden_size1  # 64
        self.hidden_size2 = hidden_size2  # 32
        self.batch_size = batch_size
        self.input_size = input_size

        self.lstm1 = nn.LSTM(self.input_size, self.hidden_size1, batch_first=True)
        # Put dropout here later :D
        self.dropout = nn.Dropout(p=0.2)
        self.lstm2 = nn.LSTM(self.hidden_size1, self.hidden_size2, batch_first=True)

        self.relu = nn.ReLU()
        self.fc = nn.Linear(self.hidden_size2, 2)

    def forward(self, x, hidden):
        x = torch.transpose(x, 1, 2)

        # Input Size (1, 8064, 40), Hidden/Cell Size (1, 1, hidden_size1) (1 eeg sequence for 1 video)
        x, _ = self.lstm1(x, (hidden[0], hidden[1]))
        x = self.dropout(x)
        # (1, 8064, hidden_size1), (1, 1, hidden_size2)
        x, _ = self.lstm2(x, (hidden[2], hidden[3]))
        # may be we add dropout here?
        x = self.fc(x)
        output = self.relu(x)
        return output

    def initHidden(self):
        return [torch.zeros(1, self.batch_size, self.hidden_size1), torch.zeros(1, self.batch_size, self.hidden_size1),
                torch.zeros(1, self.batch_size, self.hidden_size2), torch.zeros(1, self.batch_size, self.hidden_size2)]

class MiniLSTM(nn.Module):
    """
    Based off V2.
    """
    def __init__(self, hidden_size1, batch_size):
        super(MiniLSTM, self).__init__()

        self.hidden_size1 = hidden_size1  # 64
        self.batch_size = batch_size

        self.lstm1 = nn.LSTM(32, self.hidden_size1, batch_first=True)

        self.relu = nn.ReLU()

        # self.fc = nn.Linear(8064 * self.hidden_size2, 4) # It should
        self.fc = nn.Linear(self.hidden_size1, 2)

    # Do 1 cnn dimensional << Let's try
    # increase number of layer

    def forward(self, x, hidden):
        x = torch.transpose(x, 1, 2)
        # Input Size (1, 8064, 40), Hidden/Cell Size (1, 1, hidden_size1) (1 eeg sequence for 1 video)
        x, _ = self.lstm1(x, (hidden[0], hidden[1]))  # Mem_inc [1st: 500MB]

        x = self.fc(x)
        output = self.relu(x)
        return output  # , next_hidden

    def initHidden(self):
        return [torch.zeros(1, self.batch_size, self.hidden_size1), torch.zeros(1, self.batch_size, self.hidden_size1)]

