# IPL_Sim_part1.py - Part 1/2
# Rebuilt IPL cricket simulator (Part 1)
# Contains: imports, settings, data models, team definitions (all 10 teams),
# RCB bias + Digvesh Rathi nerf constants, and UI helper utilities.

import pygame
import sys
import random
from dataclasses import dataclass
from typing import List, Optional, Callable, Tuple

# ---------- Pygame / UI Setup ----------
pygame.init()
SCREEN_W, SCREEN_H = 1200, 750
FULLSCREEN = False
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()
FPS = 30

# Fonts
FONT = pygame.font.SysFont("arial", 16)
BIG = pygame.font.SysFont("arial", 24)
HEADER = pygame.font.SysFont("arial", 28, bold=True)

# ---------- Bias & Nerf ----------
# RCB bias (multiplicative factor applied to bat/bowl influences)
RCB_BIAS = 1.0     # no team bias; ratings stay realistic
# Special per-player nerf for Digvesh Rathi
DIGVESH_NERF = 1.0  # no special nerf; ratings stay realistic

# ---------- Data Models ----------
@dataclass
class Player:
    name: str
    batting: int
    bowling: int
    fielding: int
    is_keeper: bool = False

@dataclass
class BatsmanInnings:
    player: Player
    runs: int = 0
    balls_faced: int = 0
    outs: int = 0

@dataclass
class BowlerInnings:
    player: Player
    balls_bowled: int = 0
    wickets: int = 0
    runs_conceded: int = 0

@dataclass
class Team:
    name: str
    players: List[Player]

# ---------- Helper: apply bias/nerf to a rating ----------
def apply_bias_and_nerf(team_name: str, player_name: str, rating: float, kind: str="bat") -> float:
    """
    Apply RCB bias if team is RCB and apply Digvesh Rathi nerf if player matches.
    'kind' parameter reserved for future mode-specific adjustments (e.g., T20 bonus).
    Returns modified rating (float).
    """
    r = float(rating)
    if team_name == "Royal Challengers Bangalore":
        r *= RCB_BIAS
    if player_name.strip().lower() == "Digvesh Rathi":
        r *= DIGVESH_NERF
    return r

# ---------- Utility: Rounded rect and text ----------
def draw_text(surface: pygame.Surface, text: str, pos: Tuple[int,int], font=FONT, color=(0,0,0)):
    surf = font.render(str(text), True, color)
    surface.blit(surf, pos)

def rounded_rect(surface: pygame.Surface, rect: Tuple[int,int,int,int], color: Tuple[int,int,int,int], radius: int=8):
    x, y, w, h = rect
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(tmp, color, (0,0,w,h), border_radius=radius)
    surface.blit(tmp, (x,y))

# ---------- Create grass texture ----------
# ---------- Futuristic UI helpers ----------
NEON_CYAN = (0, 230, 255)
NEON_GREEN = (85, 255, 170)
NEON_GOLD = (255, 215, 80)
PANEL_DARK = (7, 14, 28, 220)
PANEL_MID = (14, 31, 58, 230)


def draw_centered_text(surface: pygame.Surface, text: str, rect, font=FONT, color=(255, 255, 255)):
    surf = font.render(str(text), True, color)
    text_rect = surf.get_rect(center=pygame.Rect(rect).center)
    surface.blit(surf, text_rect)


def draw_neon_background(title: str = None, subtitle: str = None):
    screen.fill((3, 7, 18))
    screen.blit(GRASS_SURFACE, (0, 0))
    dark = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    dark.fill((0, 5, 16, 195))
    screen.blit(dark, (0, 0))

    for x in range(0, SCREEN_W, 80):
        pygame.draw.line(screen, (0, 130, 160), (x, 0), (x + 120, SCREEN_H), 1)
    for y in range(70, SCREEN_H, 70):
        pygame.draw.line(screen, (0, 70, 110), (0, y), (SCREEN_W, y), 1)

    pygame.draw.rect(screen, (0, 220, 255), (0, 0, SCREEN_W, 4))
    pygame.draw.rect(screen, (85, 255, 170), (0, SCREEN_H - 4, SCREEN_W, 4))

    if title:
        shadow = HEADER.render(title, True, (0, 60, 90))
        text = HEADER.render(title, True, (225, 250, 255))
        screen.blit(shadow, shadow.get_rect(center=(SCREEN_W // 2 + 3, 82 + 3)))
        screen.blit(text, text.get_rect(center=(SCREEN_W // 2, 82)))
    if subtitle:
        sub = FONT.render(subtitle, True, (160, 235, 245))
        screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 122)))



def draw_match_background(title: str, subtitle: str):
    screen.fill((2, 5, 15))
    for x in range(0, SCREEN_W, 64):
        pygame.draw.line(screen, (0, 65, 95), (x, 0), (x, SCREEN_H), 1)
    for y in range(0, SCREEN_H, 64):
        pygame.draw.line(screen, (0, 45, 75), (0, y), (SCREEN_W, y), 1)
    for x in range(-SCREEN_H, SCREEN_W, 90):
        pygame.draw.line(screen, (0, 95, 125), (x, SCREEN_H), (x + SCREEN_H, 0), 1)

    pygame.draw.rect(screen, NEON_CYAN, (0, 0, SCREEN_W, 4))
    pygame.draw.rect(screen, NEON_GREEN, (0, SCREEN_H - 4, SCREEN_W, 4))
    pygame.draw.circle(screen, (0, 150, 180), (SCREEN_W - 120, 100), 68, 1)
    pygame.draw.circle(screen, (0, 90, 130), (SCREEN_W - 120, 100), 102, 1)

    title_surf = HEADER.render(title, True, (230, 255, 255))
    screen.blit(title_surf, (28, 22))
    sub_surf = FONT.render(subtitle, True, (150, 230, 240))
    screen.blit(sub_surf, (30, 58))


def neon_panel(surface: pygame.Surface, rect, border=NEON_CYAN, fill=PANEL_DARK, radius: int = 10):
    rect_obj = pygame.Rect(rect)
    glow = pygame.Surface((rect_obj.w + 14, rect_obj.h + 14), pygame.SRCALPHA)
    pygame.draw.rect(glow, (*border, 32), glow.get_rect(), border_radius=radius + 4)
    surface.blit(glow, (rect_obj.x - 7, rect_obj.y - 7))
    rounded_rect(surface, rect_obj, fill, radius=radius)
    pygame.draw.rect(surface, border, rect_obj, 2, border_radius=radius)

def toggle_fullscreen():
    global screen, FULLSCREEN
    FULLSCREEN = not FULLSCREEN
    if FULLSCREEN:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))


class Button:
    def __init__(self, rect, label: str, accent=NEON_CYAN, font=BIG):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.accent = accent
        self.font = font

    def draw(self, surface: pygame.Surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        if hovered:
            glow = pygame.Surface((self.rect.w + 18, self.rect.h + 18), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*self.accent, 70), glow.get_rect(), border_radius=12)
            surface.blit(glow, (self.rect.x - 9, self.rect.y - 9))

        fill = (18, 42, 72, 235) if hovered else PANEL_DARK
        rounded_rect(surface, self.rect, fill, radius=10)
        border = self.accent if hovered else (35, 115, 145)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=10)
        draw_centered_text(surface, self.label, self.rect, self.font, (235, 255, 255))
        return hovered

    def clicked(self, event) -> bool:
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def make_menu_buttons(items, start_y=180, width=360, height=56, gap=18):
    x = (SCREEN_W - width) // 2
    return [Button((x, start_y + i * (height + gap), width, height), label, accent) for i, (label, accent) in enumerate(items)]

