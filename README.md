# DeepLearning
Deep Learning Coursework for software, systems and applications 3rd year module

## Objective 
- Using the CIFAR-10 dataset, create a NN model capable of generating an image of a pegasus
- An intentionally ill-defined learning problem; the generative model needs to use what it learns about birds and horses in order to produce the pegasus image

## To-Do
- [x] Lecture catchup (especially lecture 4)
- [x] Research generative architectures, produce list of papers / interesting articles etc.
- [ ] Select a generative model to use
- [ ] Build and train model
- [ ] Generate pegasus image
- [ ] Tweak and refine hyperparameters etc., keep track of results and details of improvements
- [ ] Write report
  - [ ] Diagram of model, dicussions on its design **(40 marks)**
  - [ ] Include best output **(40 marks)** 
  - [ ] Include batch of 64 images **(20 marks)**

## Notes
### Lecture 3 Catchup 
- Variety of potential architectures explained in lecture 3
  - GANs look promising
- Batch normalisation explained [here](https://deeplizard.com/learn/video/dXB-KQYkzNU)

### Lecture 4 Catchup
- Generative models are effectively the reverse of classifcation models, i.e. *P(X|Y=y)* instead of *P(Y|X=x)*
- KDE explained nicely [here](https://mathisonian.github.io/kde/)
- Lots of useful statisitcal definitions, may be worth coming back to when reading papers in the future
- Dicsussion of loss functions
  - Generally a good idea to simply use L_2 as it is convenient, simple and computationally inexpensive
- GANs (Generative adversarial networks) use a game-theoretic approach to the generative problem, by competing two models against one another:
  - Discriminator, D, which estimates the probability of a given sample coming from the real dataset or being a generated sample
  - A generator, G, that learns to map noise drawn from some prior distribution (often Gaussian) to generated examples that capture p_data
  - This creates a two-player minimax game, where one player is trying to minimize G and the other is trying to maximise D. When they reach a Nash equilibrium this is when the GAN model converges.


### Lecture 5 Catchup - GANs and ACAIs
- GANs are notoriously difficult to train, they often demonstrate extreme instability
- ACAIs have a strong potential of being very useful, more detailed explanation on them can be found [here](https://www.kdnuggets.com/2019/03/interpolation-autoencoders-adversarial-regularizer.html)


## ACAIs
- ACAI paper [here](https://arxiv.org/pdf/1807.07543.pdf)
- ACAI paper notes [here](https://www.kdnuggets.com/2019/03/interpolation-autoencoders-adversarial-regularizer.html)
- ACAI implementation in tensorflow can be found [here](https://github.com/brain-research/acai)

## GANs

### Training tips
- [How to train a GAN Facebook AI](https://www.youtube.com/watch?time_continue=8&v=X1mUN6dD8uE&feature=emb_logo)
- [GAN architectures for beginners](https://sigmoidal.io/beginners-review-of-gan-architectures/)
- [More on GAN architectures](https://julianzaidi.wordpress.com/2017/04/24/deep-convolution-gan-dcgan-architecture-and-training/)
  
### DCGANs
- Paper on Deep Convolutional Generative Adversarial Networks [here](https://arxiv.org/pdf/1511.06434.pdf)
- Architecture guidelines:
  - Replace pooling layers with strided convolutions (discriminator) and fractional-strided convolutions (generator)
  - Use batch normalisation in both the generator and discriminator
  - Remove fully connected hidden layers for deeper architectures
  - Use ReLU activation in the generator for all layers except for the output, which uses Tanh
  - Use LeakyReLU activation in the discriminator

### Conditional GANs
- Paper on conditional GANs can be found [here](https://arxiv.org/pdf/1411.1784.pdf)

### Normalisation techniques
- Spectral normalisation increases training stability, paper on it [here](https://arxiv.org/pdf/1802.05957.pdf)
  - Code [here](https://github.com/pfnet-research/sngan_projection/blob/master/requirements.txt)
  
### WGANs 
- WGAN paper found [here](https://arxiv.org/pdf/1701.07875.pdf)
- 
  