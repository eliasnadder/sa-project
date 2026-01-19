import pygame

WHITE = (240, 240, 240)


class TextInputBox:
    def __init__(self, x, y, width, height, hint=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.hint = hint
        self.active = False
        self.error = False

    def draw(self, screen, font):
        # Background
        color = (90, 90, 90) if not self.active else (120, 120, 120)
        if self.error:
            color = (180, 80, 80)
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)

        # Text or hint
        if self.text:
            text_surf = font.render(self.text, True, WHITE)
        else:
            text_surf = font.render(self.hint, True, (150, 150, 150))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.error = False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return self.text
            elif event.unicode.isdigit():
                self.text += event.unicode
        return None
