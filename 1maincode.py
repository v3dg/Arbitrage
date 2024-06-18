import argparse
import itertools
import requests

# Obtain the api key that was passed in from the command line
parser = argparse.ArgumentParser(description='Sample V4')
parser.add_argument('--api-key', type=str, default='')
args = parser.parse_args()

# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/
API_KEY = 'b161f22b739552747ca4b6a72b90da3a'

# Bookmaker regions
REGIONS = 'us,us2'

# Odds markets
MARKETS = 'h2h'

# Odds format
ODDS_FORMAT = 'decimal'

# Date format
DATE_FORMAT = 'iso'

# List of sports
sports = [
    'americanfootball_cfl',
    'americanfootball_ncaaf',
    'americanfootball_nfl',
    'americanfootball_ufl',
    'aussierules_afl',
    'baseball_mlb',
    'baseball_mlb_preseason',
    'baseball_npb',
    'baseball_kbo',
    'baseball_ncaa',
    'basketball_euroleague',
    'basketball_nba',
    'basketball_wnba',
    'basketball_ncaab',
    'boxing_boxing',
    'cricket_big_bash',
    'cricket_caribbean_premier_league',
    'cricket_icc_world_cup',
    'cricket_international_t20',
    'cricket_ipl',
    'cricket_odi',
    'cricket_psl',
    'cricket_t20_blast',
    'cricket_test_match',
    'icehockey_nhl',
    'icehockey_sweden_allsvenskan',
    'icehockey_sweden_hockey_league',
    'mma_mixed_martial_arts',
    'rugbyleague_nrl',
    'soccer_africa_cup_of_nations',
    'soccer_argentina_primera_division',
    'soccer_australia_aleague',
    'soccer_austria_bundesliga',
    'soccer_belgium_first_div',
    'soccer_brazil_campeonato',
    'soccer_brazil_serie_b',
    'soccer_chile_campeonato',
    'soccer_china_superleague',
    'soccer_denmark_superliga',
    'soccer_england_efl_cup',
    'soccer_england_league1',
    'soccer_england_league2',
    'soccer_epl',
    'soccer_fa_cup',
    'soccer_fifa_world_cup',
    'soccer_fifa_world_cup_womens',
    'soccer_finland_veikkausliiga',
    'soccer_france_ligue_one',
    'soccer_france_ligue_two',
    'soccer_germany_bundesliga',
    'soccer_germany_bundesliga2',
    'soccer_germany_liga3',
    'soccer_greece_super_league',
    'soccer_italy_serie_a',
    'soccer_italy_serie_b',
    'soccer_japan_j_league',
    'soccer_korea_kleague1',
    'soccer_league_of_ireland',
    'soccer_mexico_ligamx',
    'soccer_netherlands_eredivisie',
    'soccer_norway_eliteserien',
    'soccer_poland_ekstraklasa',
    'soccer_portugal_primeira_liga',
    'soccer_spain_la_liga',
    'soccer_spain_segunda_division',
    'soccer_spl',
    'soccer_sweden_allsvenskan',
    'soccer_sweden_superettan',
    'soccer_switzerland_superleague',
    'soccer_turkey_super_league',
    'soccer_uefa_europa_conference_league',
    'soccer_uefa_champs_league',
    'soccer_uefa_euro_qualification',
    'soccer_uefa_europa_conference_league',
    'soccer_uefa_europa_league',
    'soccer_uefa_nations_league',
    'soccer_conmebol_copa_america',
    'soccer_conmebol_copa_libertadores',
    'soccer_usa_mls',
    'tennis_atp_aus_open_singles',
    'tennis_atp_french_open',
    'tennis_atp_us_open',
    'tennis_atp_wimbledon',
    'tennis_wta_aus_open_singles',
    'tennis_wta_french_open',
    'tennis_wta_us_open',
    'tennis_wta_wimbledon'
]

# Function to calculate arbitrage
def calculate_arbitrage(odds):
    total_inverse_prob = 0
    for outcome in odds:
        total_inverse_prob += 1 / outcome
    return total_inverse_prob

