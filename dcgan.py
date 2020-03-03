# -*- coding: utf-8 -*-
"""simple-gan.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/gist/cwkx/74e33bc96f94f381bd15032d57e43786/simple-gan.ipynb
"""



"""**Main imports**"""

import math
import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import matplotlib.pyplot as plt
from time import sleep

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
class_names = ['airplane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

BATCH_SIZE = 64
NUM_EPOCHS = 25
P_SWITCH = 0.25
DG_RATIO = 1
LABEL_SOFTNESS = 0.3


class PegasusDataset(torchvision.datasets.CIFAR10):
    def __init__(self, root, train=True, transform=None, target_transform=None,
                 download=False):
        super().__init__(root, train, transform, target_transform, download)

        plane_label = 0
        bird_label = 2
        horse_label = 7

        valid_classes = [plane_label, bird_label, horse_label] # index of birds and horses

        pegasus_data = [self.data[i] for i in range(len(self.targets)) if self.targets[i] in valid_classes]
        pegasus_targets = [self.targets[i] for i in range(len(self.targets)) if self.targets[i] in valid_classes]

        self.data = pegasus_data
        self.targets = pegasus_targets


# define the model
class Generator(nn.Module):
    def __init__(self, f=64):
        super(Generator, self).__init__()
        self.generate = nn.Sequential(
            nn.ConvTranspose2d(100, f*8, 4, 2, 1, bias=False),
            nn.BatchNorm2d(64*8),
            nn.ReLU(True),
            nn.ConvTranspose2d(f*8, f*4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(f*4),
            nn.ReLU(True),
            nn.ConvTranspose2d(f*4, f*2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(f*2),
            nn.ReLU(True),
            nn.ConvTranspose2d(f*2, f, 4, 2, 1, bias=False),
            nn.BatchNorm2d(f),
            nn.ReLU(True),
            nn.ConvTranspose2d(f, 3, 4, 2, 1, bias=False),
            nn.Tanh()
        )


class Discriminator(nn.Module):
    def __init__(self, f=64):
        super(Discriminator, self).__init__()
        self.discriminate = nn.Sequential(
            nn.Conv2d(3, f, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(f, f*2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(f*2),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(f*2, f*4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(f*4),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(f*4, f*8, 4, 2, 1, bias=False),
            nn.BatchNorm2d(f*8),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(f*8, 1, 4, 2, 1, bias=False),
            nn.Sigmoid()
        )


train_set = PegasusDataset('data', train=True, download=True, transform=torchvision.transforms.Compose([
        torchvision.transforms.ToTensor()
    ]))

test_set = PegasusDataset('data', train=False, download=True, transform=torchvision.transforms.Compose([
        torchvision.transforms.ToTensor()
    ]))

train_loader = torch.utils.data.DataLoader(train_set, shuffle=True, batch_size=BATCH_SIZE, drop_last=True)
test_loader = torch.utils.data.DataLoader(test_set, shuffle=True, batch_size=BATCH_SIZE, drop_last=True)


'''Used to view example data in dataset'''
# plt.figure(figsize=(10,10))
# for i in range(25):
#     plt.subplot(5,5,i+1)
#     plt.xticks([])
#     plt.yticks([])
#     plt.grid(False)
#     plt.imshow(test_loader.dataset[i][0].permute(0,2,1).contiguous().permute(2,1,0), cmap=plt.cm.binary)
#     plt.xlabel(class_names[test_loader.dataset[i][1]])


G = Generator().to(device)
D = Discriminator().to(device)


# initialise the optimiser
optimiser_G = torch.optim.Adam(G.parameters(), lr=0.0002, betas=(0.5,0.99))
optimiser_D = torch.optim.Adam(D.parameters(), lr=0.0002, betas=(0.5,0.99))
bce_loss = nn.BCELoss()

gen_loss_per_epoch = []
dis_loss_per_epoch = []
# # training loop
for epoch in range(NUM_EPOCHS):
    
    # arrays for metrics
    logs = {}
    gen_loss_arr = np.zeros(0)
    dis_loss_arr = np.zeros(0)

    dg_count = 0

    # iterate over the training dataset
    for batch, targets in train_loader:

        batch, targets = batch.to(device), targets.to(device)

        # train discriminator 
        optimiser_D.zero_grad()
        g = G.generate(torch.randn(batch.size(0), 100, 1, 1).to(device))
        l_r = bce_loss(D.discriminate(batch).mean(), torch.ones(1)[0].to(device)) # real -> 1
        l_f = bce_loss(D.discriminate(g.detach()).mean(), torch.zeros(1)[0].to(device)) #  fake -> 0
        loss_d = (l_r + l_f)/2.0
        loss_d.backward()
        optimiser_D.step()

        dis_loss_arr = np.append(dis_loss_arr, loss_d.item())

        #used for dg_ratio
        dg_count += 1
        
        #if trained discriminator enough
        if dg_count == DG_RATIO:
            # train generator
            optimiser_G.zero_grad()
            g = G.generate(torch.randn(batch.size(0), 100, 1, 1).to(device))
            
            
            # probabilistic label switching
            switch_rand = random.random()

            if P_SWITCH < switch_rand:

                soft_upper_tensor = torch.ones(1) - torch.randn(1) * LABEL_SOFTNESS
                loss_g = bce_loss(D.discriminate(g).mean(), soft_upper_tensor[0].to(device)) # fake -> 1
            
            else:
                soft_lower_tensor = torch.randn(1) * LABEL_SOFTNESS
                loss_g = bce_loss(D.discriminate(g).mean(), soft_lower_tensor[0].to(device)) # fake -> 0

            loss_g.backward()
            optimiser_G.step()

            # append multiple to make plot easier to visualise
            for _ in range(DG_RATIO):
                gen_loss_arr = np.append(gen_loss_arr, loss_g.item())

            dg_count = 0
            

    gen_loss_per_epoch.append(gen_loss_arr[len(gen_loss_arr) - 1])
    dis_loss_per_epoch.append(dis_loss_arr[len(dis_loss_arr) - 1])

    print('Training epoch %d complete' % epoch)


# display pegasus attempts

g = G.generate(torch.randn(BATCH_SIZE, 100, 1, 1).to(device))

plt.figure(figsize=(10,10))

if BATCH_SIZE >= 64:
    for i in range(64):
        plt.subplot(8,8,i+1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        plt.imshow(g[i].cpu().data.permute(0,2,1).contiguous().permute(2,1,0), cmap=plt.cm.binary)

else:
    num_images_displayed = 0
    batch_num = 0
    while num_images_displayed < 64:
        plt.subplot(8,8,num_images_displayed+1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        plt.imshow(g[batch_num].cpu().data.permute(0,2,1).contiguous().permute(2,1,0), cmap=plt.cm.binary)

        num_images_displayed += 1
        batch_num += 1

        if batch_num >= BATCH_SIZE:
            batch_num = 0
            g = G.generate(torch.randn(x.size(0), 100, 1, 1).to(device))

# save output
plt.savefig('./output/pegasus_p025soft.png')

# clear figures
plt.cla()
plt.clf()

# plot loss data for final epoch

plt.plot(np.arange(len(gen_loss_arr)), gen_loss_arr, color='green', label='Generator loss')
plt.plot(np.arange(len(dis_loss_arr)), dis_loss_arr, color='red', label='Discriminator loss')
plt.title('Loss in final epoch')
plt.ylabel('Loss')
plt.xlabel('Training iteration')
plt.legend(loc=2)
plt.savefig('./output_p025soft.png')

plt.cla()
plt.clf()

# plot loss data for final training cycle on each epoch

plt.plot(np.arange(len(gen_loss_per_epoch)), gen_loss_per_epoch, color='green', label='Generator loss')
plt.plot(np.arange(len(dis_loss_per_epoch)), dis_loss_per_epoch, color='red', label='Discriminator loss')
plt.title('Loss over all epochs')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(loc=2)
plt.savefig('./output/epoch_p025soft.png')