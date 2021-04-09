from multiprocessing.dummy import Pool as ThreadPool
import os
import pickle
from scripts.agent import LocalAgent
import neat
import scripts.visualize as visualize

class Train:
    def __init__(self, driver_factory, generations):
        self.generations = generations
        self.driver_factory = driver_factory

    def _fitness_func(self, genome):
        genome_id, genome = genome
        agent = None
        try:
            driver, url = self.driver_factory()
            agent = LocalAgent(driver, url)
        except:
            return (genome_id, None)

        agent.setup()

        net = neat.nn.FeedForwardNetwork.create(genome, self.config)

        fitness = 0
        while not agent.is_done():
            # Get next action
            state = agent.get_state()
            output = net.activate(state)

            # Run and score
            fitness = agent.update(output)

        if agent.is_dead():
            print('Agent died!')
            fitness = 0

        agent.close()

        genome.fitness = fitness
        return (genome_id, fitness)

    def _eval_genomes(self, genomes, config):
        pool = ThreadPool(len(genomes))
        rewards = pool.map(self._fitness_func, genomes)

        # Wait for threads to finish
        pool.close()
        pool.join()

        for (index, (genome_id, fitness)) in enumerate(rewards):
            default_fitness = genomes[index][1].fitness if genomes[index][1].fitness else 0.
            genomes[index][1].fitness = float(fitness) if (not fitness is None) else default_fitness

    def _run(self, config_file, n, checkpoint=None):
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_file)
        self.config = config

        # Setup runner
        population = neat.Population(config) if (checkpoint is None) else checkpoint
        population.add_reporter(neat.StdOutReporter(True))
        population.add_reporter(neat.Checkpointer(20, filename_prefix="checkpoints/checkpoint-"))

        stats = neat.StatisticsReporter()
        population.add_reporter(stats)

        winner = None
        try:
            # Run
            population.run(self._eval_genomes, n)
            winner = population.best_genome
            pickle.dump(winner, open('./checkpoints/winner.pkl', 'wb'))
        except KeyboardInterrupt:
            # Visualize
            visualize.draw_net(config, winner, True)
            visualize.plot_stats(stats, ylog=False, view=True)
            visualize.plot_species(stats, view=True)

    def main(self, config_file="config"):
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, config_file)
        self._run(config_path, self.generations)

class TrainCont(Train):
    def __init__(self, driver_factory, generations, checkpoint_file_name):
        super().__init__(driver_factory, generations)
        self.checkpoint_file_name = checkpoint_file_name

    def _run(self, config_file, n):
        checkpoint = neat.Checkpointer.restore_checkpoint(self.checkpoint_file_name)
        super()._run(config_file, n, checkpoint)
