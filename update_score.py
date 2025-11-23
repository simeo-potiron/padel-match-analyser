from templates import formats
import copy

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Increment points
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def check_set_won(board):
    """
    Only for sets ending without TB or super-TB.
    Check if one of the teams have reached the minimum number of games to win a set and have a break.
    """
    nb_games_per_set = formats.get(board["format"])["games"]
    games_a, games_b = board["match"]["games"]["A"], board["match"]["games"]["B"]
    return (max(games_a, games_b) >= nb_games_per_set) and (abs(games_a - games_b) >= 2)

def check_match_won(board):
    """
    Check if one of the teams have reached the minimum number of sets to win the match.
    """
    nb_sets_to_win = formats.get(board["format"])["sets"]
    sets_a, sets_b = board["match"]["sets"]["A"], board["match"]["sets"]["B"]
    return max(sets_a, sets_b) >= nb_sets_to_win

def check_match_point(board):
    """
    Check if one of the teams can win the match at the next point.
    """  
    # Add a point to team A and check if they can win the match
    fake_board_a = {
        "format": board["format"],
        "match": copy.deepcopy(board["match"]),
        "winner": None
    }
    point_won(fake_board_a, "A", False)
    if fake_board_a["winner"] is not None:
        return "A"
    # Add a point to team A and check if they can win the match
    fake_board_b = {
        "format": board["format"],
        "match": copy.deepcopy(board["match"]),
        "winner": None
    }
    point_won(fake_board_b, "B", False)
    if fake_board_b["winner"] is not None:
        return "B"
    # If no team can win the match, return 0
    return 0

