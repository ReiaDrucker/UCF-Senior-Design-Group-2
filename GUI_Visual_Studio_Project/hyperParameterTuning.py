import numpy as np
from ray import tune

# Loss function we are seeking to minimize
def objective(step, alpha, beta, charlie):
    return alpha + beta + charlie

def training_function(config, checkpoint_dir="./hpTuning"):
    # Hyperparameters
    alpha, beta, charlie = config["alpha"], config["beta"], config["charlie"]

    # How many samples do we want for each pair
    for step in range(10):
        # Iterative training function - can be any arbitrary training procedure.
        intermediate_score = objective(step, alpha, beta, charlie)
        # Feed the score back back to Tune.
        tune.report(mean_loss=intermediate_score)

# Should probably setup checkpointing so that if there is a crash we can resume from where we left off
def main(): 

    analysis = tune.run(

        training_function,
        name = "experiment",
        local_dir = "./hpTuning",
        verbose = 2,

        # How much of your cpu and gpu to give each trial
        # My machine has 16 threads so if passed 16 it would give one trial all 16 threads
        # Here I am giving each trial no cpu cores and a hundreth of my gpu
        resources_per_trial = {"cpu": 0, "gpu": 0.01},

        config =
        {
            # There are other options for how we want to distribute our options
            "alpha": tune.grid_search([0.001, 0.01, 0.1]),
            "beta": tune.grid_search([1, 2, 3]),
            "charlie": tune.grid_search([-1, 1, 0])
        },

        # Set to True to continue from a checkpoint if stopped
        # Set to False if a new expirement is intended
        resume = False
        )

    print("Best config: ", analysis.get_best_config(metric="mean_loss", mode="min"))
    
if __name__ == '__main__':
    main()
