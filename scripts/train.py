from multiprocessing.dummy import Pool as ThreadPool
import os
import pickle
from scripts.agent import AgarioAgent, Agent, AggressiveAgent, DefensiveAgent, GreedyAgent, LocalAgent, AgarioAgent, NNAgent
import neat
import scripts.visualize as visualize
from threading import Lock, Thread
import random

USE_VISUALS = False

class Train:
    def __init__(self, driver_factory, generations):
        self.generations = generations
        self.driver_factory = driver_factory

    def _fitness_func(self, genome):
        genome_id, genome = genome
        net = neat.nn.FeedForwardNetwork.create(genome, self.config)

        # Setup agent
        agent = None
        try:
            driver, url = self.driver_factory.create()
            agent = NNAgent(driver, url, net)
        except Exception:
            return (genome_id, None)

        # Setup opponent
        thread = Thread(target=self._spawn_opponent)
        thread.start()

        # Run and score
        fitness = agent.run()
        if agent.is_dead():
            print('Agent died!')
            fitness = 0
        agent.close()

        # Finish opponent
        try:
            thread.join()
        except Exception as e:
            print(e)

        genome.fitness = fitness
        return (genome_id, fitness)

    def _spawn_opponent(self, agent_spawner=None):
        # Choose a random agent
        if agent_spawner is None:
            agent_spawner = random.choice([
                lambda driver, url: AggressiveAgent(driver, url),
                lambda driver, url: GreedyAgent(driver, url),
                lambda driver, url: DefensiveAgent(driver, url),
            ])

        # Randomly add an agent
        if random.random() < 0.5:
            return

        try:
            driver, url = self.driver_factory.create()
            agent = agent_spawner(driver, url)
            agent.run()
            agent.close()
        except Exception:
            pass

    def _eval_genomes(self, genomes, config):
        # Create agents
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

        try:
            population.run(self._eval_genomes, n)
        finally:
            winner = population.best_genome
            pickle.dump(winner, open('./checkpoints/winner.pkl', 'wb'))

            if USE_VISUALS:
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

    def _run(self, config_file, n, _=None):
        checkpoint = neat.Checkpointer.restore_checkpoint(self.checkpoint_file_name)
        super()._run(config_file, n, checkpoint)
