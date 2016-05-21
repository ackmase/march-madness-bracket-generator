import csv
import random
import sys

TOURNAMENT = ['Midwest',
              'West',
              'South',
              'East',
              'Final Four',
              'Championship',
              'Champion!']

ROUND_NAMES = ['%s Round of 64',
               '%s Round of 32',
               '%s Sweet Sixteen',
               '%s Elite Eight',
               'Final Four',
               'Championship']

LINEUP_ORDER = TOURNAMENT[:4]

CSV_PATH_TO_DATA = '/path/to/file.csv'


class Team(object):
  """Team object that holds name and statistical information about that team.
  """
  
  def __init__(self, name, seed, division, odds):
    """Initializes object.

    Args:
      name: String, name of team.
      seed: String, seed of team.
      division: String, name of division.
      odds: Float, odds of team winning the championship.
    """
    self.name = name
    self.seed = seed
    self.division = division
    self.odds = odds
    self.probability = 1 / odds
    self.previous_upset = False


def SingleRoundPlayBall(lineup):
  """Takes a lineup and produces the next one.

  Args:
    lineup: List of team objects. The assumption is that adjacent teams are
      paired up with one another.

  Returns:
    List of teams objects that represents the next round lineup.
  """
  return [WeightedCoinFlip (lineup[index], lineup[index + 1])
          for index in range(0, len(lineup), 2)]


def WeightedCoinFlip(team1, team2):
  """Matches up two teams and returns a winner with weights based on odds.

  Also sets the previous_upset field for the team.

  Args:
    team1: Team object 1.
    team2: Team object 2.

  Returns:
    The winner (team object).
  """
  hat = []
  underdog = None
  team1.previous_upset = False
  team2.previous_upset = False

  team1_win_probability, team2_win_probability = (
    CalculateWinProbabilities(team1, team2))

  # Determine underdog.
  if team1_win_probability > team2_win_probability:
    underdog = 2
  elif team1_win_probability < team2_win_probability:
    underdog = 1

  # Put slips of paper in hat for team1.
  for x in range(int(round(team1_win_probability * 10, 0))):
    hat.append(team1)
    
  # Put slips of paper in hat for team2.
  for x in range(int(round(team2_win_probability * 10, 0))):
    hat.append(team2)

  # Check to see that the hat is completely full and there are no rounding
  # errors.
  assert len(hat) == 1000

  winner_index = random.randint(0, len(hat) - 1)
  winner = hat[winner_index]

  # Figure out if the win is an upset.
  if winner.name == team1.name and underdog == 1:
    winner.previous_upset = True
  if winner.name == team2.name and underdog == 2:
    winner.previous_upset = True

  return winner


def RandomCoinFlip(team1, team2):
  """Matches up two teams and returns a winner.
  
  Args:
    team1: Team object 1.
    team2: Team object 2.
  
  Returns: 
    The winner (team object).
  """
  team_list = [team1, team2]
  winner_index = random.randint(0, 1)
  return team_list[winner_index]


def CalculateWinProbabilities(team1, team2):
  """Calculates win probability for teams to the nearest 0.1%

  Args:
    team1: Team object 1.
    team2: Team object 2.

  Returns:
    Win probability for team 1 and 2.
  """
  team1_win_probability = round(
    team1.probability /
    (team1.probability + team2.probability), 3) * 100
  team2_win_probability = round(
    team2.probability /
    (team1.probability + team2.probability), 3) * 100
  return team1_win_probability, team2_win_probability


def PritsPrintLineup(lineup):
  """Prints the lineup pretty print style.

  Args:
    lineup: List of team objects. The assumption is that adjacent teams are
       paired up with one another.
  """
  for index in range(0, len(lineup), 2):
    team1 = lineup[index]
    team2 = lineup[index + 1]
    team1_win_probability, team2_win_probability = (
      CalculateWinProbabilities(team1, team2))
    formatted_team1_name = team1.name.lower()
    formatted_team2_name = team2.name.lower()

    print '[%s] %s (%s%%) vs. [%s] %s (%s%%)' % (team1.seed,
                                                 FormattedTeamName(team1),
                                                 team1_win_probability,
                                                 team2.seed,
                                                 FormattedTeamName(team2),
                                                 team2_win_probability)
  print ''


def FormattedTeamName(team):
  """Format team name in all caps if it was the  underdog in previous round.

  Args:
    team: Team object.

  Returns:
    String, formatted team name.
  """
  return team.name.upper() if team.previous_upset else team.name.lower()


def PrintTournamentHeader(tournament_name):
  """Prints the tournament header.
 
  Args:
    tournament_name: String, name of tournament.
  """
  print '**************************************************'
  print tournament_name
  print '**************************************************'


def ImportData(csv_path):
  """Imports data from CSV and creates lineup with team objects.

  Args:
    csv_path: String, path to CSV.

  Yields::
    The lineup.
  """
  # Represents an object with divisions for keys and lineup lists for values.
  # (e.g., {'Midwest': [team1, team2...]}
  lineup_dict = {}

  with open(csv_path) as data_file:
    data_reader = csv.DictReader(data_file)
    for row in data_reader:
      name = row['Team']
      seed = row['Seed']
      division = row['Division']
      odds = float(row['Odds'])
      team = Team(name, seed, division, odds)
      lineup_dict.setdefault(division, []).append(team)

  for division in LINEUP_ORDER:
    yield lineup_dict[division]


def main():
  if len(sys.argv) != 2:
    print 'usage: python march-madness.py /path/to/file.csv'
    
  csv_path_to_data = sys.argv[1]
  semi_final_lineup = []
  final_lineup = []
  tournament_index = 0

  # Import team names, odds, and lineup.
  lineups = ImportData(csv_path_to_data)

  # Start indicator
  print '\n\n-----------------------------------------------------------'
  print '                       START                                 '
  print '-----------------------------------------------------------\n\n'

  # Standard Tournament
  for lineup in lineups:
    PrintTournamentHeader(TOURNAMENT[tournament_index])
    round_index = 0

    while len(lineup) > 1:
      print ROUND_NAMES[round_index] % (TOURNAMENT[tournament_index])
      PritsPrintLineup(lineup)
      lineup = SingleRoundPlayBall(lineup)
      round_index += 1
      
    print '%s Final Four\n%s\n' % (TOURNAMENT[tournament_index],
                                   FormattedTeamName(lineup[0]))
    semi_final_lineup.extend(lineup)
    tournament_index += 1

  # Final Four
  PrintTournamentHeader(TOURNAMENT[tournament_index])
  tournament_index += 1
  PritsPrintLineup(semi_final_lineup)
  final_lineup = SingleRoundPlayBall(semi_final_lineup)

  # Championship
  PrintTournamentHeader(TOURNAMENT[tournament_index])
  tournament_index += 1
  PritsPrintLineup(final_lineup)

  # Champion
  PrintTournamentHeader(TOURNAMENT[tournament_index])
  print FormattedTeamName(SingleRoundPlayBall(final_lineup)[0])
  print '\n-----------------------------------------------------------'
  print '                        END                                '
  print '-----------------------------------------------------------'

if __name__ == '__main__':
  main()
