# Strucutre for DL Report

## Need to include
- Architecture diagram
- Architecture description and design choices
- Testing and evaluation methods and results
- Potential improvements
- Chosen pegasus
- 8x8 sample of output

## Architecture diagram
- DCGAN diagram in DCGAN paper?
- Use graph.io perhaps, can include layer details potentially
- Give architecture of both discriminator and generator

## Architecture Description and design choices
- DCGAN: one of the most stable models for these sorts of tasks
  - Split batch training on discriminator
  - Soft labels
  - Label switching
- Training on horse, bird, plane and deer data
  - Planes have more spread wings
- Reducing loss and loss noise:
  - DG_ratio, normalising data
- Hyperparameter choices: 
  - Batch size
  - Label softness
  - Probability of switching labels