import neat
from multiprocessing.dummy import Pool as ThreadPool



def neat_runner(callback):
    agar_aio = neat.NEAT(n_networks = 150,
                    input_size = 2,
                    output_size = 2,
                    bias = True,
                    c1 = 1.0, c2 = 1.0, c3 = 0.4,
                    distance_threshold = 3.0,
                    weight_mutation_rate = 0.8,
                    node_mutation_rate = 0.03,
                    connection_mutation_rate = 0.05,
                    interspecies_mating_rate = 0.001,
                    disable_rate = 0.75,
                    stegnant_threshold = 15,
                    input_activation = neat.steepened_sigmoid,
                    hidden_activation = neat.steepened_sigmoid,
                    output_activation = neat.steepened_sigmoid)

    FITNESS_THRESHOLD = 100

    while True:
        print(f'Generation: {agar_aio.generation}')
        pool = ThreadPool(len(agar_aio.population))

        def score_genome(genome):
            print('Scoring genome')

            # Run and score
            fitness = callback(genome)
            return (fitness, genome)

        rewards = pool.map(score_genome, agar_aio.population[0:1])

        # Wait for threads to finish
        pool.close()
        pool.join()

        # Return if any genomes were above the threshold value
        for (fitness, genome) in rewards:
            # if fitness >= FITNESS_THRESHOLD:
            return genome

        return
        # agar_aio.next_generation(rewards)
