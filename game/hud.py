import pygame as pg
from .utils import draw_text

class Hud:
    
    def __init__(self, total_resources, width, height):
        self.width = width
        self.height = height
        self.hud_colour = (122, 122, 122, 175)

        # Resources HUD
        self.resources_surface = pg.Surface((width, height * 0.02), pg.SRCALPHA)
        self.resources_rect = self.resources_surface.get_rect(topleft=(0, 0))
        self.resources_surface.fill(self.hud_colour)
        self.total_resources = total_resources

        # Building HUD
        self.build_surface = pg.Surface((width * 0.15, height * 0.25), pg.SRCALPHA)
        self.build_rect = self.build_surface.get_rect(topleft=(width * 0.84, height * 0.74))
        self.build_surface.fill(self.hud_colour)

        # Select HUD
        self.select_surface = pg.Surface((width * 0.3, height * 0.2), pg.SRCALPHA)
        self.select_rect = self.select_surface.get_rect(topleft=(width * 0.35, height * 0.79))
        self.select_surface.fill(self.hud_colour)

        self.images = self.load_images()
        self.tiles = self.create_build_hud()

        self.selected_tile = None
        self.examined_tile = None

    def create_build_hud(self):
        render_pos = [self.width * 0.84 + 10, self.height * 0.74 + 10]
        object_width = self.build_surface.get_width() // 5
        tiles = []

        for image_name, image in self.images.items():
            pos = render_pos.copy()
            image_tmp = image.copy()
            image_scale = self.scale_image(image_tmp, w=object_width)
            rect = image_scale.get_rect(topleft=pos)

            tile = {
                "name": image_name,
                "icon": image_scale,
                "image": image,
                "rect": rect
            }
            tiles.append(tile)
            render_pos[0] += image_scale.get_width() + 10

        return tiles

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_action = pg.mouse.get_pressed()

        if mouse_action[2]:
            self.selected_tile = None

        for tile in self.tiles:
            if tile["rect"].collidepoint(mouse_pos):
                if mouse_action[0]:
                    self.selected_tile = tile

        

    def draw(self, screen):
        if self.selected_tile is not None:
            img = self.selected_tile["image"].copy()
        # Draw the resource HUD
        screen.blit(self.resources_surface, (0, 0))
        # Draw the select HUD
        if self.examined_tile is not None:
            w, h = self.select_rect.width, self.select_rect.height
            screen.blit(self.select_surface, (self.width * 0.35, self.height * 0.79))
            img = self.examined_tile.image.copy()
            img_scale = self.scale_image(img, h=h * 0.7)
            draw_text(screen, self.examined_tile.name, 40, (255, 255, 255), self.select_rect.topleft)
            draw_text(screen, str(self.examined_tile.inventory), 30, (255, 255, 255), self.select_rect.center)

        for tile in self.tiles:
            icon = tile["icon"].copy()
            screen.blit(icon, tile["rect"].topleft)

        # Draw the resource values
        pos = self.width - 400
        txt = "Total resources produced: " + str(self.total_resources)
        draw_text(screen, txt, 30, (255, 255, 255), (pos, 0))
        

    def load_images(self):
        images = {}
        image_files = {
            "lumbermill": "assets/graphics/building01.png",
            "stonemasonry": "assets/graphics/building02.png"
        }

        for name, file_path in image_files.items():
            image = pg.image.load(file_path).convert_alpha()
            images[name] = image

        return images

    def scale_image(self, image, w=None, h=None):
        if w is not None and h is not None:
            image = pg.transform.scale(image, (int(w), int(h)))
        elif w is not None:
            scale = w / image.get_width()
            h = scale * image.get_height()
            image = pg.transform.scale(image, (int(w), int(h)))
        elif h is not None:
            scale = h / image.get_height()
            w = scale * image.get_width()
            image = pg.transform.scale(image, (int(w), int(h)))

        return image
