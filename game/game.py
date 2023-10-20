import pygame as pg
import sys
from .world import World
from .settings import TILE_SIZE
from .utils import draw_text
from .camera import Camera
from .hud import Hud
from .workers import Worker
import random
import pandas as pd


class Game:

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width, self.height = self.screen.get_size()
        self.start_time = pg.time.get_ticks()
        self.end_time = 10000

        # Controls
        self.GIVING_WORKER_COUNT = 20
        self.STEALING_WORKER_COUNT = 0
        self.BUILDING_COUNT = 7
        self.WORLD_SIZE = 50

        # entities
        self.entities = []

        # Counter of the total resources produced
        self.total_resources = 0

        # hud
        self.hud = Hud(self.total_resources, self.width, self.height)

        # world
        self.world = World(self.entities, self.hud, self.WORLD_SIZE,
                           self.WORLD_SIZE, self.width, self.height, self)
        # buildings
        for _ in range(self.BUILDING_COUNT):
            self.create_random_lumbermill()
        # worker
        for _ in range(self.GIVING_WORKER_COUNT):
            Worker(self.world.world[25][25], self.world, 1, "GW" + str(_))
        for _ in range(self.STEALING_WORKER_COUNT):
            Worker(self.world.world[25][25], self.world, -1,
                   "BW" + str(self.GIVING_WORKER_COUNT + _))

        # camera
        self.camera = Camera(self.width, self.height)

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        now = pg.time.get_ticks()
        if now - self.start_time >= self.end_time and False:
            self.quit_game()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit_game()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit_game()

    def quit_game(self):
        while True:
            user_input = input(
                "Do you want to save the data? (y/n): ").strip().lower()
            if user_input == 'y':
                self.export_data_to_excel()
                break
            elif user_input == 'n':
                break
            else:
                break
        pg.quit()
        sys.exit()

    def export_data_to_excel(self):
        # Create a single Excel writer to manage the file
        with pd.ExcelWriter(self.excel_filename, engine='xlsxwriter') as writer:
            data = []

            for entity in self.entities:
                if isinstance(entity, Worker):
                    data.append([
                        entity.id,
                        entity.character_value,
                        entity.building_looted_all_time,
                        entity.interaction_count_all_time,
                        entity.interaction_transfer_all_time,
                        entity.step_counter,
                        entity.export_inventory,  
                        entity.export_interaction_with_time,
                        entity.export_interaction_transfers_with_time
                    ])

            # Export the parameters of the simulation
            self.export_sheet_data(writer, "game_data", [
                ["ID", "Character value", "Building looted", "Interaction count", "Interaction transfer",
                    "Step counter", "Inventory", "Interactions with timer", "Interactions transfers with timer"]
            ] + data)

            self.export_sheet_data(writer, "general_game_data", [
                ["Total Worker", "Nice worker", "Bad worker", "Total building",
                    "Total resources produced", "Duration", "World size"],
                [self.GIVING_WORKER_COUNT + self.STEALING_WORKER_COUNT, self.GIVING_WORKER_COUNT, self.STEALING_WORKER_COUNT,
                    self.BUILDING_COUNT, self.total_resources, self.end_time / 1000, self.WORLD_SIZE]
            ])

            data = []
            for entity in self.entities:
                if isinstance(entity, Worker):

                    inventory_values = entity.export_inventory

                    # Ensure inventory_values have the right length
                    while len(inventory_values) < self.export_items_count:
                        inventory_values.append(inventory_values[-1])

                    inventory_values = inventory_values[:self.export_items_count]

                    row_data = [entity.id]
                    row_data.extend(["Inventory"])
                    row_data.extend(inventory_values)
                    data.append(row_data)

            # export the inventory levels of all the workers
            self.export_sheet_data(writer, "inventory_data", [
                ["ID", "Inventory"] +
                [i+1 for i in range(len(inventory_values))]
            ] + data)

            data = []
            for entity in self.entities:
                if isinstance(entity, Worker):
                    interaction_values = entity.export_interaction_with_time
                    while len(interaction_values) < self.export_items_count:
                        interaction_values.append(interaction_values[-1])
                    interaction_values = interaction_values[:self.export_items_count]
                    row_data = [entity.id]
                    row_data.extend(["Interactions"])
                    row_data.extend(interaction_values)
                    data.append(row_data)

            # export the amount of interactions of all the workers
            self.export_sheet_data(writer, "interactions_with_time_data", [
                ["ID", "Interactions"] +
                [i+1 for i in range(len(interaction_values))]
            ] + data)

            data = []
            for entity in self.entities:
                if isinstance(entity, Worker):
                    interaction_transfer_values = entity.export_interaction_transfers_with_time
                    while len(interaction_transfer_values) < self.export_items_count:
                        interaction_transfer_values.append(interaction_transfer_values[-1])
                    interaction_transfer_values = interaction_transfer_values[:self.export_items_count]
                    row_data = [entity.id]
                    row_data.extend(["Interaction transfer amounts"])
                    row_data.extend(interaction_transfer_values)
                    data.append(row_data)

            # export the amount that has been transfered during an interaction of all the workers
            self.export_sheet_data(writer, "interaction_transfer_data", [
                ["ID", "Interaction transfer amounts"] +
                [i+1 for i in range(len(interaction_transfer_values))]
            ] + data)

            data = []
            for entity in self.entities:
                if isinstance(entity, Worker):
                    step_values = entity.export_steps_with_time
                    while len(step_values) < self.export_items_count:
                        step_values.append(step_values[-1])
                    step_values = step_values[:self.export_items_count]
                    row_data = [entity.id]
                    row_data.extend(["Steps with time"])
                    row_data.extend(step_values)
                    data.append(row_data)

            # export the amount of steps taken of all the workers
            self.export_sheet_data(writer, "Steps with time", [
                ["ID", "Steps with time"] +
                [i+1 for i in range(len(step_values))]
            ] + data)


    def export_sheet_data(self, writer, sheet_name, data):
        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    def worker_has_inventory_count(self):
        worker_count = 0  # Initialize a count for the workers
        for entity in self.entities:
            if isinstance(entity, Worker):
                if len(entity.export_inventory) < self.export_items_count:
                    return False  # Return False if any worker doesn't meet the condition
                worker_count += 1  # Increment the worker count
        return worker_count == (self.GIVING_WORKER_COUNT + self.STEALING_WORKER_COUNT)  

    def update(self):
        self.camera.update()

        for entity in self.entities:
            entity.update()

        self.hud.update()
        self.world.update(self.camera)
        self.hud.total_resources = self.total_resources

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.world.draw(self.screen, self.camera)
        self.hud.draw(self.screen)
        draw_text(
            self.screen, f'fps={round(self.clock.get_fps())}', 25, (255, 255, 255), (10, 10))
        pg.display.flip()

    # creates buildings randomly in the world
    def create_random_lumbermill(self):
        while True:
            # Randomly choose a grid position
            x = random.randint(0, self.world.grid_length_x - 1)
            y = random.randint(0, self.world.grid_length_y - 1)

            # Check if the chosen position is suitable 
            if (
                not self.world.world[x][y]["collision"]
                and self.is_far_from_existing_buildings(x, y, min_distance=5)
            ):
                # Create the Lumbermill at the chosen position
                self.world.create_building((x, y), self)
                break

    def is_far_from_existing_buildings(self, x, y, min_distance):
        for i in range(self.world.grid_length_x):
            for j in range(self.world.grid_length_y):
                if self.world.buildings[i][j] and self.distance(x, y, i, j) < min_distance:
                    return False
        return True

    def distance(self, x1, y1, x2, y2):
        # Calculate the distance between two grid positions
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