def point_won(board, team, update_stats=True):
    """
    Update the score board when a team wins a point.
    """
    # If a real point increment, a server needs to be set
    if update_stats and board["serving"]["current"] is None:
        return False
    
    # Ensure follow_players_stats exists in board
    if "follow_players_stats" not in board.keys():
        board["follow_players_stats"] = False

    # Check match specs to see if we are playing a TB or super-TB
    match_specs = formats.get(board["format"])
    nb_games_per_set, nb_sets_to_win, tb_loc = match_specs["games"], match_specs["sets"], match_specs["tie_break"]
    super_tb = match_specs["super_tb"] and (board["match"]["sets"]["A"] == board["match"]["sets"]["B"] == (nb_sets_to_win - 1))
    tie_break = (board["match"]["games"]["A"] == board["match"]["games"]["B"] == (nb_games_per_set + tb_loc)) and not super_tb

    # Store current server and point won
    if update_stats:
        board["live_stats"]["points_won"].append(team)
        if tie_break or super_tb:
            # Fake change of the server in the TB
            match ((board["match"]["points"]["A"] + board["match"]["points"]["B"]) //2) % 4:
                case 0: 
                    board["live_stats"]["serving"].append(board["serving"]["current"])
                case 1:
                    board["live_stats"]["serving"].append("A1" if board["serving"]["current"][0] == "B" else "B1")
                case 2: 
                    board["live_stats"]["serving"].append(board["serving"]["current"][0] + ("1" if board["serving"]["current"][1] == "2" else "2"))
                case 3:
                    board["live_stats"]["serving"].append("A2" if board["serving"]["current"][0] == "B" else "B2")
        else:
            board["live_stats"]["serving"].append(board["serving"]["current"])

    # Deal with tie-breaks
    call_game_won = False
    if tie_break or super_tb:
        # Add a point
        board["match"]["points"][team] += 1
        # Check if the TB is over
        max_points_tb = 10 if super_tb else 7
        call_game_won = board["match"]["points"][team] >= max_points_tb and (board["match"]["points"][team] - board["match"]["points"]['A' if team == 'B' else 'B']) >= 2

    # Deal with normal games
    else:
        if board["match"]["points"][team] == 0:
            board["match"]["points"][team] = 15
        elif board["match"]["points"][team] == 15:
            board["match"]["points"][team] = 30
        elif board["match"]["points"][team] == 30:
            board["match"]["points"][team] = 40
        elif board["match"]["points"][team] == 40:
            if match_specs["advantages"]:
                if board["match"]["points"]['A' if team == 'B' else 'B'] == "A":
                    for team in ["A", "B"]:
                        board["match"]["points"][team] = 40
                elif board["match"]["points"]['A' if team == 'B' else 'B'] == 40:
                    board["match"]["points"][team] = "A"
                else:
                    call_game_won = True
            else:
                call_game_won = True
        else:
            call_game_won = True

    # Check if it's a break point:
    if update_stats and not call_game_won:
        serv_team, ret_team = board["serving"]["current"][0], "A" if board["serving"]["current"][0] == "B" else "B"
        if board["match"]["points"][ret_team] == 40:
            if match_specs["advantages"]:
                if board["match"]["points"][serv_team] not in [40, "A"]:
                    board["live_stats"]["break_points"].append(ret_team)
            else:
                board["live_stats"]["break_points"].append(ret_team)
        elif board["match"]["points"][ret_team] == "A":
            board["live_stats"]["break_points"].append(ret_team)

    # Call game_won / set_won functions if needed
    if call_game_won:
        game_won(board, team, update_stats=update_stats, is_tb=(tie_break or super_tb))
    elif update_stats:
        # Check if it's a match point (the 1st point of a game/set cannot be a match point)
        board["live_stats"]["match_points"].append(check_match_point(board))

    # Add empty values in Live section
    if update_stats:
        for evt_type in board["live_stats"]:
            if (len(board["live_stats"][evt_type]) < len(board["live_stats"]["points_won"])) and not (evt_type in ["A1", "A2", "B1", "B2"] and board["follow_players_stats"]):
                board["live_stats"][evt_type].append(0)

    return True

def game_won(board, team, update_stats=True, is_tb=False):
    if update_stats:
        # Check if it was a break
        if (team != board["serving"]["current"][0]) and not is_tb:
            board["live_stats"]["breaks"].append(team)
        # Change server
        board["serving"]["previous"], board["serving"]["current"], board["serving"]["next"] = [
            board["serving"]["current"], 
            board["serving"]["next"],
            board["serving"]["current"][0] + ("1" if board["serving"]["current"][1] == "2" else "2")
        ]

    # Increment games
    board["match"]["games"][team] += 1

    # Distinguish TB and normal games
    if is_tb:
        set_won(board, team, update_stats, is_tb=True)
    else:
        # Reset points
        board["match"]["points"] = {"A": 0, "B": 0}
        # Check if the set is over
        if check_set_won(board):
            set_won(board, team, update_stats, is_tb=False)

def set_won(board, team, update_stats=True, is_tb=False):
    if update_stats:
        # Update score
        board["match"]["score"].append({"A": board["match"]["games"]["A"], "B": board["match"]["games"]["B"]})
        if is_tb:
            board["match"]["score_tb"].append({"A": board["match"]["points"]["A"], "B": board["match"]["points"]["B"]})
        else:
            board["match"]["score_tb"].append(None)
        # Reset servers
        board["serving"]["current"], board["serving"]["next"] = None, None
    
    # Increment sets and reset games and points
    board["match"]["sets"][team] += 1
    board["match"]["games"] = board["match"]["points"] = {"A": 0, "B": 0}
    
    # Check if the match is over
    if check_match_won(board):
        match_won(board, team, update_stats)
    elif update_stats:
        # Store "Fin de Set" event
        board["live_stats"]["events"].append(f"Fin set {board['match']['sets']['A'] + board['match']['sets']['B']}")

def match_won(board, team, update_stats=True):
    board["winner"] = team
    if update_stats:
        # Store "Fin de Match" event
        board["live_stats"]["events"].append(f"Fin de match")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                       Annulation point
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def undo_point_won(board):
    # Check who won last point (if any)
    try:
        last_winner = board["live_stats"]["points_won"][-1]
    except:
        return False

    # Match specs
    match_specs = formats.get(board["format"])
    nb_games_per_set, nb_sets_to_win, tb_loc = match_specs["games"], match_specs["sets"], match_specs["tie_break"]

    # Check if a game has been won:
    fully_updated = False
    if board["match"]["points"]["A"] == board["match"]["points"]["B"] == 0:
        # Check if a set has been won:
        if board["match"]["games"]["A"] == board["match"]["games"]["B"] == 0:
            # Reset sets
            board["match"]["sets"][last_winner] += -1

            # Reset games 
            board["match"]["games"] = board["match"]["score"].pop()
            board["match"]["games"][last_winner] += -1
            
            # Check if we were playing a TB or super-TB
            if board["match"]["score_tb"][-1] is not None:
                # Reset points
                board["match"]["points"] = board["match"]["score_tb"].pop()
                board["match"]["points"][last_winner] += -1

                # Reset server (we only care for current server)
                nb_points_played = board["match"]["points"]["A"] + board["match"]["points"]["B"] + 1
                board["serving"]["current"] = board["live_stats"]["serving"][-nb_points_played]
                
                # Fully dealt with
                fully_updated = True
        else:
            # De-increment games
            board["match"]["games"][last_winner] += -1
    else:
        # Check if we were playing a TB / super-TB
        super_tb = match_specs["super_tb"] and (board["match"]["sets"]["A"] == board["match"]["sets"]["B"] == (nb_sets_to_win - 1))
        tie_break = (board["match"]["games"]["A"] == board["match"]["games"]["B"] == (nb_games_per_set + tb_loc)) and not super_tb
        
        # De-increment points
        if tie_break or super_tb:
            board["match"]["points"][last_winner] += -1
        else:
            match board["match"]["points"][last_winner]:
                case 15:
                    board["match"]["points"][last_winner] = 0
                case 30:
                    board["match"]["points"][last_winner] = 15
                case 40:
                    board["match"]["points"][last_winner] = 30
                case "A":
                    board["match"]["points"][last_winner] = 40
        
        # Fully dealt with (server stays the same)
        fully_updated = True

    # Update server and points when it was a game point
    if not fully_updated:
        # Search for servers of last game and the game before and count points
        last_server = previous_server = board["live_stats"]["serving"][-1]
        last_game_points, pointer = {"A": 0, "B": 0}, -1
        while previous_server == last_server:
            last_game_points[board["live_stats"]["points_won"][pointer]] += 1
            pointer += -1
            previous_server = board["live_stats"]["serving"][pointer] if abs(pointer) <= len(board["live_stats"]["serving"]) else None
        
        # Reset server
        board["serving"]["previous"], board["serving"]["current"], board["serving"]["next"] = [
            previous_server, 
            last_server,
            (previous_server[0] + ("1" if previous_server[1] == "2" else "2")) if previous_server else None
        ]
        
        # Remove the last played point from last_game_points
        last_game_points[last_winner] += -1

        # Reset points (count each team points from the last game using serving)
        if (last_game_points["A"] <= 3) and (last_game_points["B"] <= 3):
            match last_game_points["A"]:
                case 1:
                    board["match"]["points"]["A"] = 15
                case 2:
                    board["match"]["points"]["A"] = 30
                case 3:
                    board["match"]["points"]["A"] = 40
            match last_game_points["B"]:
                case 1:
                    board["match"]["points"]["B"] = 15
                case 2:
                    board["match"]["points"]["B"] = 30
                case 3:
                    board["match"]["points"]["B"] = 40
        else:
            if last_game_points["A"] > last_game_points["B"]:
                board["match"]["points"] = {"A": "A", "B": 40}
            elif last_game_points["A"] < last_game_points["B"]:
                board["match"]["points"] = {"A": 40, "B": "A"}
            else:
                board["match"]["points"] = {"A": 40, "B": 40}

    # Remove all stats from last point
    for stat in board["live_stats"].keys():
        board["live_stats"][stat].pop()
    
    # If winner is set, remove it
    if board["winner"] in ["A", "B"]:
        board["winner"] = None
    
    return True