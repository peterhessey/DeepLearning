"""
Code for my solution to the SSA Deep Learning Coursework
"""


# imports 
import math
import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import matplotlib.pyplot as plt
from time import sleep

#set up cuda device
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

#class names for training and test datasets
class_names = ['airplane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

#tunable hyperparamters
BATCH_SIZE = 32
NUM_EPOCHS = 50
P_SWITCH = 1
DG_RATIO = 1
LABEL_SOFTNESS = 0.3
NORMALISE = False

#setting up custom dataset based on CIFAR10 but with only the necessary classes
class PegasusDataset(torchvision.datasets.CIFAR10):
    def __init__(self, root, train=True, transform=None, target_transform=None,
                 download=False):
        super().__init__(root, train, transform, target_transform, download)

        plane_label = 0
        bird_label = 2
        deer_label = 4
        horse_label = 7

        valid_classes = [plane_label, bird_label, deer_label, horse_label] # index of birds and horses

        pegasus_data = [self.data[i] for i in range(len(self.targets)) if self.targets[i] in valid_classes]

        # print(type(pegasus_data))
        pegasus_targets = [self.targets[i] for i in range(len(self.targets)) if self.targets[i] in valid_classes]

        self.data = pegasus_data
        self.targets = pegasus_targets


# define the generator model
class Generator(nn.Module):
    def __init__(self, f=64):
        super(Generator, self).__init__()
        self.generate = nn.Sequential(
            nn.ConvTranspose2d(100, f*8, 4, 2, 1, bias=False),
            nn.BatchNorm2d(f*8),
            nn.LeakyReLU(0.2, inplace=True),
            nn.ConvTranspose2d(f*8, f*4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(f*4),
            nn.LeakyReLU(0.2, inplace=True),
            nn.ConvTranspose2d(f*4, f*2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(f*2),
            nn.LeakyReLU(0.2, inplace=True),
            nn.ConvTranspose2d(f*2, f, 4, 2, 1, bias=False),
            nn.BatchNorm2d(f),
            nn.LeakyReLU(0.2, inplace=True),
            nn.ConvTranspose2d(f, 3, 4, 2, 1, bias=False),
            nn.Tanh()
        )

# define the discriminator model
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

# training dataset
train_set = PegasusDataset('data', train=True, download=True, transform=torchvision.transforms.Compose([
        torchvision.transforms.ToTensor()
    ]))

# testing dataset
test_set = PegasusDataset('data', train=False, download=True, transform=torchvision.transforms.Compose([
        torchvision.transforms.ToTensor()
    ]))

# dataloaders used for easier access to data for training
train_loader = torch.utils.data.DataLoader(train_set, shuffle=True, batch_size=BATCH_SIZE, drop_last=True)
test_loader = torch.utils.data.DataLoader(test_set, shuffle=True, batch_size=BATCH_SIZE, drop_last=True)

# create generator and discriminator
G = Generator().to(device)
D = Discriminator().to(device)

# initialise the optimiser
optimiser_G = torch.optim.Adam(G.parameters(), lr=0.0002, betas=(0.5,0.99))
optimiser_D = torch.optim.Adam(D.parameters(), lr=0.0002, betas=(0.5,0.99))
bce_loss = nn.BCELoss()

# arrays used to track loss over each epoch
gen_loss_per_epoch = []
dis_loss_per_epoch = []

# main training loop
for epoch in range(NUM_EPOCHS):
    
    # arrays for metrics
    gen_loss_arr = np.zeros(0)
    dis_loss_arr = np.zeros(0)

    dg_count = 0

    # probabilistic label switching
    switch_rand = random.random()

    # iterate over the training dataset
    for batch, targets in train_loader:

        batch, targets = batch.to(device), targets.to(device)

        # applying label softness
        real_label = torch.full((BATCH_SIZE, ), 1 * (1 - random.random() *LABEL_SOFTNESS), device=device)
        fake_label = torch.full((BATCH_SIZE, ), 1 * LABEL_SOFTNESS, device=device)

        # if switching labels
        if P_SWITCH > switch_rand:
            temp = real_label.clone().detach()
            real_label = fake_label.clone().detach()
            fake_label = temp

        # train discriminator 
        optimiser_D.zero_grad()

        # process all real batch first

        # calculate real loss
        l_r = bce_loss(D.discriminate(batch), real_label) # real -> 1
        # backpropogate
        l_r.backward()
        
        # process all fake batch
        g = G.generate(torch.randn(batch.size(0), 100, 1, 1).to(device))
        # calculate fake loss
        l_f = bce_loss(D.discriminate(g), fake_label) #  fake -> 0      
        # backpropogate
        l_f.backward()

        # step optimsier
        optimiser_D.step()

        # combined loss, useful for plotitng but not for training
        loss_d = (l_r + l_f) / 2
        dis_loss_arr = np.append(dis_loss_arr, loss_d.mean().item())

        #used for dg_ratio
        dg_count += 1
        
        #if trained discriminator enough
        if dg_count == DG_RATIO:
            # train generator
            optimiser_G.zero_grad()
            g = G.generate(torch.randn(batch.size(0), 100, 1, 1).to(device))

            loss_g = bce_loss(D.discriminate(g).view(-1), real_label) # fake -> 1

            loss_g.backward()
            optimiser_G.step()

            # append multiple to make plot easier to visualise
            for _ in range(DG_RATIO):
                gen_loss_arr = np.append(gen_loss_arr, loss_g.mean().item())

            dg_count = 0
            

    gen_loss_per_epoch.append(gen_loss_arr[len(gen_loss_arr) - 1])
    dis_loss_per_epoch.append(dis_loss_arr[len(dis_loss_arr) - 1])

    print('Training epoch %d complete' % epoch)


# display pegasus attempts

g = G.generate(torch.randn(BATCH_SIZE, 100, 1, 1).to(device))


plt.figure(figsize=(10,10))

# have to use multiple batches if wanting to display 64 images and batch size < 64
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
            g = G.generate(torch.randn(BATCH_SIZE, 100, 1, 1).to(device))
            

# save output
plt.savefig('./output/pegasus_e%sb%sd%sp%ss%s.png' % (str(NUM_EPOCHS),
                                                BATCH_SIZE, 
                                                str(DG_RATIO),
                                                str(P_SWITCH).replace('.', ''),
                                                str(LABEL_SOFTNESS).replace('.', '')))

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
plt.savefig('./output/loss_e%sb%sd%sp%ss%s.png' % (str(NUM_EPOCHS),
                                                BATCH_SIZE, 
                                                str(DG_RATIO),
                                                str(P_SWITCH).replace('.', ''),
                                                str(LABEL_SOFTNESS).replace('.', '')))

plt.cla()
plt.clf()

# plot loss data for final training cycle on each epoch

plt.plot(np.arange(len(gen_loss_per_epoch)), gen_loss_per_epoch, color='green', label='Generator loss')
plt.plot(np.arange(len(dis_loss_per_epoch)), dis_loss_per_epoch, color='red', label='Discriminator loss')
plt.title('Loss over all epochs')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(loc=2)
plt.savefig('./output/epoch_e%sb%sd%sp%ss%s.png' % (str(NUM_EPOCHS),
                                                BATCH_SIZE, 
                                                str(DG_RATIO),
                                                str(P_SWITCH).replace('.', ''),
                                                str(LABEL_SOFTNESS).replace('.', '')))