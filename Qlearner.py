
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
"""
This code is copy of creater 'Python Engineer' from youtube. I thank him to teach us this project! 

"""

class Linear_Q(nn.Module):
    #Defining the model
    def __init__(self, input_length, hidden_length, output_length):
        super().__init__()
        self.linear1 = nn.Linear(input_length, hidden_length)
        self.linear2 = nn.Linear(hidden_length, output_length)

    #Defining the forward of deep learninh
    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr #Learning rate for Gradient
        self.gamma = gamma #Gamma value
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr) #Adam optimizer for the model
        self.criterion = nn.MSELoss() #Mean Square Error

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)


        if len(state.shape) == 1:
            #Adding new direction
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        # 1: predicted Q values with current state
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new

        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        # pred.clone()
        # preds[argmax(action)] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()
