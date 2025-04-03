import pygame
from typing import Callable, Union, Tuple, Optional
import math
import random


class Button:
    """
    An enhanced button class for Pygame with customizable properties and visual effects.

    Attributes:
        text: The text displayed on the button
        pos: Position (x, y) of the top-left corner
        size: Width and height of the button
        callback: Function to call when the button is clicked
        margin: Width of the border/margin around the button
        font_size: Font size for the button text
        colors: Dictionary containing all color settings
        enabled: Whether the button is enabled (clickable)
        visible: Whether the button is visible
        effects: Dictionary of visual effects to apply
    """

    def __init__(
        self,
        text: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        callback: Callable[[], None],
        margin: int = 0,
        font_size: int = 50,
        colors: Optional[dict] = None,
        enabled: bool = True,
        visible: bool = True,
        effects: Optional[dict] = None,
    ):
        self.text = text
        self.pos = pos
        self.size = size
        self.callback = callback
        self.margin = margin
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.inner_rect = pygame.Rect(
            pos[0] + margin, pos[1] + margin, size[0] - 2 * margin, size[1] - 2 * margin
        )
        self.font = pygame.font.Font(None, font_size)
        self.enabled = enabled
        self.visible = visible

        # Animation timing
        self.animation_time = 0

        # Default colors
        self.colors = {
            "normal": (50, 50, 50),  # Dark gray
            "hover": (75, 75, 75),  # Medium gray
            "pressed": (25, 25, 25),  # Very dark gray
            "disabled": (100, 100, 100),  # Light gray
            "text": (255, 255, 255),  # White
            "text_disabled": (180, 180, 180),  # Light gray
            "margin": (200, 200, 200),  # Light gray for margin/border
            "glow": (100, 180, 255, 150),  # Blue glow with alpha
        }

        # Default effects
        self.effects = {
            "shadow": False,  # Drop shadow
            "glow": False,  # Glowing effect when hovered
            "pulse": False,  # Pulsating animation
            "gradient": True,  # Use gradient coloring
            "rounded_corners": 10,  # Rounded corner radius
            "hover_animation": False,  # Animate on hover
            "click_animation": True,  # Animation on click
            "text_shadow": False,  # Text shadow
            "particle_effect": False,  # Particle effects on click
        }

        # Override with custom colors if provided
        if colors:
            self.colors.update(colors)

        # Override with custom effects if provided
        if effects:
            self.effects.update(effects)

        # State tracking
        self.pressed = False
        self.hover_scale = 1.0
        self.press_scale = 1.0
        self.particles = []
        self.hovered_time = 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button on the given surface with visual effects"""
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()
        mouse_over = self.rect.collidepoint(mouse_pos)

        # Update animation timers
        self.animation_time += 0.02
        if mouse_over:
            self.hovered_time += 0.05
            if self.effects["hover_animation"]:
                self.hover_scale = 1.0 + math.sin(self.hovered_time * 3) * 0.02
        else:
            self.hovered_time = 0
            self.hover_scale = 1.0

        # Determine button color based on state
        if not self.enabled:
            color = self.colors["disabled"]
            text_color = self.colors["text_disabled"]
        elif self.pressed and mouse_over:
            color = self.colors["pressed"]
            text_color = self.colors["text"]
            if self.effects["click_animation"]:
                self.press_scale = 0.95
        elif mouse_over:
            color = self.colors["hover"]
            text_color = self.colors["text"]
        else:
            color = self.colors["normal"]
            text_color = self.colors["text"]
            self.press_scale = 1.0

        # Apply scaling for hover/press animations
        scaled_rect = self.rect.copy()
        if self.effects["hover_animation"] or self.effects["click_animation"]:
            scale_factor = self.hover_scale * self.press_scale
            # Calculate scaled dimensions
            scaled_width = int(self.rect.width * scale_factor)
            scaled_height = int(self.rect.height * scale_factor)
            # Center the scaled rect on the original position
            offset_x = (self.rect.width - scaled_width) // 2
            offset_y = (self.rect.height - scaled_height) // 2
            scaled_rect = pygame.Rect(
                self.rect.x + offset_x,
                self.rect.y + offset_y,
                scaled_width,
                scaled_height,
            )
            # Scale inner rect too if margin is set
            if self.margin > 0:
                inner_scaled_width = int(
                    (self.rect.width - 2 * self.margin) * scale_factor
                )
                inner_scaled_height = int(
                    (self.rect.height - 2 * self.margin) * scale_factor
                )
                inner_offset_x = (self.rect.width - inner_scaled_width) // 2
                inner_offset_y = (self.rect.height - inner_scaled_height) // 2
                self.inner_rect = pygame.Rect(
                    self.rect.x + inner_offset_x,
                    self.rect.y + inner_offset_y,
                    inner_scaled_width,
                    inner_scaled_height,
                )

        rounded_corners = self.effects["rounded_corners"]

        # Draw shadow if enabled
        if self.effects["shadow"]:
            shadow_rect = scaled_rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            pygame.draw.rect(
                screen, (20, 20, 20, 150), shadow_rect, border_radius=rounded_corners
            )

        # Draw glow effect when hovered
        if self.effects["glow"] and mouse_over:
            glow_size = 10
            glow_rect = pygame.Rect(
                scaled_rect.x - glow_size,
                scaled_rect.y - glow_size,
                scaled_rect.width + glow_size * 2,
                scaled_rect.height + glow_size * 2,
            )

            # Create a surface with alpha for the glow
            glow_surface = pygame.Surface(
                (glow_rect.width, glow_rect.height), pygame.SRCALPHA
            )

            # Draw multiple circles with decreasing alpha for glow effect
            glow_color = self.colors.get("glow", (100, 180, 255, 150))
            for i in range(glow_size, 0, -2):
                alpha = 150 - (i * 10)
                current_color = (glow_color[0], glow_color[1], glow_color[2], alpha)
                pygame.draw.rect(
                    glow_surface,
                    current_color,
                    pygame.Rect(
                        i, i, glow_rect.width - 2 * i, glow_rect.height - 2 * i
                    ),
                    border_radius=rounded_corners + i,
                )

            # Draw the glow surface
            screen.blit(glow_surface, (glow_rect.x, glow_rect.y))

        # Apply gradient if enabled
        if self.effects["gradient"]:
            # Create a surface for gradient
            button_surface = pygame.Surface(
                (scaled_rect.width, scaled_rect.height), pygame.SRCALPHA
            )

            # Generate gradient colors
            base_color = color
            light_color = tuple(min(c + 40, 255) for c in base_color[:3])
            dark_color = tuple(max(c - 40, 0) for c in base_color[:3])

            # Draw gradient
            for i in range(scaled_rect.height):
                # Calculate gradient color
                if i < scaled_rect.height // 2:
                    # Top half: light to base
                    ratio = i / (scaled_rect.height // 2)
                    current_color = tuple(
                        int(light_color[j] + (base_color[j] - light_color[j]) * ratio)
                        for j in range(3)
                    )
                else:
                    # Bottom half: base to dark
                    ratio = (i - scaled_rect.height // 2) / (scaled_rect.height // 2)
                    current_color = tuple(
                        int(base_color[j] + (dark_color[j] - base_color[j]) * ratio)
                        for j in range(3)
                    )

                # Draw a horizontal line with the current color
                pygame.draw.line(
                    button_surface, current_color, (0, i), (scaled_rect.width, i)
                )

            # Apply rounded corners to the gradient surface
            if rounded_corners > 0:
                # Create a mask with rounded corners
                mask = pygame.Surface(
                    (scaled_rect.width, scaled_rect.height), pygame.SRCALPHA
                )
                pygame.draw.rect(
                    mask,
                    (255, 255, 255),
                    (0, 0, scaled_rect.width, scaled_rect.height),
                    border_radius=rounded_corners,
                )
                # Apply the mask to the gradient surface
                button_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # Draw the gradient button
            screen.blit(button_surface, (scaled_rect.x, scaled_rect.y))
        else:
            # Draw margin/border if margin is set
            if self.margin > 0:
                pygame.draw.rect(
                    screen,
                    self.colors["margin"],
                    scaled_rect,
                    border_radius=rounded_corners,
                )
                # Draw the inner button with smaller border radius
                pygame.draw.rect(
                    screen,
                    color,
                    self.inner_rect,
                    border_radius=max(0, rounded_corners - self.margin),
                )
            else:
                # Draw button background without margin
                pygame.draw.rect(
                    screen, color, scaled_rect, border_radius=rounded_corners
                )

        # Apply pulsating effect
        if self.effects["pulse"]:
            pulse_factor = 0.5 + abs(math.sin(self.animation_time * 2)) * 0.5
            pulse_color = tuple(int(c * pulse_factor) for c in color[:3])
            pulse_alpha = 100

            # Create a surface for the pulse effect
            pulse_surface = pygame.Surface(
                (scaled_rect.width, scaled_rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(
                pulse_surface,
                pulse_color + (pulse_alpha,),
                (0, 0, scaled_rect.width, scaled_rect.height),
                border_radius=rounded_corners,
            )

            # Apply the pulse effect
            screen.blit(pulse_surface, (scaled_rect.x, scaled_rect.y))

        # Draw button text with optional shadow
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=scaled_rect.center)

        if self.effects["text_shadow"]:
            # Draw text shadow
            shadow_surface = self.font.render(self.text, True, (20, 20, 20))
            shadow_rect = shadow_surface.get_rect(
                center=(text_rect.centerx + 2, text_rect.centery + 2)
            )
            screen.blit(shadow_surface, shadow_rect)

        screen.blit(text_surface, text_rect)

        # Draw particles for click effect
        if self.effects["particle_effect"] and self.particles:
            # Update and draw particles
            new_particles = []
            for particle in self.particles:
                # Unpack particle data: position, velocity, color, size, life
                (x, y), (vx, vy), color, size, life = particle

                # Update particle position and properties
                x += vx
                y += vy
                size *= 0.95  # Shrink over time
                life -= 1

                # Keep alive particles
                if life > 0 and size > 0.5:
                    pygame.draw.circle(screen, color, (int(x), int(y)), int(size))
                    new_particles.append(((x, y), (vx, vy), color, size, life))

            self.particles = new_particles

    def check_click(self, event: pygame.event.Event) -> bool:
        """Check if the button was clicked."""
        if not self.enabled or not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True

                # Create particles on click if enabled
                if self.effects["particle_effect"]:
                    self._create_particles(event.pos)

                self.callback()  # Call the callback function
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False

        return False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events with press and release detection."""
        if not self.enabled or not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True

                # Create particles on click if enabled
                if self.effects["particle_effect"]:
                    self._create_particles(event.pos)

                return False  # Not yet clicked (only pressed down)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False

            if was_pressed and self.rect.collidepoint(event.pos):
                self.callback()  # Call the callback function
                return True  # Button was clicked

        return False

    def _create_particles(self, pos):
        """Create particles for click effect"""
        particles_count = 20
        for _ in range(particles_count):
            # Random angle and speed
            angle = math.radians(random.uniform(0, 360))
            speed = random.uniform(1, 3)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

            # Random color based on button color
            base_color = self.colors["normal"]
            color_variance = 40
            particle_color = tuple(
                min(255, max(0, c + random.randint(-color_variance, color_variance)))
                for c in base_color[:3]
            )

            # Create particle: (position, velocity, color, size, life)
            particle = (
                pos,
                velocity,
                particle_color,
                random.uniform(1, 3),
                random.randint(20, 40),
            )
            self.particles.append(particle)

    def update(self) -> None:
        """Update button state and animations"""
        if not self.enabled or not self.visible:
            self.pressed = False
            self.hover_scale = 1.0
            return

        mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button
        mouse_pos = pygame.mouse.get_pos()
        mouse_over = self.rect.collidepoint(mouse_pos)

        if mouse_pressed and mouse_over:
            self.pressed = True
        elif not mouse_pressed:
            self.pressed = False

        # Smoothly return press scale to normal
        if not self.pressed and self.press_scale < 1.0:
            self.press_scale = min(1.0, self.press_scale + 0.05)

    # Property access methods remain unchanged
    def set_position(self, pos: Tuple[int, int]) -> None:
        """Set button position"""
        self.pos = pos
        self.rect.topleft = pos
        self.inner_rect.topleft = (pos[0] + self.margin, pos[1] + self.margin)

    def set_text(self, text: str) -> None:
        """Change button text"""
        self.text = text

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the button"""
        self.enabled = enabled

    def set_visible(self, visible: bool) -> None:
        """Show or hide the button"""
        self.visible = visible

    def set_margin(self, margin: int) -> None:
        """Set the button's margin/border width"""
        self.margin = margin
        self.inner_rect = pygame.Rect(
            self.pos[0] + margin,
            self.pos[1] + margin,
            self.size[0] - 2 * margin,
            self.size[1] - 2 * margin,
        )

    def set_colors(self, colors: dict) -> None:
        """Update button colors"""
        self.colors.update(colors)

    def set_effects(self, effects: dict) -> None:
        """Update button visual effects"""
        self.effects.update(effects)

    def is_hovered(self) -> bool:
        """Check if the mouse is hovering over the button"""
        return self.rect.collidepoint(pygame.mouse.get_pos())


