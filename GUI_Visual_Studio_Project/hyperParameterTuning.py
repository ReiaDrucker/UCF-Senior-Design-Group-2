import numpy as np
from ray import tune


# This is the loss function we are seeking to minimize
def objective(step, alpha, beta):
    return alpha + beta


def training_function(config, checkpoint_dir=None):
    # Hyperparameters
    alpha, beta = config["alpha"], config["beta"]

    # How many samples do we want for each pair
    for step in range(10):
        # Iterative training function - can be any arbitrary training procedure.
        intermediate_score = objective(step, alpha, beta)
        # Feed the score back back to Tune.
        tune.report(mean_loss=intermediate_score)

# Should probably setup checkpointing so that if there is a crash we can resume from where we left off
def main(): 

    analysis = tune.run(
    
        training_function,

        config =
        {
            # There are other options for how we want to distribute our options
            "alpha": tune.grid_search([0.001, 0.01, 0.1]),
            "beta": tune.grid_search([1, 2, 3])
        },

        # This is specific to my desktop not sure what behavior you will get
        resources_per_trial={"cpu": 16, "gpu": 2})

    print("Best config: ", analysis.get_best_config(metric="mean_loss", mode="min"))
    
if __name__ == '__main__':
    main()