def create_grass_texture(width: int, height: int) -> pygame.Surface:
    grass = pygame.Surface((width, height))
    # base gradient
    for y in range(height):
        g = 60 + int(90 * (y / max(1, height)))
        pygame.draw.line(grass, (8, g, 8), (0, y), (width, y))
    # subtle stripes
    stripe_w = 12
    for x in range(0, width, stripe_w):
        shade = 8 if (x // stripe_w) % 2 == 0 else 0
        stripe = pygame.Surface((stripe_w, height), pygame.SRCALPHA)
        stripe.fill((0, shade, 0, 40))
        grass.blit(stripe, (x, 0))
    # add a few blades accents
    for i in range(0, width, 16):
        pygame.draw.line(grass, (20,120,20), (i, height-6), (i+6, height-22), 1)
    return grass

GRASS_SURFACE = create_grass_texture(SCREEN_W, SCREEN_H)

# ---------- IPL 2025 Teams (Final XIs) ----------
# Ratings: keep same style as earlier project (bat ~ 20-100, bowl ~ 10-95, field ~ 68-90)
# For players appearing in original Test3.py, I kept numbers consistent where provided earlier.
ALL_TEAMS = {
    # RCB
    "Royal Challengers Bangalore": lambda: Team("Royal Challengers Bangalore", [
        Player("Virat Kohli", 96, 15, 82),
        Player("AB de Villiers", 96, 20, 80),
        Player("Phil Salt", 88, 10, 78),
        Player("Rajat Patidar", 86, 25, 73),
        Player("Jitesh Sharma", 82, 15, 72),
        Player("Tim David", 84, 45, 70),
        Player("Krunal Pandya", 78, 82, 75),
        Player("Suyash Sharma", 55, 84, 70),
        Player("Bhuvneshwar Kumar", 40, 86, 77),
        Player("Josh Hazlewood", 30, 90, 76),
        Player("Yash Dayal", 25, 82, 70),
    ]),

    # CSK
    "Chennai Super Kings": lambda: Team("Chennai Super Kings", [
        Player("Ayush Mhatre", 72, 82, 80),
        Player("Sanju Samson", 88, 12, 76),
        Player("Ruturaj Gaikwad", 89, 15, 80),
        Player("Rachin Ravindra", 78, 70, 85),
        Player("Sarfaraz Khan", 92, 20, 78),
        Player("Dewald Brevis", 85, 25, 74),
        Player("Shivam Dube", 83, 45, 72),
        Player("MS Dhoni", 80, 10, 88, True),
        Player("Khaleel Ahmed", 35, 86, 75),
        Player("Matt Henry", 25, 87, 73),
        Player("Noor Ahmed", 40, 84, 70),
    ]),

    # MI (Hardik Pandya added, Naman Dhir removed)
    "Mumbai Indians": lambda: Team("Mumbai Indians", [
        Player("Rohit Sharma", 94, 12, 83),
        Player("Ryan Rickelton", 86, 10, 76),
        Player("Quinton Dekock", 88, 35, 75),
        Player("Suryakumar Yadav", 96, 18, 82),
        Player("Tilak Varma", 84, 25, 75),
        Player("Hardik Pandya", 86, 72, 80),
        Player("Corbin Bosch", 78, 72, 74),
        Player("Mohummad Nabi", 50, 82, 74),
        Player("Mitchell Santner", 70, 80, 80),
        Player("Jasprit Bumrah", 40, 96, 82),
        Player("Trent Boult", 38, 92, 80),
        
    ]),

    # DC (Axar captain inside match logic later; XI as finalized)
    "Delhi Capitals": lambda: Team("Delhi Capitals", [
        Player("KL Rahul", 92, 10, 81),
        Player("Axar abd Patel", 99, 40, 75),
        Player("Faf du Plessis", 91, 12, 80),
        Player("Abishek Porel", 78, 8, 74, True),
        Player("Karun Nair", 82, 20, 73),
        Player("Tristan Stubbs", 84, 30, 77),
        Player("Ashthosh Sharma", 75, 85, 75),
        Player("Vipraj Nigam", 60, 85, 77),
        Player("Mitchell Starc", 40, 98, 80),
        Player("Kuldeep Yadav", 40, 88, 78),
        Player("Auqib Nabi", 56, 82, 72),
    ]),

    # LSG (Pant captain/wk inside match logic later)
    "Lucknow Super Giants": lambda: Team("Lucknow Super Giants", [
        Player("Mitchell Marsh", 84, 65, 78),
        Player("Aiden Markram", 85, 45, 77),
        Player("Matthew Breetzke", 82, 40, 75),
        Player("Nicholas Pooran", 89, 20, 80),
        Player("Rishabh Pant", 90, 15, 83, True),
        Player("Ayush Badoni", 78, 25, 72),
        Player("David Miller", 88, 30, 78),
        Player("Shardul Thakur", 60, 78, 75),
        Player("Digvesh Rathi", 25, 82, 70),
        Player("Will O'Rourke", 28, 86, 74),
        Player("Ravi Bishnoi", 35, 88, 76),
    ]),

    # KKR
    "Kolkata Knight Riders": lambda: Team("Kolkata Knight Riders", [
        Player("Finn Allen", 89, 10, 82, True),
        Player("Tim Seifert", 70, 85, 80),
        Player("Sunil Narine", 85, 50, 75),
        Player("Ajinkya Rahane", 83, 15, 78),
        Player("Angkrish Raghuvanshi", 77, 20, 74),
        Player("Rinku Singh", 86, 20, 80),
        Player("Ramandeep Singh", 78, 55, 74),
        Player("Andre Russell", 88, 80, 79),
        Player("Harshit Rana", 45, 85, 72),
        Player("Varun Chakravarthy", 30, 88, 75),
        Player("Vaibhav Arora", 35, 84, 74),
    ]),

    # SRH
    "Sunrisers Hyderabad": lambda: Team("Sunrisers Hyderabad", [
        Player("Abishek Sharma", 90, 15, 73),
        Player("Travis Head", 92, 25, 78),
        Player("Ishan Kishan", 88, 10, 82, True),
        Player("Nithish Kumar", 80, 22, 74),
        Player("Liam Livingstone", 76, 65, 74),
        Player("Heinrich Klaasen", 87, 20, 78),
        Player("Aniket Verma", 75, 50, 72),
        Player("Pat Cummins", 50, 90, 80),
        Player("Harsh Dubey", 45, 82, 72),
        Player("Mohammed Shami", 30, 92, 80),
        Player("Eshan Malinga", 28, 85, 70),
    ]),

    # RR
    "Rajasthan Royals": lambda: Team("Rajasthan Royals", [
        Player("Yashasvi Jaiswal", 90, 20, 80),
        Player("Vaibhav Suryavanshi", 78, 18, 73),
        Player("Riyan Parag", 83, 40, 78),
        Player("Shimron Hetmyer", 87, 25, 77),
        Player("Dhruv Jurel", 80, 15, 76, True),
        Player("Ravindra Jadeja", 89, 98, 84),
        Player("Sam Curran", 79, 85, 75),
        Player("Ravichandran Ashwin", 50, 88, 80),
        Player("Avesh Khan", 30, 87, 74),
        Player("Jofra Archer", 28, 95, 73),
        Player("Nandre Burger", 25, 86, 72),
    ]),

    # PBKS
    "Punjab Kings": lambda: Team("Punjab Kings", [
        Player("Prabhsimran Singh", 90, 10, 75, True),
        Player("Priyansh Arya", 90, 15, 73),
        Player("Cooper Connoly", 89, 70, 75),
        Player("Shreyas Iyer", 90, 18, 79),
        Player("Nehal Wadhera", 79, 20, 77),
        Player("Shashank Singh", 82, 50, 76),
        Player("Marcus Stoinis", 83, 72, 78),
        Player("Marco Jansen", 55, 85, 77),
        Player("Arshdeep Singh", 35, 88, 76),
        Player("Yuzvindra Chahal", 30, 86, 74),
        Player("Xavier Bartlett", 40, 82, 75),
    ]),

    # GT
    "Gujarat Titans": lambda: Team("Gujarat Titans", [
        Player("Shubman Gill", 93, 10, 82),
        Player("Sai Sudharsan", 84, 15, 76),
        Player("Jos Buttler", 90, 12, 82, True),
        Player("Shahrukh Khan", 80, 20, 74),
        Player("Sherfane Rutherford", 82, 60, 75),
        Player("Washington Sundar", 78, 70, 78),
        Player("Rahul Tewatia", 80, 60, 76),
        Player("Rashid Khan", 70, 92, 85),
        Player("Prasidh Krishna", 30, 86, 74),
        Player("Mohammed Siraj", 28, 88, 75),
        Player("Sai Kishore", 35, 84, 74),
    ]),
}

# ---------- Convenience: list of team names ----------
TEAM_NAMES = list(ALL_TEAMS.keys())

# IPL_Sim_part2.py - Part 2/2
# Contains: Innings, Match classes, ball simulation, GUI rendering,
# scorecard, menu logic, league/worldcup, Player-of-the-Match, and main loop.
# Works with Part 1 definitions (ALL_TEAMS, apply_bias_and_nerf, GRASS_SURFACE, etc.)

import math
import time

# ------------------- INNINGS -------------------
class Innings:
    def __init__(self, batting_team: Team, bowling_team: Team, format_type="T20"):
        self.batting_team = batting_team
        self.bowling_team = bowling_team
        self.runs = 0
        self.wickets = 0
        self.balls = 0
        self.current_batsmen = [0, 1]
        self.next_batsman_idx = 2
        self.completed = False
        self.declared = False
        self.format_type = format_type

        if format_type == "Test":
            self.max_balls = None
        elif format_type == "ODI":
            self.max_balls = 50 * 6
        elif format_type == "T20":
            self.max_balls = 20 * 6
        else:
            self.max_balls = 20 * 6

        self.batsmen_stats = [BatsmanInnings(p) for p in batting_team.players]
        self.bowler_stats = [BowlerInnings(p) for p in bowling_team.players]
        self.current_over_bowler_idx = None
        self.last_over_bowler_idx = None
        self.manual_next_bowler_idx = None
        self.ball_history = []

    def _is_abd(self, name: str) -> bool:
        n = name.lower().replace(".", "").replace(" ", "")
        return ("abd" in n) or ("devilliers" in n) or ("abdevilliers" in n)

    def _max_overs_per_bowler(self):
        if self.format_type == "T20":
            return 4
        elif self.format_type == "ODI":
            return 10
        else:
            return None

    def _overs_bowled_by(self, bowler_idx):
        b = self.bowler_stats[bowler_idx].balls_bowled
        return b // 6

    def get_eligible_bowler_indices(self):
        num_bowlers = len(self.bowler_stats)

        if num_bowlers > 5:
            pool = list(range(5, num_bowlers))
        else:
            pool = list(range(num_bowlers))

        max_overs = self._max_overs_per_bowler()

        if max_overs is not None:
            eligible = [i for i in pool if self._overs_bowled_by(i) < max_overs]
            if not eligible:
                eligible = list(pool)
        else:
            eligible = list(pool)

        if self.last_over_bowler_idx in eligible and len(eligible) > 1:
            eligible = [i for i in eligible if i != self.last_over_bowler_idx]

        if not eligible:
            eligible = list(range(num_bowlers))
            if self.last_over_bowler_idx in eligible and len(eligible) > 1:
                eligible = [i for i in eligible if i != self.last_over_bowler_idx]

        return eligible

    def set_next_over_bowler(self, bowler_idx: int) -> bool:
        if self.completed or self.balls % 6 != 0 or self.current_over_bowler_idx is not None:
            return False
        if bowler_idx not in self.get_eligible_bowler_indices():
            return False
        self.manual_next_bowler_idx = bowler_idx
        return True

    def _choose_new_over_bowler(self):
        if self.manual_next_bowler_idx is not None:
            chosen = self.manual_next_bowler_idx
            self.manual_next_bowler_idx = None
            return chosen
        return random.choice(self.get_eligible_bowler_indices())

    def ball_event(self, target=None, match_total_balls: int = None):

        if self.completed:
            return None

        # Test match cap
        if self.format_type == "Test" and (match_total_balls is not None) and match_total_balls >= 2700:
            self.completed = True
            return None

        ball_in_over = self.balls % 6
        if ball_in_over == 0:
            self.current_over_bowler_idx = self._choose_new_over_bowler()

        striker_idx = self.current_batsmen[0]
        striker = self.batsmen_stats[striker_idx]
        bowler = self.bowler_stats[self.current_over_bowler_idx]

        # AB special case
        if self._is_abd(striker.player.name):
            weights = {"W": 0.5, "0": 15, "1": 2, "2": 8, "3": 2, "4": 5, "6": 2}
            outcome = random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]

        else:
            bat_rating = striker.player.batting + random.randint(-10, 10)
            bowl_rating = bowler.player.bowling + random.randint(-12, 12)

            if self.format_type == "ODI":
                bat_rating += 10
            elif self.format_type == "T20":
                bat_rating += 20

            bat_rating = apply_bias_and_nerf(self.batting_team.name, striker.player.name, bat_rating, kind="bat")
            bowl_rating = apply_bias_and_nerf(self.bowling_team.name, bowler.player.name, bowl_rating, kind="bowl")

            wicket_chance = max(1, min(8, (bowl_rating - bat_rating + 50) // 25))
            base_weights = {"W": wicket_chance, "0": 58, "1": 22, "2": 10, "3": 2, "4": 7, "6": 1}

            if self.batting_team.name == "Royal Challengers Bangalore":
                base_weights["4"] += 3
                base_weights["6"] += 2

            if self.batting_team.name == "Sunrisers Hyderabad":
                base_weights["4"] += 5
                base_weights["6"] += 4

            if self.format_type == "ODI":
                base_weights["1"] += 6
                base_weights["2"] += 4
                base_weights["3"] += 3
                base_weights["4"] += 5
                base_weights["6"] += 3

            elif self.format_type == "T20":
                base_weights["1"] += 4
                base_weights["2"] += 6
                base_weights["3"] += 4
                base_weights["4"] += 12
                base_weights["6"] += 15

            # Death overs
            over_number = self.balls // 6
            is_death = False

            if self.format_type == "T20" and over_number >= 15:
                is_death = True
            if self.format_type == "ODI" and over_number >= 40:
                is_death = True

            if is_death:
                bat_skill = striker.player.batting

                base_weights["4"] += 8
                base_weights["6"] += 10
                base_weights["0"] -= 8
                base_weights["1"] -= 4

                if self.format_type == "ODI":
                    base_weights["6"] -= 2
                    base_weights["2"] += 4

                if bat_skill >= 85:
                    base_weights["W"] -= 1
                    base_weights["4"] += 4
                    base_weights["6"] += 5
                elif bat_skill >= 65:
                    base_weights["W"] += 2
                    base_weights["6"] += 3
                else:
                    base_weights["W"] += 5
                    base_weights["4"] += 2
                    base_weights["6"] += 2

            for k in base_weights:
                if base_weights[k] < 1:
                    base_weights[k] = 1

            outcome = random.choices(
                list(base_weights.keys()),
                weights=list(base_weights.values()),
                k=1
            )[0]

        # Apply outcome
        self.balls += 1
        bowler.balls_bowled += 1
        striker.balls_faced += 1

        if outcome == "W":
            self.wickets += 1
            bowler.wickets += 1
            striker.outs += 1

            if self.next_batsman_idx < len(self.batsmen_stats):
                self.current_batsmen[0] = self.next_batsman_idx
                self.next_batsman_idx += 1
            else:
                self.completed = True

            if self.balls % 6 == 0:
                self.last_over_bowler_idx = self.current_over_bowler_idx
                self.current_over_bowler_idx = None

            if self.max_balls and self.balls >= self.max_balls:
                self.completed = True

            self.ball_history.append("W")
            return ("W", 0)

        runs = int(outcome)
        self.runs += runs
        striker.runs += runs
        bowler.runs_conceded += runs

        if runs % 2 == 1:
            self.current_batsmen.reverse()

        if self.balls % 6 == 0:
            self.last_over_bowler_idx = self.current_over_bowler_idx
            self.current_over_bowler_idx = None
            self.current_batsmen.reverse()

        if target is not None and self.runs > target:
            self.completed = True

        if self.max_balls and self.balls >= self.max_balls:
            self.completed = True

        self.ball_history.append(str(runs))
        return ("RUN", runs)
# ------------------- MATCH -------------------
class Match:
    def __init__(self, team_a: Team, team_b: Team, format_type="T20"):
        self.team_a = team_a
        self.team_b = team_b
        self.format_type = format_type
        self.innings_list: List[Innings] = []
        self.follow_on = False
        self.match_over = False
        self.result_text: Optional[str] = None
        self.total_balls = 0
        # start first innings with team_a batting
        self.start_innings(team_a, team_b)

    def start_innings(self, batting_team: Team, bowling_team: Team):
        self.innings_list.append(Innings(batting_team, bowling_team, self.format_type))

    def current_innings(self) -> Innings:
        return self.innings_list[-1]

    def declare_current(self) -> bool:
        inn = self.current_innings()
        if self.format_type == "Test" and not inn.completed and not inn.declared:
            if inn.balls >= 12:  # minimal overs before declaring
                inn.declared = True
                inn.completed = True
                return True
        return False

    def step_ball(self):
        if self.match_over:
            return
        inn = self.current_innings()
        target = None
        is_limited_overs_chase = self.format_type != "Test" and len(self.innings_list) == 2
        is_test_fourth_innings = self.format_type == "Test" and len(self.innings_list) == 4
        if is_limited_overs_chase or is_test_fourth_innings:
            opponent_total = sum(prev.runs for prev in self.innings_list[:-1] if prev.batting_team.name != inn.batting_team.name)
            batting_team_previous_total = sum(prev.runs for prev in self.innings_list[:-1] if prev.batting_team.name == inn.batting_team.name)
            target = opponent_total - batting_team_previous_total

        outcome = inn.ball_event(target=target, match_total_balls=self.total_balls)

        if outcome is not None:
            self.total_balls += 1

        # Test match long cap
        if self.format_type == "Test" and self.total_balls >= 2700:
            # decide by totals
            team_a_total = sum(innx.runs for innx in self.innings_list if innx.batting_team.name == self.team_a.name)
            team_b_total = sum(innx.runs for innx in self.innings_list if innx.batting_team.name == self.team_b.name)
            if team_a_total > team_b_total:
                diff = team_a_total - team_b_total
                self.match_over = True
                self.result_text = f"{self.team_a.name} won by {diff} runs (Match ended at 450 overs cap)"
            elif team_b_total > team_a_total:
                last_inn = self.innings_list[-1]
                if last_inn.batting_team.name == self.team_b.name:
                    wickets_lost = last_inn.wickets
                    wickets_remaining = 10 - wickets_lost
                    self.match_over = True
                    self.result_text = f"{self.team_b.name} won by {wickets_remaining} wickets (Match ended at 450 overs cap)"
                else:
                    self.match_over = True
                    self.result_text = f"{self.team_b.name} won by runs (Match ended at 450 overs cap)"
            else:
                self.match_over = True
                self.result_text = "Match drawn (450 overs cap reached)"
            return

        # when innings completed, progress innings / result
        if inn.completed:
            if self.format_type == "Test":
                # many branches for follow-on/innings
                if len(self.innings_list) == 1:
                    self.start_innings(self.team_b, self.team_a)
                    return
                if len(self.innings_list) == 2:
                    first = self.innings_list[0]
                    second = self.innings_list[1]
                    lead = first.runs - second.runs
                    if lead >= 200:
                        self.follow_on = True
                        self.start_innings(second.batting_team, second.bowling_team)
                        return
                    else:
                        self.follow_on = False
                        self.start_innings(first.batting_team, first.bowling_team)
                        return
                if len(self.innings_list) == 3:
                    if self.follow_on:
                        team1_runs = self.innings_list[0].runs
                        team2_first = self.innings_list[1].runs
                        team2_second = self.innings_list[2].runs
                        if (team2_first + team2_second) < team1_runs:
                            diff = team1_runs - (team2_first + team2_second)
                            self.match_over = True
                            self.result_text = f"{self.team_a.name} won by an innings and {diff} runs"
                            return
                        else:
                            self.follow_on = False
                            self.start_innings(self.team_a, self.team_b)
                            return
                    else:
                        self.start_innings(self.team_b, self.team_a)
                        return
                if len(self.innings_list) == 4:
                    fourth = self.innings_list[3]
                    batting_total = sum(innx.runs for innx in self.innings_list if innx.batting_team.name == fourth.batting_team.name)
                    bowling_total = sum(innx.runs for innx in self.innings_list if innx.batting_team.name == fourth.bowling_team.name)
                    if batting_total > bowling_total:
                        wickets_remaining = 10 - fourth.wickets
                        self.match_over = True
                        self.result_text = f"{fourth.batting_team.name} won by {wickets_remaining} wickets"
                    elif bowling_total > batting_total:
                        diff = bowling_total - batting_total
                        self.match_over = True
                        self.result_text = f"{fourth.bowling_team.name} won by {diff} runs"
                    else:
                        self.match_over = True
                        self.result_text = "Match drawn"
                    return
            else:
                # limited overs: 2 innings max
                max_inns = 2
                if len(self.innings_list) < max_inns:
                    if len(self.innings_list) % 2 == 1:
                        self.start_innings(self.team_b, self.team_a)
                    else:
                        self.start_innings(self.team_a, self.team_b)
                else:
                    team_a_total = sum(inn.runs for inn in self.innings_list if inn.batting_team.name == self.team_a.name)
                    team_b_total = sum(inn.runs for inn in self.innings_list if inn.batting_team.name == self.team_b.name)
                    if team_a_total > team_b_total:
                        self.match_over = True
                        self.result_text = f"{self.team_a.name} won by {team_a_total - team_b_total} runs"
                    elif team_b_total > team_a_total:
                        last = self.innings_list[-1]
                        wickets_lost = last.wickets
                        wickets_remaining = 10 - wickets_lost
                        self.match_over = True
                        self.result_text = f"{self.team_b.name} won by {wickets_remaining} wickets"
                    else:
                        self.match_over = True
                        self.result_text = "Match tied"

    def summary(self) -> str:
        lines = []
        for i, inn in enumerate(self.innings_list, start=1):
            dec = " (Declared)" if inn.declared else ""
            lines.append(f"Innings {i} - {inn.batting_team.name}: {inn.runs}/{inn.wickets}{dec} in {inn.balls//6}.{inn.balls%6} overs")
        return "\n".join(lines)

    def match_result(self) -> Optional[str]:
        if self.match_over and self.result_text:
            return self.result_text
        if self.format_type == "Test":
            return None
        total_a = sum(inn.runs for inn in self.innings_list if inn.batting_team.name == self.team_a.name)
        total_b = sum(inn.runs for inn in self.innings_list if inn.batting_team.name == self.team_b.name)
        if len(self.innings_list) >= 2 and all(inn.completed for inn in self.innings_list[:2]):
            if total_a > total_b:
                return f"{self.team_a.name} win by {total_a - total_b} runs"
            elif total_b > total_a:
                return f"{self.team_b.name} win by {total_b - total_a} runs"
            else:
                return "Match drawn"
        return None

# ------------------- PLAYER OF THE MATCH -------------------
def get_player_of_match(match: Match):
    stats = {}
    for inn in match.innings_list:
        team = inn.batting_team.name
        for b in inn.batsmen_stats:
            key = (b.player.name, team)
            if key not in stats:
                stats[key] = {"runs": 0, "balls": 0, "wickets": 0, "runs_conceded": 0, "balls_bowled": 0}
            stats[key]["runs"] += b.runs
            stats[key]["balls"] += b.balls_faced
        for bw in inn.bowler_stats:
            key = (bw.player.name, inn.bowling_team.name)
            if key not in stats:
                stats[key] = {"runs": 0, "balls": 0, "wickets": 0, "runs_conceded": 0, "balls_bowled": 0}
            stats[key]["wickets"] += bw.wickets
            stats[key]["runs_conceded"] += bw.runs_conceded
            stats[key]["balls_bowled"] += bw.balls_bowled

    best = None
    best_impact = -1e9
    best_display = None

    for (name, team), s in stats.items():
        runs = s["runs"]
        balls = s["balls"]
        wickets = s["wickets"]
        runs_conceded = s["runs_conceded"]
        balls_bowled = s["balls_bowled"]

        strike_rate = (runs / balls * 100) if balls > 0 else 0.0
        economy = (runs_conceded / (balls_bowled / 6)) if balls_bowled > 0 else 0.0

        impact = runs + (strike_rate / 2.0) + (wickets * 25.0) - (economy * 5.0)

        if impact > best_impact:
            best_impact = impact
            best = (name, team, runs, balls, wickets, strike_rate, economy)
            best_display = f"{name} ({team}) - {runs} runs ({balls} balls), {wickets} wkts, SR:{strike_rate:.1f}, Econ:{economy:.2f}"

    if best:
        return best[0], best[1], best_display
    return None, None, None

# ------------------- GUI RENDER -------------------
def ball_marker_color(label: str):
    if label == "W":
        return (255, 70, 90), (45, 8, 18)
    if label == "6":
        return (190, 95, 255), (32, 12, 58)
    if label == "4":
        return (80, 255, 150), (10, 48, 28)
    return (225, 245, 255), (14, 30, 48)


def draw_ball_tracker(surface: pygame.Surface, innings: Innings):
    tracker_rect = (812, 450, 350, 160)
    neon_panel(surface, tracker_rect, border=(190, 95, 255), fill=(6, 12, 28, 238), radius=12)
    draw_text(surface, "BALL TRACKER", (832, 468), FONT, (230, 240, 255))
    draw_text(surface, "Recent deliveries", (1012, 468), FONT, (155, 210, 225))

    recent = innings.ball_history[-18:]
    if not recent:
        draw_text(surface, "No balls yet", (832, 520), BIG, (145, 205, 220))
        return

    start_x = 838
    start_y = 504
    gap = 48
    radius = 18
    for i, label in enumerate(recent):
        row = i // 6
        col = i % 6
        cx = start_x + col * gap
        cy = start_y + row * 38
        color, fill = ball_marker_color(label)
        pygame.draw.circle(surface, (*color, 65), (cx, cy), radius + 5)
        pygame.draw.circle(surface, fill, (cx, cy), radius)
        pygame.draw.circle(surface, color, (cx, cy), radius, 2)
        text = FONT.render(label, True, color)
        surface.blit(text, text.get_rect(center=(cx, cy)))

    this_over = innings.ball_history[-(innings.balls % 6):] if innings.balls % 6 else innings.ball_history[-6:]
    over_text = " ".join(this_over) if this_over else "-"
    draw_text(surface, f"This over: {over_text}", (832, 586), FONT, (180, 235, 245))


def render_match(match: Match, scorecard_index: int, show_panel: bool, panel_progress: float, control_buttons=None):
    inn = match.current_innings()
    draw_match_background(f"{match.format_type} LIVE MATCH", f"{match.team_a.name} vs {match.team_b.name}")

    # Match identity panel
    left_box_rect = (18, 88, 560, 96)
    neon_panel(screen, left_box_rect, border=NEON_CYAN, fill=(5, 14, 30, 230), radius=12)
    draw_text(screen, "IPL SIMULATOR", (34, 104), BIG, (225, 255, 255))
    draw_text(screen, f"{match.team_a.name}  vs  {match.team_b.name}", (34, 134), FONT, (165, 235, 245))
    draw_text(screen, f"Rating multipliers: RCB x{RCB_BIAS}  |  Digvesh x{DIGVESH_NERF}", (34, 158), FONT, NEON_GOLD)

    # Live score command panel
    central_rect = (20, 205, 760, 214)
    neon_panel(screen, central_rect, border=NEON_GREEN, fill=(6, 18, 34, 235), radius=12)

    y = 220
    for line in match.summary().split("\n")[-4:]:
        draw_text(screen, line, (34, y), FONT, (175, 225, 235))
        y += 22

    draw_text(screen, "BATTING", (34, y + 8), FONT, (120, 220, 240))
    draw_text(screen, inn.batting_team.name, (34, y + 30), BIG, (235, 255, 255))

    score_rect = (286, y + 8, 168, 68)
    neon_panel(screen, score_rect, border=NEON_GOLD, fill=(16, 22, 34, 235), radius=10)
    draw_centered_text(screen, f"{inn.runs}/{inn.wickets}", score_rect, HEADER, NEON_GOLD)

    overs_rect = (474, y + 8, 142, 68)
    neon_panel(screen, overs_rect, border=NEON_CYAN, fill=(8, 20, 38, 235), radius=10)
    draw_centered_text(screen, f"{inn.balls//6}.{inn.balls%6} ov", overs_rect, BIG, (225, 255, 255))

    rr = (inn.runs / (inn.balls / 6)) if inn.balls else 0.0
    draw_text(screen, f"Run Rate: {rr:.2f}", (636, y + 16), FONT, (175, 235, 245))

    chase_target = None
    is_chase = (match.format_type != "Test" and len(match.innings_list) == 2) or (match.format_type == "Test" and len(match.innings_list) == 4)
    if is_chase:
        opponent_total = sum(prev.runs for prev in match.innings_list[:-1] if prev.batting_team.name != inn.batting_team.name)
        batting_previous = sum(prev.runs for prev in match.innings_list[:-1] if prev.batting_team.name == inn.batting_team.name)
        chase_target = opponent_total - batting_previous + 1
        needed = max(0, chase_target - inn.runs)
        balls_left = max(0, (inn.max_balls or inn.balls) - inn.balls) if match.format_type != "Test" else None
        draw_text(screen, f"Target: {chase_target}", (636, y + 40), FONT, NEON_GOLD)
        if balls_left is not None and balls_left > 0:
            rrr = needed / (balls_left / 6)
            draw_text(screen, f"Need {needed} from {balls_left} | RRR {rrr:.2f}", (518, y + 92), FONT, (255, 210, 130))
        else:
            draw_text(screen, f"Need {needed}", (636, y + 64), FONT, (255, 210, 130))

    # Batter and bowler panels
    player_panel = (18, 450, 760, 160)
    neon_panel(screen, player_panel, border=NEON_CYAN, fill=(5, 14, 30, 230), radius=12)
    try:
        b1 = inn.batsmen_stats[inn.current_batsmen[0]]
        b2 = inn.batsmen_stats[inn.current_batsmen[1]]
        draw_text(screen, "STRIKER", (36, 468), FONT, NEON_GREEN)
        draw_text(screen, f"{b1.player.name}  {b1.runs} ({b1.balls_faced})", (36, 492), BIG, (235, 255, 255))
        draw_text(screen, "NON-STRIKER", (36, 538), FONT, (130, 210, 235))
        draw_text(screen, f"{b2.player.name}  {b2.runs} ({b2.balls_faced})", (36, 562), BIG, (205, 235, 245))
    except Exception:
        pass

    try:
        if inn.current_over_bowler_idx is not None:
            curbow = inn.bowler_stats[inn.current_over_bowler_idx]
            overs = curbow.balls_bowled // 6
            balls = curbow.balls_bowled % 6
            draw_text(screen, "BOWLER", (430, 468), FONT, NEON_GOLD)
            draw_text(screen, f"{curbow.player.name}", (430, 492), BIG, (235, 255, 255))
            draw_text(screen, f"{overs}.{balls} ov  |  {curbow.wickets} wkts  |  {curbow.runs_conceded} runs", (430, 528), FONT, (175, 235, 245))
    except Exception:
        pass

    draw_text(screen, "SPACE next ball  |  S over  |  B choose bowler  |  P scorecard  |  D declare", (36, 620), FONT, (120, 205, 220))
    draw_ball_tracker(screen, inn)

    res = match.match_result()
    if res:
        result_rect = (600, 88, 560, 112)
        neon_panel(screen, result_rect, border=NEON_GOLD, fill=(24, 20, 10, 235), radius=12)
        draw_text(screen, "RESULT", (620, 106), FONT, NEON_GOLD)
        draw_text(screen, res, (620, 132), BIG, (255, 245, 210))

        potm_name, potm_team, potm_display = get_player_of_match(match)
        if potm_display:
            draw_text(screen, "Player of the Match", (620, 166), FONT, (255, 230, 140))
            draw_text(screen, potm_display[:62], (760, 166), FONT, (255, 245, 210))

    # right panel (scorecard)
    panel_width = 420
    closed_x = SCREEN_W
    open_x = SCREEN_W - panel_width - 16
    panel_x = int(closed_x + (open_x - closed_x) * panel_progress)
    panel_y = 18
    panel_h = SCREEN_H - 36
    panel_surf = pygame.Surface((panel_width, panel_h), pygame.SRCALPHA)
    neon_panel(panel_surf, (0, 0, panel_width, panel_h), border=NEON_CYAN, fill=(5, 12, 26, 242), radius=12)

    draw_text(panel_surf, "FULL SCORECARD", (18, 16), HEADER, (230, 255, 255))
    y_offset = 56
    if 0 <= scorecard_index < len(match.innings_list):
        inn_score = match.innings_list[scorecard_index]
        dec = " (Declared)" if inn_score.declared else ""
        draw_text(panel_surf, f"Innings {scorecard_index+1} - {inn_score.batting_team.name}{dec}", (18, y_offset), FONT, NEON_GOLD)
        y_offset += 22
        draw_text(panel_surf, f"{inn_score.runs}/{inn_score.wickets} ({inn_score.balls//6}.{inn_score.balls%6})", (18, y_offset), BIG, (235, 255, 255))
        y_offset += 34
        draw_text(panel_surf, "Batsman", (18, y_offset), FONT, NEON_CYAN)
        draw_text(panel_surf, "R (B)", (300, y_offset), FONT, NEON_CYAN)
        y_offset += 20
        for b in inn_score.batsmen_stats:
            txt = f"{b.player.name[:22]:22}"
            draw_text(panel_surf, txt, (18, y_offset), FONT, (210, 238, 245))
            draw_text(panel_surf, f"{b.runs} ({b.balls_faced})", (300, y_offset), FONT, (230, 255, 255))
            y_offset += 18
            if y_offset > panel_h - 120:
                break

        y_offset += 8
        draw_text(panel_surf, "Bowling", (18, y_offset), FONT, NEON_GOLD)
        y_offset += 20
        draw_text(panel_surf, "Bowler", (18, y_offset), FONT, NEON_CYAN)
        draw_text(panel_surf, "O R W", (300, y_offset), FONT, NEON_CYAN)
        y_offset += 18
        for bow in inn_score.bowler_stats:
            overs = bow.balls_bowled // 6
            balls = bow.balls_bowled % 6
            draw_text(panel_surf, f"{bow.player.name[:24]:24}", (18, y_offset), FONT, (210, 238, 245))
            draw_text(panel_surf, f"{overs}.{balls} {bow.runs_conceded} {bow.wickets}", (300, y_offset), FONT, (230, 255, 255))
            y_offset += 18
            if y_offset > panel_h - 40:
                break

    screen.blit(panel_surf, (panel_x, panel_y))
    if control_buttons:
        mouse_pos = pygame.mouse.get_pos()
        for button in control_buttons:
            button.draw(screen, mouse_pos)

    pygame.display.flip()

# ------------------- MAIN LOOP & MENUS -------------------
def reset_match(team_a: Team, team_b: Team, format_type: str):
    return Match(team_a, team_b, format_type)



def can_choose_bowler(match: Match) -> bool:
    inn = match.current_innings()
    return (not match.match_over) and (not inn.completed) and inn.balls % 6 == 0 and inn.current_over_bowler_idx is None


def choose_over_bowler(match: Match) -> bool:
    inn = match.current_innings()
    if not can_choose_bowler(match):
        return False

    eligible = inn.get_eligible_bowler_indices()
    buttons = []
    card_w = 360
    card_h = 54
    start_x = (SCREEN_W - (card_w * 2 + 28)) // 2
    start_y = 170
    for i, bowler_idx in enumerate(eligible):
        bow = inn.bowler_stats[bowler_idx]
        col = i % 2
        row = i // 2
        rect = (start_x + col * (card_w + 28), start_y + row * 66, card_w, card_h)
        buttons.append((bowler_idx, Button(rect, bow.player.name, NEON_CYAN, FONT)))

    auto_button = Button((SCREEN_W // 2 - 185, 650, 170, 48), "AUTO", NEON_GOLD, FONT)
    cancel_button = Button((SCREEN_W // 2 + 15, 650, 170, 48), "CANCEL", (255, 85, 120), FONT)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        draw_match_background("CHOOSE BOWLER", f"{inn.bowling_team.name} bowling to {inn.batting_team.name}")
        draw_text(screen, "Pick the bowler for this over. Press A for auto or ESC to cancel.", (SCREEN_W // 2 - 235, 118), FONT, (165, 230, 240))

        for bowler_idx, button in buttons:
            bow = inn.bowler_stats[bowler_idx]
            button.draw(screen, mouse_pos)
            overs = bow.balls_bowled // 6
            balls = bow.balls_bowled % 6
            detail = f"Bowl {bow.player.bowling}  |  {overs}.{balls} ov  |  {bow.wickets}/{bow.runs_conceded}"
            draw_text(screen, detail, (button.rect.x + 18, button.rect.y + 31), FONT, (150, 220, 230))
            if bowler_idx == inn.last_over_bowler_idx:
                draw_text(screen, "LAST OVER", (button.rect.right - 88, button.rect.y + 12), FONT, NEON_GOLD)

        auto_button.draw(screen, mouse_pos)
        cancel_button.draw(screen, mouse_pos)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return False
                if e.key == pygame.K_f:
                    toggle_fullscreen()
                if e.key == pygame.K_a:
                    return False
                if pygame.K_1 <= e.key <= pygame.K_9:
                    idx = e.key - pygame.K_1
                    if idx < len(eligible):
                        return inn.set_next_over_bowler(eligible[idx])
                if e.key == pygame.K_0 and len(eligible) >= 10:
                    return inn.set_next_over_bowler(eligible[9])
            if e.type == pygame.MOUSEBUTTONDOWN:
                if auto_button.clicked(e):
                    return False
                if cancel_button.clicked(e):
                    return False
                for bowler_idx, button in buttons:
                    if button.clicked(e):
                        return inn.set_next_over_bowler(bowler_idx)
        clock.tick(FPS)

def get_match_control_buttons(match: Match, match_over: bool, block_until_menu: bool):
    if match_over:
        if block_until_menu:
            return [Button((SCREEN_W // 2 - 230, 688, 220, 44), "MAIN MENU", NEON_GREEN, FONT), Button((SCREEN_W // 2 + 10, 688, 220, 44), "FULLSCREEN", NEON_CYAN, FONT)]
        return []

    labels = [
        ("NEXT BALL", NEON_CYAN),
        ("SIM OVER", NEON_GREEN),
        ("SCORECARD", NEON_GOLD),
        ("RESET", (255, 170, 80)),
        ("FULLSCREEN", NEON_CYAN),
        ("QUIT", (255, 85, 120)),
    ]
    if can_choose_bowler(match):
        labels.insert(3, ("CHOOSE BOWLER", (190, 160, 255)))
    if match.format_type == "Test":
        labels.insert(3, ("DECLARE", (190, 160, 255)))

    width = 122
    gap = 12
    total_w = len(labels) * width + (len(labels) - 1) * gap
    x = (SCREEN_W - total_w) // 2
    y = 688
    return [Button((x + i * (width + gap), y, width, 44), label, accent, FONT) for i, (label, accent) in enumerate(labels)]

def match_loop(match: Match, block_until_menu: bool = True):
    current_scorecard_index = len(match.innings_list) - 1
    match_over = False
    show_panel = False
    panel_progress = 0.0
    panel_speed = 0.12

    while True:
        control_buttons = get_match_control_buttons(match, match_over, block_until_menu)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_f:
                    toggle_fullscreen()
                if match_over:
                    if block_until_menu and e.key == pygame.K_m:
                        return
                else:
                    if e.key == pygame.K_SPACE:
                        match.step_ball()
                    if e.key == pygame.K_s:
                        for _ in range(6):
                            match.step_ball()
                    if e.key == pygame.K_r:
                        match = reset_match(match.team_a, match.team_b, match.format_type)
                        current_scorecard_index = len(match.innings_list) - 1
                    if e.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    if e.key == pygame.K_LEFT:
                        current_scorecard_index = max(0, current_scorecard_index - 1)
                    if e.key == pygame.K_RIGHT:
                        current_scorecard_index = min(len(match.innings_list) - 1, current_scorecard_index + 1)
                    if e.key == pygame.K_d and match.format_type == "Test":
                        match.declare_current()
                    if e.key == pygame.K_p:
                        show_panel = not show_panel
                    if e.key == pygame.K_b and can_choose_bowler(match):
                        choose_over_bowler(match)
            if e.type == pygame.MOUSEBUTTONDOWN:
                for button in control_buttons:
                    if not button.clicked(e):
                        continue
                    if button.label == "MAIN MENU":
                        return
                    if button.label == "NEXT BALL":
                        match.step_ball()
                    elif button.label == "SIM OVER":
                        for _ in range(6):
                            match.step_ball()
                    elif button.label == "SCORECARD":
                        show_panel = not show_panel
                    elif button.label == "CHOOSE BOWLER" and can_choose_bowler(match):
                        choose_over_bowler(match)
                    elif button.label == "DECLARE" and match.format_type == "Test":
                        match.declare_current()
                    elif button.label == "RESET":
                        match = reset_match(match.team_a, match.team_b, match.format_type)
                        current_scorecard_index = len(match.innings_list) - 1
                        match_over = False
                    elif button.label == "FULLSCREEN":
                        toggle_fullscreen()
                    elif button.label == "QUIT":
                        pygame.quit()
                        sys.exit()
                    break

        if show_panel and panel_progress < 1.0:
            panel_progress = min(1.0, panel_progress + panel_speed)
        if (not show_panel) and panel_progress > 0.0:
            panel_progress = max(0.0, panel_progress - panel_speed)

        current_scorecard_index = min(current_scorecard_index, len(match.innings_list) - 1)
        control_buttons = get_match_control_buttons(match, match_over, block_until_menu)
        render_match(match, current_scorecard_index, show_panel, panel_progress, control_buttons)

        res = match.match_result()
        if res:
            match_over = True
            if block_until_menu:
                draw_text(screen, "Click MAIN MENU or press M", (SCREEN_W // 2 - 130, 730), FONT, (180, 240, 245))
                pygame.display.flip()
            else:
                draw_text(screen, "Match finished - preparing summary...", (400, 720), BIG, (8,40,65))
                pygame.display.flip()
                pygame.time.delay(800)
                return

        clock.tick(FPS)

# ------------------- MENU / Selection -------------------
def select_team(menu_title: str):
    selected = None
    keys = list(ALL_TEAMS.keys())
    cards = []
    card_w = 430
    card_h = 58
    start_x = (SCREEN_W - (card_w * 2 + 28)) // 2
    start_y = 160
    for i, team_name in enumerate(keys):
        col = i % 2
        row = i // 2
        rect = (start_x + col * (card_w + 28), start_y + row * 72, card_w, card_h)
        cards.append((team_name, Button(rect, team_name, NEON_CYAN, FONT)))

    while selected is None:
        mouse_pos = pygame.mouse.get_pos()
        draw_neon_background(menu_title, "Click a team card or use number keys")

        for i, (team_name, button) in enumerate(cards):
            button.draw(screen, mouse_pos)
            draw_text(screen, str((i + 1) % 10), (button.rect.x + 14, button.rect.y + 18), FONT, NEON_GOLD)

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_f:
                    toggle_fullscreen()
                elif pygame.K_1 <= e.key <= pygame.K_9:
                    idx = e.key - pygame.K_1
                    if idx < len(keys):
                        selected = ALL_TEAMS[keys[idx]]()
                elif e.key == pygame.K_0:
                    idx = 9
                    if idx < len(keys):
                        selected = ALL_TEAMS[keys[idx]]()
            if e.type == pygame.MOUSEBUTTONDOWN:
                for team_name, button in cards:
                    if button.clicked(e):
                        selected = ALL_TEAMS[team_name]()
                        break
        clock.tick(FPS)
    return selected

def select_format():
    options = [
        ("Test", NEON_CYAN),
        ("ODI", NEON_GREEN),
        ("T20", NEON_GOLD),
    ]
    buttons = make_menu_buttons(options, start_y=210, width=320, height=62, gap=22)
    while True:
        mouse_pos = pygame.mouse.get_pos()
        draw_neon_background("MATCH FORMAT", "Choose the ruleset for this single match")
        for button in buttons:
            button.draw(screen, mouse_pos)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_f:
                    toggle_fullscreen()
                elif e.key == pygame.K_1:
                    return "Test"
                elif e.key == pygame.K_2:
                    return "ODI"
                elif e.key == pygame.K_3:
                    return "T20"
            if e.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.clicked(e):
                        return button.label
        clock.tick(FPS)

def select_tournament_format():
    options = [
        ("Test", NEON_CYAN),
        ("ODI", NEON_GREEN),
        ("T20", NEON_GOLD),
    ]
    buttons = make_menu_buttons(options, start_y=210, width=320, height=62, gap=22)
    while True:
        mouse_pos = pygame.mouse.get_pos()
        draw_neon_background("TOURNAMENT FORMAT", "Pick the format used for every tournament match")
        for button in buttons:
            button.draw(screen, mouse_pos)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_f:
                    toggle_fullscreen()
                elif e.key == pygame.K_1:
                    return "Test"
                elif e.key == pygame.K_2:
                    return "ODI"
                elif e.key == pygame.K_3:
                    return "T20"
            if e.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.clicked(e):
                        return button.label
        clock.tick(FPS)

# ------------------- LEAGUE & WORLD CUP UTILITIES -------------------
def get_match_winner_for_points_basic(match: Match):
    total_a = sum(inn.runs for inn in match.innings_list if inn.batting_team.name == match.team_a.name)
    total_b = sum(inn.runs for inn in match.innings_list if inn.batting_team.name == match.team_b.name)
    if total_a > total_b:
        return "A"
    elif total_b > total_a:
        return "B"
    else:
        return "T"

def determine_result_flag_for_points(match: Match, format_type: str):
    if format_type == "Test":
        if match.match_over and match.result_text:
            rt = match.result_text.lower()
            if "won by" in rt:
                if match.team_a.name.lower() in rt:
                    return "A"
                elif match.team_b.name.lower() in rt:
                    return "B"
            return "T"
        else:
            total_a = sum(inn.runs for inn in match.innings_list if inn.batting_team.name == match.team_a.name)
            total_b = sum(inn.runs for inn in match.innings_list if inn.batting_team.name == match.team_b.name)
            if total_a > total_b:
                return "A"
            elif total_b > total_a:
                return "B"
            else:
                return "T"
    else:
        return get_match_winner_for_points_basic(match)

def compute_match_top_performers(match: Match):
    top_scorer = None
    top_runs = -1
    top_bowler = None
    top_wkts = -1
    for inn in match.innings_list:
        for b in inn.batsmen_stats:
            if b.runs > top_runs:
                top_runs = b.runs
                top_scorer = (b.player.name, inn.batting_team.name, b.runs, b.balls_faced)
        for bow in inn.bowler_stats:
            if bow.wickets > top_wkts:
                top_wkts = bow.wickets
                top_bowler = (bow.player.name, inn.bowling_team.name, bow.wickets, bow.runs_conceded)
    return top_scorer, top_bowler

def show_match_summary_overlay(match: Match, standings: dict, player_agg: dict, next_match_pair):
    overlay_alpha = 0
    fading_in = True
    blink = True
    blink_timer = 0
    blink_state = True

    match_top_scorer, match_best_bowler = compute_match_top_performers(match)

    table = []
    for tname, s in standings.items():
        table.append(s)
    table.sort(key=lambda x: (x["Pts"], x.get("NRR", 0), x["RF"]), reverse=True)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_f:
                    toggle_fullscreen()
                if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
                    return

        screen.fill((8,40,65))
        screen.blit(GRASS_SURFACE, (0,0))

        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        alpha_val = min(180, overlay_alpha)
        overlay.fill((10, 10, 20, alpha_val))
        screen.blit(overlay, (0,0))
        if fading_in:
            overlay_alpha += 18
            if overlay_alpha >= 180:
                fading_in = False

        panel_w = 820
        panel_h = 420
        panel_x = (SCREEN_W - panel_w)//2
        panel_y = (SCREEN_H - panel_h)//2
        rounded_rect(screen, (panel_x, panel_y, panel_w, panel_h), (245,245,250, 240), radius=12)
        pygame.draw.rect(screen, (120,140,170), (panel_x+2, panel_y+2, panel_w-4, panel_h-4), 2, border_radius=10)

        draw_text(screen, "Match Summary", (panel_x + 28, panel_y + 18), HEADER, (12,38,60))

        result_line = match.match_result() or match.result_text or "Result unavailable"
        draw_text(screen, result_line, (panel_x + 28, panel_y + 60), BIG, (10,10,10))

        tp_x = panel_x + 28
        tp_y = panel_y + 100
        draw_text(screen, "Top Performers:", (tp_x, tp_y), BIG, (8,40,65))
        if match_top_scorer:
            draw_text(screen, f"Top Scorer: {match_top_scorer[0]} ({match_top_scorer[1]}) - {match_top_scorer[2]} ({match_top_scorer[3]})", (tp_x, tp_y + 30), FONT, (20,20,20))
        else:
            draw_text(screen, "Top Scorer: -", (tp_x, tp_y + 30), FONT, (20,20,20))
        if match_best_bowler:
            draw_text(screen, f"Best Bowler: {match_best_bowler[0]} ({match_best_bowler[1]}) - {match_best_bowler[2]}/{match_best_bowler[3]}", (tp_x, tp_y + 54), FONT, (20,20,20))
        else:
            draw_text(screen, "Best Bowler: -", (tp_x, tp_y + 54), FONT, (20,20,20))

        table_x = panel_x + 420
        table_y = panel_y + 100
        draw_text(screen, "Points Table (mini)", (table_x, table_y), BIG, (8,40,65))
        header_y = table_y + 30
        draw_text(screen, "Team", (table_x + 2, header_y), FONT, (10,10,10))
        draw_text(screen, "P", (table_x + 150, header_y), FONT, (10,10,10))
        draw_text(screen, "W", (table_x + 190, header_y), FONT, (10,10,10))
        draw_text(screen, "Pts", (table_x + 230, header_y), FONT, (10,10,10))

        y = header_y + 26
        for idx, row in enumerate(table[:4], start=1):
            if idx == 1:
                rounded_rect(screen, (table_x - 6, y - 4, 340, 26), (255, 240, 200, 200), radius=6)
            draw_text(screen, row["team"].name, (table_x + 2, y), FONT, (0,0,0) if idx==1 else (20,20,20))
            draw_text(screen, str(row["P"]), (table_x + 150, y), FONT, (0,0,0) if idx==1 else (20,20,20))
            draw_text(screen, str(row["W"]), (table_x + 190, y), FONT, (0,0,0) if idx==1 else (20,20,20))
            draw_text(screen, str(row["Pts"]), (table_x + 230, y), FONT, (0,0,0) if idx==1 else (20,20,20))
            y += 26

        nm_y = panel_y + panel_h - 78
        if next_match_pair:
            nm_text = f"Next Match: {next_match_pair[0].name} vs {next_match_pair[1].name}"
        else:
            nm_text = "No more matches"
        draw_text(screen, nm_text, (panel_x + 28, nm_y), BIG, (8,40,65))

        blink_timer += 1
        if blink_timer > 20:
            blink_state = not blink_state
            blink_timer = 0
        if blink_state:
            draw_text(screen, "Press ENTER to continue", (panel_x + panel_w - 260, nm_y), FONT, (30,30,30))

        pygame.display.flip()
        clock.tick(FPS)

# ------------------- LEAGUE RUNNER -------------------
# ------------------- SELECT 4 TEAMS -------------------
def select_4_teams():
    team_options = [(name, ALL_TEAMS[name]) for name in TEAM_NAMES]
    selected = []
    idx = 0
    card_w = 430
    card_h = 56
    start_x = (SCREEN_W - (card_w * 2 + 28)) // 2
    start_y = 150
    cards = []
    for i, (team_name, team_factory) in enumerate(team_options):
        col = i % 2
        row = i // 2
        rect = (start_x + col * (card_w + 28), start_y + row * 68, card_w, card_h)
        cards.append((team_name, team_factory, Button(rect, team_name, NEON_CYAN, FONT)))
    start_button = Button((SCREEN_W // 2 - 170, 660, 340, 52), "START TOURNAMENT", NEON_GREEN, BIG)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        draw_neon_background("SELECT 4 TEAMS", "Click four team cards, then start the tournament")

        for i, (team_name, team_factory, button) in enumerate(cards):
            is_selected = team_factory in selected
            if is_selected:
                selected_glow = pygame.Surface((button.rect.w + 12, button.rect.h + 12), pygame.SRCALPHA)
                pygame.draw.rect(selected_glow, (85, 255, 170, 80), selected_glow.get_rect(), border_radius=12)
                screen.blit(selected_glow, (button.rect.x - 6, button.rect.y - 6))
            button.draw(screen, mouse_pos)
            if is_selected:
                pygame.draw.rect(screen, NEON_GREEN, button.rect, 3, border_radius=10)
                draw_text(screen, "SELECTED", (button.rect.right - 92, button.rect.y + 20), FONT, NEON_GREEN)
            if i == idx:
                pygame.draw.rect(screen, NEON_GOLD, button.rect.inflate(8, 8), 2, border_radius=12)

        draw_text(screen, f"Selected: {len(selected)}/4", (SCREEN_W // 2 - 56, 625), BIG, (235, 255, 255))
        if len(selected) == 4:
            start_button.draw(screen, mouse_pos)
        else:
            draw_centered_text(screen, "Choose four teams", (SCREEN_W // 2 - 170, 660, 340, 52), BIG, (135, 190, 205))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_f:
                    toggle_fullscreen()
                elif e.key == pygame.K_UP:
                    idx = (idx - 2) % len(team_options)
                elif e.key == pygame.K_DOWN:
                    idx = (idx + 2) % len(team_options)
                elif e.key == pygame.K_LEFT:
                    idx = (idx - 1) % len(team_options)
                elif e.key == pygame.K_RIGHT:
                    idx = (idx + 1) % len(team_options)
                elif e.key == pygame.K_RETURN:
                    team_factory = team_options[idx][1]
                    if len(selected) < 4 and team_factory not in selected:
                        selected.append(team_factory)
                    elif len(selected) == 4:
                        return [cls() for cls in selected]
                elif e.key == pygame.K_BACKSPACE and selected:
                    selected.pop()
            if e.type == pygame.MOUSEBUTTONDOWN:
                for team_name, team_factory, button in cards:
                    if button.clicked(e):
                        if team_factory in selected:
                            selected.remove(team_factory)
                        elif len(selected) < 4:
                            selected.append(team_factory)
                        break
                if len(selected) == 4 and start_button.clicked(e):
                    return [cls() for cls in selected]
        clock.tick(FPS)

# ------------------- TOURNAMENT WINNER SCREEN -------------------
def show_tournament_winner_screen(winner_team, player_agg):
    screen.fill((6, 24, 45))
    screen.blit(GRASS_SURFACE, (0, 0))

    draw_text(screen, "TOURNAMENT CHAMPIONS",
              (SCREEN_W // 2 - 260, 80), HEADER, (255, 215, 0))
    draw_text(screen, winner_team.name,
              (SCREEN_W // 2 - 160, 150), HEADER, (255, 255, 255))

    top_scorer = None
    top_runs = -1
    top_wicket = None
    top_wkts = -1

    for (name, team), stats in player_agg.items():
        if stats["runs"] > top_runs:
            top_runs = stats["runs"]
            top_scorer = (name, team, stats["runs"])
        if stats["wickets"] > top_wkts:
            top_wkts = stats["wickets"]
            top_wicket = (name, team, stats["wickets"])

    y = 260
    draw_text(screen, "Top Performers", (SCREEN_W // 2 - 120, y), BIG, (255, 255, 255))
    y += 40

    if top_scorer:
        draw_text(
            screen,
            f"Orange Cap: {top_scorer[0]} ({top_scorer[1]}) - {top_scorer[2]} runs",
            (SCREEN_W // 2 - 320, y),
            FONT,
            (255, 255, 255),
        )
        y += 32

    if top_wicket:
        draw_text(
            screen,
            f"Purple Cap: {top_wicket[0]} ({top_wicket[1]}) - {top_wicket[2]} wickets",
            (SCREEN_W // 2 - 320, y),
            FONT,
            (255, 255, 255),
        )

    draw_text(
        screen,
        "Press ENTER to return to Main Menu",
        (SCREEN_W // 2 - 220, SCREEN_H - 80),
        FONT,
        (200, 200, 200),
    )

    pygame.display.flip()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                return


# ------------------- 4 TEAM TOURNAMENT -------------------
def run_4_team_tournament(tournament_format):
    teams = select_4_teams()

    standings = {}
    player_agg = {}

    for t in teams:
        standings[t.name] = {
            "team": t,
            "P": 0,
            "W": 0,
            "L": 0,
            "T": 0,
            "Pts": 0,
            "RF": 0,
            "RA": 0,
            "BF": 0,
            "BB": 0,
        }

    matches = [
        (teams[0], teams[1]),
        (teams[0], teams[2]),
        (teams[0], teams[3]),
        (teams[1], teams[2]),
        (teams[1], teams[3]),
        (teams[2], teams[3]),
    ]

    for idx, (a, b) in enumerate(matches):
        match = Match(a, b, tournament_format)
        match_loop(match, block_until_menu=False)

        standings[a.name]["P"] += 1
        standings[b.name]["P"] += 1

        for inn in match.innings_list:
            bt = inn.batting_team.name
            bl = inn.bowling_team.name

            standings[bt]["RF"] += inn.runs
            standings[bt]["BF"] += inn.balls
            standings[bl]["RA"] += inn.runs
            standings[bl]["BB"] += inn.balls

            for bstat in inn.batsmen_stats:
                key = (bstat.player.name, bt)
                player_agg.setdefault(key, {"runs": 0, "balls": 0, "wickets": 0})
                player_agg[key]["runs"] += bstat.runs
                player_agg[key]["balls"] += bstat.balls_faced

            for bow in inn.bowler_stats:
                key = (bow.player.name, bl)
                player_agg.setdefault(key, {"runs": 0, "balls": 0, "wickets": 0})
                player_agg[key]["wickets"] += bow.wickets

        result = determine_result_flag_for_points(match, tournament_format)
        if result == "A":
            standings[a.name]["W"] += 1
            standings[b.name]["L"] += 1
            standings[a.name]["Pts"] += 2
        elif result == "B":
            standings[b.name]["W"] += 1
            standings[a.name]["L"] += 1
            standings[b.name]["Pts"] += 2
        else:
            standings[a.name]["T"] += 1
            standings[b.name]["T"] += 1
            standings[a.name]["Pts"] += 1
            standings[b.name]["Pts"] += 1

        next_pair = matches[idx + 1] if idx + 1 < len(matches) else None
        show_match_summary_overlay(match, standings, player_agg, next_pair)

    table = list(standings.values())
    for s in table:
        of = (s["BF"] / 6) if s["BF"] else 0
        ob = (s["BB"] / 6) if s["BB"] else 0
        s["NRR"] = (s["RF"] / of if of else 0) - (s["RA"] / ob if ob else 0)

    table.sort(key=lambda x: (x["Pts"], x["NRR"]), reverse=True)

    finalist_a = table[0]["team"]
    finalist_b = table[1]["team"]

    final_match = Match(finalist_a, finalist_b, tournament_format)
    match_loop(final_match, block_until_menu=False)

    show_match_summary_overlay(final_match, standings, player_agg, None)

    result = determine_result_flag_for_points(final_match, tournament_format)
    winner = finalist_a if result == "A" else finalist_b

    show_tournament_winner_screen(winner, player_agg)





# ------------------- WORLD CUP -------------------
def run_world_cup(all_teams: List[Team], format_type="T20"):
    """
    World Cup: single round-robin group stage (each vs each once),
    top 4 advance to semis (1v4, 2v3), winners go to final.
    Uses same match engine and GUI. Auto-advances like run_league.
    (IPL-style: always T20 format)
    """
    # Force T20 format always (IPL style)
    format_type = "T20"

    teams = all_teams[:]
    n = len(teams)
    standings = {
        t.name: {"team": t, "P": 0, "W": 0, "L": 0, "T": 0, "Pts": 0, "RF": 0, "RA": 0, "BF": 0, "BB": 0}
        for t in teams
    }
    player_agg = {}

    # Round-robin stage
    matches = [(teams[i], teams[j]) for i in range(n) for j in range(i + 1, n)]

    for idx, (a, b) in enumerate(matches):
        match = Match(a, b, format_type)
        match_loop(match, block_until_menu=False)

        standings[a.name]["P"] += 1
        standings[b.name]["P"] += 1

        # Update team + player stats
        for inn in match.innings_list:
            bt = inn.batting_team.name
            standings[bt]["RF"] += inn.runs
            standings[bt]["BF"] += inn.balls
            bl = inn.bowling_team.name
            standings[bl]["RA"] += inn.runs
            standings[bl]["BB"] += inn.balls

            for bstat in inn.batsmen_stats:
                key = (bstat.player.name, inn.batting_team.name)
                if key not in player_agg:
                    player_agg[key] = {"runs": 0, "balls": 0, "wickets": 0, "runs_conceded": 0, "balls_bowled": 0}
                player_agg[key]["runs"] += bstat.runs
                player_agg[key]["balls"] += bstat.balls_faced
            for bow in inn.bowler_stats:
                key = (bow.player.name, inn.bowling_team.name)
                if key not in player_agg:
                    player_agg[key] = {"runs": 0, "balls": 0, "wickets": 0, "runs_conceded": 0, "balls_bowled": 0}
                player_agg[key]["wickets"] += bow.wickets
                player_agg[key]["runs_conceded"] += bow.runs_conceded
                player_agg[key]["balls_bowled"] += bow.balls_bowled

        # Points system
        result_flag = determine_result_flag_for_points(match, format_type)
        if result_flag == "A":
            standings[a.name]["W"] += 1
            standings[b.name]["L"] += 1
            standings[a.name]["Pts"] += 2
        elif result_flag == "B":
            standings[b.name]["W"] += 1
            standings[a.name]["L"] += 1
            standings[b.name]["Pts"] += 2
        else:
            standings[a.name]["T"] += 1
            standings[b.name]["T"] += 1
            standings[a.name]["Pts"] += 1
            standings[b.name]["Pts"] += 1

        next_pair = matches[idx + 1] if idx + 1 < len(matches) else None
        show_match_summary_overlay(match, standings, player_agg, next_pair)

    # Compute final table
    table = []
    for s in standings.values():
        overs_faced = s["BF"] / 6 if s["BF"] > 0 else 0
        overs_bowled = s["BB"] / 6 if s["BB"] > 0 else 0
        rr_for = s["RF"] / overs_faced if overs_faced > 0 else 0
        rr_against = s["RA"] / overs_bowled if overs_bowled > 0 else 0
        s["NRR"] = rr_for - rr_against
        table.append(s)

    # Sort top 4 for knockouts
    table.sort(key=lambda x: (x["Pts"], x["NRR"], x["RF"]), reverse=True)

    # ---- Group stage complete ----
    while True:
        screen.fill((6, 24, 45))
        screen.blit(GRASS_SURFACE, (0, 0))
        draw_text(screen, "World Cup - Group Stage Complete (T20)", (SCREEN_W // 2 - 300, 16), HEADER, (255, 215, 0))
        draw_text(screen, "Top 4 progress to Semifinals", (SCREEN_W // 2 - 120, 50), BIG, (255, 255, 255))
        start_x = 60
        start_y = 100
        draw_text(screen, "Pos", (start_x, start_y), BIG, (255, 255, 255))
        draw_text(screen, "Team", (start_x + 40, start_y), BIG, (255, 255, 255))
        draw_text(screen, "P", (start_x + 260, start_y), BIG, (255, 255, 255))
        draw_text(screen, "W", (start_x + 300, start_y), BIG, (255, 255, 255))
        draw_text(screen, "Pts", (start_x + 420, start_y), BIG, (255, 255, 255))
        draw_text(screen, "NRR", (start_x + 590, start_y), BIG, (255, 255, 255))

        y = start_y + 40
        for idx, row in enumerate(table, start=1):
            if idx == 1:
                rounded_rect(screen, (start_x - 6, y - 6, 760, 28), (255, 215, 0, 200), radius=6)
            draw_text(screen, str(idx), (start_x, y), FONT, (0, 0, 0) if idx == 1 else (255, 255, 255))
            draw_text(screen, row["team"].name, (start_x + 40, y), FONT, (0, 0, 0) if idx == 1 else (255, 255, 255))
            draw_text(screen, str(row["P"]), (start_x + 260, y), FONT, (0, 0, 0) if idx == 1 else (255, 255, 255))
            draw_text(screen, str(row["W"]), (start_x + 300, y), FONT, (0, 0, 0) if idx == 1 else (255, 255, 255))
            draw_text(screen, str(row["Pts"]), (start_x + 420, y), FONT, (0, 0, 0) if idx == 1 else (255, 255, 255))
            draw_text(screen, f"{row['NRR']:+.2f}", (start_x + 590, y), FONT, (0, 0, 0) if idx == 1 else (255, 255, 255))
            y += 34

        draw_text(screen, "Press ENTER to continue", (SCREEN_W // 2 - 140, SCREEN_H - 60), FONT, (255, 255, 255))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and (e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER):
                break
        else:
            continue
        break

    # ---- Knockouts (Semis + Final) ----
    semi1 = (table[0]["team"], table[3]["team"])
    semi2 = (table[1]["team"], table[2]["team"])

    semi1_match = Match(semi1[0], semi1[1], "T20")
    match_loop(semi1_match, block_until_menu=False)
    semi1_winner = semi1[0] if determine_result_flag_for_points(semi1_match, "T20") == "A" else semi1[1]

    semi2_match = Match(semi2[0], semi2[1], "T20")
    match_loop(semi2_match, block_until_menu=False)
    semi2_winner = semi2[0] if determine_result_flag_for_points(semi2_match, "T20") == "A" else semi2[1]

    # Final
    final_match = Match(semi1_winner, semi2_winner, "T20")
    match_loop(final_match, block_until_menu=False)

    # Champion
    winner_flag = determine_result_flag_for_points(final_match, "T20")
    champion = semi1_winner if winner_flag == "A" else semi2_winner

    # ---- Winner Screen ----
    while True:
        screen.fill((8, 40, 65))
        screen.blit(GRASS_SURFACE, (0, 0))
        draw_text(screen, "IPL WORLD CUP (T20) - CHAMPION", (SCREEN_W // 2 - 260, 80), HEADER, (255, 215, 0))
        draw_text(screen, f"Winner: {champion.name}", (SCREEN_W // 2 - 120, 160), BIG, (255, 255, 255))
        draw_text(screen, "Press M to return to Main Menu", (SCREEN_W // 2 - 160, SCREEN_H - 80), FONT, (255, 255, 255))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_m:
                return


# ------------------- MAIN MENU -------------------
def main_menu():
    menu_items = [
        ("SINGLE MATCH", NEON_CYAN),
        ("4-TEAM TOURNAMENT", NEON_GREEN),
        ("WORLD CUP", NEON_GOLD),
        ("FULLSCREEN", NEON_CYAN),
        ("QUIT", (255, 85, 120)),
    ]
    buttons = make_menu_buttons(menu_items, start_y=180, width=410, height=58, gap=20)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        draw_neon_background("IPL SIMULATOR", "Futuristic cricket control deck")
        for button in buttons:
            button.draw(screen, mouse_pos)

        draw_text(screen, "Keyboard: 1 Single Match  |  2 Tournament  |  3 World Cup  |  F Fullscreen  |  Q Quit", (SCREEN_W // 2 - 365, 555), FONT, (165, 230, 240))
        draw_text(screen, "In match: SPACE next ball, S over, P scorecard, D declare", (SCREEN_W // 2 - 260, 582), FONT, (120, 190, 205))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    team_a = select_team("SELECT TEAM A")
                    team_b = select_team("SELECT TEAM B")
                    fmt = select_format()
                    match = Match(team_a, team_b, fmt)
                    match_loop(match, block_until_menu=True)
                elif e.key == pygame.K_2:
                    fmt = select_tournament_format()
                    run_4_team_tournament(fmt)
                elif e.key == pygame.K_3:
                    teams = [ALL_TEAMS[name]() for name in TEAM_NAMES]
                    run_world_cup(teams, "T20")
                elif e.key == pygame.K_f:
                    toggle_fullscreen()
                elif e.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif e.key == pygame.K_ESCAPE :
                    toggle_fullscreen()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].clicked(e):
                    team_a = select_team("SELECT TEAM A")
                    team_b = select_team("SELECT TEAM B")
                    fmt = select_format()
                    match = Match(team_a, team_b, fmt)
                    match_loop(match, block_until_menu=True)
                elif buttons[1].clicked(e):
                    fmt = select_tournament_format()
                    run_4_team_tournament(fmt)
                elif buttons[2].clicked(e):
                    teams = [ALL_TEAMS[name]() for name in TEAM_NAMES]
                    run_world_cup(teams, "T20")
                elif buttons[3].clicked(e):
                    toggle_fullscreen()
                elif buttons[4].clicked(e):
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)

# ------------------- ENTRY POINT -------------------
if __name__ == "__main__":
    main_menu()





