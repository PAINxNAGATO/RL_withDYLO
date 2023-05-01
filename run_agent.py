# Imports:
from env import Environment
from env import cat1_pos, cat2_pos, a
from agent_brain import QLearningTable
import warnings
import concurrent.futures

warnings.simplefilter(action='ignore', category=FutureWarning)


pixels = 64

def update():
    global flag
    # Resulted list for the plotting Episodes via Steps
    steps = []

    # Summed costs for all episodes in resulted list
    all_costs = []

    for episode in range(1000):
        # Initial Observation
        observation = env.reset()

        # Updating number of Steps for each Episode
        i = 0

        # Updating the cost for each episode
        cost = 0

        while True:
            # Refreshing environment
            env.render()

            # RL chooses action based on observation
            action = RL.choose_action(str(observation))

            # RL takes an action and get the next observation and reward
            observation_, reward, done = env.step(action)

            # RL learns from this transition and calculating the cost
            cost += RL.learn(str(observation), action, reward, str(observation_))

            # Swapping the observations - current and next
            observation = observation_

            # Calculating number of Steps in the current Episode
            i += 1

            # Break while loop when it is the end of current Episode
            # When agent reached the goal or obstacle
            if done:
                steps += [i]
                all_costs += [cost]
                break

    # Showing the final route
    env.final()

    # Showing the Q-table with values for each action
    RL.print_q_table()

    # Plotting the results
    RL.plot_results(steps, all_costs)

    # Printing Cat's path map:
    print()
    print("Cat 1 most visited squares:")
    for k in cat1_pos.keys():
        if cat1_pos[k] != 0:
            if [k[0] * pixels, k[1] * pixels] in a.values():
                say = 'YES'
            else:
                say = 'NO'
            print(f'Cell {k}: {cat1_pos[k]} times | Cell in final path: {say}')
    print()
    print()
    print("Cat 2 most visited squares:")
    for k in cat2_pos.keys():
        if cat2_pos[k] != 0:
            if [k[0] * pixels, k[1] * pixels] in a.values():
                say = 'YES'
            else:
                say = 'NO'
            print(f'Cell {k}: {cat2_pos[k]} times | Cell in final path: {say}')
    print()


# Commands to be implemented after running this file
if __name__ == "__main__":
    # Calling for the environment
    env = Environment()
    # Calling for the main algorithm
    RL = QLearningTable(actions=list(range(env.n_actions)))
    # Running the main loop with Episodes by calling the function update()
    env.after(100, update)  # Or just update()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        f1 = executor.submit(env.cat1_move)
        f2 = executor.submit(env.cat2_move)
        env.mainloop()