class Label:
    """
    A label class for Pygame that shows a title and value.

    Attributes:
        title: The title text displayed on the label
        value: The value text displayed on the label
        pos: Position (x, y) of the top-left corner
        font_size: Font size for the text
        colors: Dictionary containing color settings
        visible: Whether the label is visible
        effects: Dictionary of visual effects to apply
    """

    def __init__(
        self,
        title: str,
        value: str,
        pos: Tuple[int, int],
        font_size: int = 36,
        colors: Optional[dict] = None,
        visible: bool = True,
        effects: Optional[dict] = None,
        alignment: str = "left",
        spacing: int = 10,
        width: Optional[int] = None,
    ):
        self.title = title
        self.value = value
        self.pos = pos
        self.font_size = font_size
        self.visible = visible
        self.alignment = alignment  # "left", "center", or "right"
        self.spacing = spacing  # Space between title and value
        self.width = width  # Optional fixed width

        # Create fonts
        self.title_font = pygame.font.Font(None, font_size)
        self.value_font = pygame.font.Font(None, font_size)

        # Default colors
        self.colors = {
            "title": (220, 220, 220),  # Light gray for title
            "value": (255, 255, 255),  # White for value
            "background": None,  # No background by default
            "border": None,  # No border by default
            "shadow": (20, 20, 20, 150),  # Shadow color with alpha
        }

        # Default effects
        self.effects = {
            "shadow": False,  # Text shadow
            "value_highlight": False,  # Highlight the value part
            "background": False,  # Draw a background
            "border": False,  # Draw a border
            "rounded_corners": 5,  # Border radius if background is drawn
            "animate_value": False,  # Animate value changes
            "pulse_on_change": False,  # Pulse when value changes
        }

        # Override with custom colors if provided
        if colors:
            self.colors.update(colors)

        # Override with custom effects if provided
        if effects:
            self.effects.update(effects)

        # Animation properties
        self.animation_time = 0
        self.previous_value = self.value
        self.pulse_alpha = 0
        self.animation_progress = 1.0

        # Calculate initial size
        self.update_size()

    def update_size(self):
        """Update label dimensions based on content"""
        # Get title and value sizes
        title_surface = self.title_font.render(self.title, True, self.colors["title"])
        value_surface = self.value_font.render(
            str(self.value), True, self.colors["value"]
        )

        self.title_size = title_surface.get_size()
        self.value_size = value_surface.get_size()

        # Calculate total width based on alignment and content
        if self.width:
            self.total_width = self.width
        else:
            if self.alignment == "center":
                # Center alignment: max width needed for title or value
                self.total_width = max(self.title_size[0], self.value_size[0])
            else:
                # Left or right alignment: sum of widths + spacing
                self.total_width = (
                    self.title_size[0] + self.spacing + self.value_size[0]
                )

        # Calculate height (same for both title and value)
        self.height = max(self.title_size[1], self.value_size[1])

        # Create a rect for the entire label
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.total_width, self.height)

    def set_value(self, new_value):
        """Update the label's value"""
        if str(new_value) != str(self.value):
            # Store previous value for animation
            self.previous_value = self.value
            self.value = new_value

            # Trigger animation if enabled
            if self.effects["animate_value"] or self.effects["pulse_on_change"]:
                self.animation_progress = 0.0
                self.pulse_alpha = 200

            self.update_size()

    def update(self, dt=0.016):
        """Update animations"""
        # Update animation timing
        if self.animation_progress < 1.0:
            self.animation_progress = min(1.0, self.animation_progress + (dt * 5))

        # Update pulse alpha
        if self.pulse_alpha > 0:
            self.pulse_alpha = max(0, self.pulse_alpha - (dt * 400))

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the label on the given surface"""
        if not self.visible:
            return

        # Update animation timing
        self.animation_time += 0.02

        # Render title and value surfaces
        title_surface = self.title_font.render(self.title, True, self.colors["title"])
        value_surface = self.value_font.render(
            str(self.value), True, self.colors["value"]
        )

        # Calculate positions based on alignment
        if self.alignment == "left":
            title_x = self.pos[0]
            value_x = self.pos[0] + self.title_size[0] + self.spacing
        elif self.alignment == "center":
            title_x = self.pos[0] + (self.total_width - self.title_size[0]) // 2
            value_x = self.pos[0] + (self.total_width - self.value_size[0]) // 2
        else:  # right
            value_x = self.pos[0] + self.total_width - self.value_size[0]
            title_x = value_x - self.title_size[0] - self.spacing

        title_y = self.pos[1] + (self.height - self.title_size[1]) // 2
        value_y = self.pos[1] + (self.height - self.value_size[1]) // 2

        # Draw background if enabled
        if self.effects["background"] and self.colors["background"]:
            pygame.draw.rect(
                screen,
                self.colors["background"],
                self.rect,
                border_radius=self.effects["rounded_corners"],
            )

        # Draw border if enabled
        if self.effects["border"] and self.colors["border"]:
            pygame.draw.rect(
                screen,
                self.colors["border"],
                self.rect,
                width=2,
                border_radius=self.effects["rounded_corners"],
            )

        # Draw pulse effect when value changes
        if self.effects["pulse_on_change"] and self.pulse_alpha > 0:
            pulse_color = (*self.colors["value"][:3], self.pulse_alpha)
            pulse_rect = pygame.Rect(
                value_x - 5,
                value_y - 5,
                self.value_size[0] + 10,
                self.value_size[1] + 10,
            )

            # Create a surface for the pulse with alpha
            pulse_surface = pygame.Surface(
                (pulse_rect.width, pulse_rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(
                pulse_surface,
                pulse_color,
                pygame.Rect(0, 0, pulse_rect.width, pulse_rect.height),
                border_radius=self.effects["rounded_corners"],
            )

            # Draw pulse effect behind the value
            screen.blit(pulse_surface, (pulse_rect.x, pulse_rect.y))

        # Draw text shadow if enabled
        if self.effects["shadow"]:
            shadow_offset = 2

            # Title shadow
            title_shadow = self.title_font.render(
                self.title, True, self.colors["shadow"]
            )
            screen.blit(
                title_shadow, (title_x + shadow_offset, title_y + shadow_offset)
            )

            # Value shadow
            value_shadow = self.value_font.render(
                str(self.value), True, self.colors["shadow"]
            )
            screen.blit(
                value_shadow, (value_x + shadow_offset, value_y + shadow_offset)
            )

        # Draw title and value text
        screen.blit(title_surface, (title_x, title_y))

        # Draw value with possible highlight effect
        if self.effects["value_highlight"]:
            # Create a highlight surface for the value
            value_rect = pygame.Rect(
                value_x - 4, value_y - 2, self.value_size[0] + 8, self.value_size[1] + 4
            )

            # Draw the highlight
            pygame.draw.rect(
                screen,
                (*self.colors["value"][:3], 50),  # Semi-transparent value color
                value_rect,
                border_radius=3,
            )

        # Draw the value text
        screen.blit(value_surface, (value_x, value_y))

    # Utility methods
    def set_position(self, pos: Tuple[int, int]):
        """Set label position"""
        self.pos = pos
        self.rect.topleft = pos

    def set_title(self, title: str):
        """Set the label title"""
        if title != self.title:
            self.title = title
            self.update_size()

    def set_font_size(self, size: int):
        """Set font size for both title and value"""
        self.font_size = size
        self.title_font = pygame.font.Font(None, size)
        self.value_font = pygame.font.Font(None, size)
        self.update_size()

    def set_visible(self, visible: bool):
        """Show or hide the label"""
        self.visible = visible

    def set_colors(self, colors: dict):
        """Update label colors"""
        self.colors.update(colors)

    def set_effects(self, effects: dict):
        """Update label effects"""
        self.effects.update(effects)

    def set_alignment(self, alignment: str):
        """Set text alignment (left, center, right)"""
        self.alignment = alignment
        self.update_size()


def format_time(time: int):
    time //= 1000
    return str(time // 60).zfill(2) + ":" + str(time % 60).zfill(2)


def collide(
    pos1: tuple[int, int],
    size1: tuple[int, int],
    pos2: tuple[int, int],
    size2: tuple[int, int],
):
    """
    Check if two rectangular areas collide.

    Args:
        pos1 (tuple[int, int]): Top-left corner of the first rectangle (x, y).
        size1 (tuple[int, int]): Size of the first rectangle (width, height).
        pos2 (tuple[int, int]): Top-left corner of the second rectangle (x, y).
        size2 (tuple[int, int]): Size of the second rectangle (width, height).

    Returns:
        bool: True if the rectangles collide, False otherwise.
    """
    collision = all(
        pos1[i] <= pos2[i]
        and pos1[i] + size1[i] >= pos2[i]
        or pos2[i] <= pos1[i]
        and pos2[i] + size2[i] >= pos1[i]
        for i in range(2)
    )
    return collision
