# How to train a GAN
Notes on [this](https://www.youtube.com/watch?time_continue=8&v=X1mUN6dD8uE&feature=emb_logo) video

## Stability
- They're difficult to validate
- Visual inspection is used to evaluate whether or not GAN is making good quality output

## DCGANs Radford et. al.
- Much more stable GAN architectures, getting reasonable samples from their favourite image dataset
- **Salimans et. al.** improved techinques for training GANs (*could be a good paper to read!*)

## Tricks

### 1. Normalise the inputs
- Normalise images between -1 and 1
- Tanh as the last layer of the generator output

### 2. Modified loss function
- Maximise log(D) rather than min(log(1-d))
- In practice when training discriminator, keep labels as is, but on generator you can flip those target labels **IMPORTANT**

### 3. Use sperhical z
- Sample new images from sphere rather than cube latent space
- *Will need to look into this more*

### 4. Using BatchNorm properly
- When trianing D, don't mix samples only give batch of real or fake one at a time (*i think I'm already doing this but check*)
  
### 5. Avoid sparse gradients
- Avoid ReLU, MaxPool
- LeakyReLU (both G and D) *this is new*
- sparse gradients are not as nice for generative models as for discriminative models

### 6. Soft and Noisy labels
- Label smoothing: rather than using 0 for fake and 1 for real, soften them to a stochastic value (0 to 0.3 and 0.7 to 1 for example)
- Noisy labels: with some probability p, flip the labels 

### 7. DCGANs/Hybrid models
- If in image domain use DCGAN if you can

### 8. Stability tricks from RL
- Experience replay can help in stabilising GANs
  - Keep past generations and occasionally show them to discriminator

### 9. Optimisers: ADAM
- ADAM is the most optimal and stable for GANs
- lr of 0.0002, tweak beta1 and beta2
- Potnetially SGD for discriminator and ADAM for generator

### 10. Track failures early
- If your GAN is not working you want to know that early
- If loss of generator steadily decreases then its fooling D with garbage, should be too steady

### 11. Don't balance via loss statistics
- Don't try and alternate training for equilibrium 
- These heuristics don't work unless you have some sort of solid theoretical backing

### 12. If you have labels, use them
- Can also train the discriminator to classify samples
  - This is where conditional GANs come in

### 13. Add noise to inputs, decay over time
- Add artificial noise to inputs D, decay the amount of noise you add over time
- **Zhao et.al. EBGAN** adding noise to each layer of generator

### 14. Train the discriminator more (sometimes)
- If you have a lot of noise, for every iteration of training the generator, train the discriminator k times

### 15. Batch Discrimination
- Insetad of classifyying a single sample as real or fake, one classifies a whole batch as real or fake
- Actual implementation is a little  more complex
  - In the OpenAI techniques paper, *mixed results*

## Questions
- When discriminator is happy it collapses to 0.5
- 