# Loop through each sport and fetch odds
for SPORT in sports:
    # Now get a list of live & upcoming games for the current sport, along with odds for different bookmakers
    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds', params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    })

    if odds_response.status_code != 200:
        print(f'Failed to get odds for {SPORT}: status_code {odds_response.status_code}, response body {odds_response.text}')
    else:
        odds_json = odds_response.json()
        print(f'Number of events for {SPORT}: {len(odds_json)}')

        # Print the remaining requests
        print('Remaining requests:', odds_response.headers['x-requests-remaining'])

        arbitrage_opportunity_found = False

        for event in odds_json:
            outcomes = {}

            for bookmaker in event['bookmakers']:
                outcomes[bookmaker['title']] = {
                    'home': bookmaker['markets'][0]['outcomes'][0]['price'],
                    'away': bookmaker['markets'][0]['outcomes'][1]['price']
                }

                if len(bookmaker['markets'][0]['outcomes']) > 2:
                    outcomes[bookmaker['title']]['tie'] = bookmaker['markets'][0]['outcomes'][2]['price']

            for bookmaker1, bookmaker2 in itertools.combinations(outcomes.keys(), 2):
                odds1 = outcomes[bookmaker1]['home']
                odds2 = outcomes[bookmaker2]['away']

                if 'tie' in outcomes[bookmaker1]:
                    odds_tie = outcomes[bookmaker1]['tie']
                    total_inverse_prob = calculate_arbitrage([odds1, odds2, odds_tie])
                else:
                    total_inverse_prob = calculate_arbitrage([odds1, odds2])

                if total_inverse_prob < 1:
                    print(f"\nMatch for {SPORT}: {event['home_team']} vs. {event['away_team']}")
                    print(f"Start Time: {event['commence_time']} (UTC)")

                    print(f"Highest Odds for {SPORT}: {odds1} ({bookmaker1}), {odds2} ({bookmaker2})")

                    bet_amount1 = 100 * (1 / odds1) / total_inverse_prob
                    bet_amount2 = 100 * (1 / odds2) / total_inverse_prob

                    original_minimum_profit = 100 / total_inverse_prob - 100
                    print(f"Minimum Profit: ${original_minimum_profit:.2f}")

                    print(f"Bet ${bet_amount1:.2f} on {event['home_team']} ({bookmaker1})")
                    print(f"Bet ${bet_amount2:.2f} on {event['away_team']} ({bookmaker2})")

                    # Round bet amounts to the nearest dollar
                    bet_amount1_rounded = round(bet_amount1)
                    bet_amount2_rounded = round(bet_amount2)

                    if 'tie' in outcomes[bookmaker1]:
                        bet_amount_tie = 100 * (1 / odds_tie) / total_inverse_prob
                        bet_amount_tie_rounded = round(bet_amount_tie)
                    else:
                        bet_amount_tie_rounded = 0

                    # Recalculate the total investment and new profits
                    total_investment = bet_amount1_rounded + bet_amount2_rounded + (bet_amount_tie_rounded if 'tie' in outcomes[bookmaker1] else 0)

                    profit1 = bet_amount1_rounded * odds1 - total_investment
                    profit2 = bet_amount2_rounded * odds2 - total_investment
                    profit_tie = bet_amount_tie_rounded * odds_tie - total_investment if 'tie' in outcomes[bookmaker1] else float('-inf')

                    if profit1 > 0 and profit2 > 0 and (profit_tie > 0 if 'tie' in outcomes[bookmaker1] else True):
                        print(f"Rounded Bet ${bet_amount1_rounded} on {event['home_team']} ({bookmaker1})")
                        print(f"Rounded Bet ${bet_amount2_rounded} on {event['away_team']} ({bookmaker2})")

                        if 'tie' in outcomes[bookmaker1]:
                            print(f"Rounded Bet ${bet_amount_tie_rounded} on Tie ({bookmaker1})")

                        print(f"New Minimum Profit if {event['home_team']} wins: ${profit1:.2f}")
                        print(f"New Minimum Profit if {event['away_team']} wins: ${profit2:.2f}")

                        if 'tie' in outcomes[bookmaker1]:
                            print(f"New Minimum Profit if Tie: ${profit_tie:.2f}")

                        arbitrage_opportunity_found = True

        if not arbitrage_opportunity_found:
            print(f"No arbitrage opportunity found for {SPORT}")
