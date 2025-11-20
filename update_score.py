from templates import formats
import copy

def check_set_won(board):
    match_specs = formats.get(board["format"])
    nb_games_per_set, nb_sets_to_win = match_specs["games"], match_specs["sets"]
    super_tb = match_specs["super_tb"] and (board["match"]["sets"]["A"] == board["match"]["sets"]["B"] == (nb_sets_to_win - 1))
    # Deal with super tie-break (10 points)
    if super_tb:
        c_score = [board["match"]["points"][team] for team in ["A", "B"]]
        return any([score >= 10 and (score - c_score[1-idx]) >= 2 for idx, score in enumerate(c_score)])
    # Deal with normal set (6 games)
    else:
        c_score = [board["match"]["games"][team] for team in ["A", "B"]]
        return any([game >= nb_games_per_set and ((game - c_score[1-idx]) >= 2 or game > nb_games_per_set) for idx, game in enumerate(c_score)])

def check_match_won(board):
    nb_sets_to_win = formats.get(board["format"])["sets"]
    return any([sets >= nb_sets_to_win for sets in board["match"]["sets"].values()])

def check_match_point(board):    
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
    call_game_won, call_set_won = False, False
    if tie_break or super_tb:
        # Add a point
        board["match"]["points"][team] += 1
        if check_set_won(board):
            call_set_won = True
        elif tie_break and board["match"]["points"][team] >= 7 and (board["match"]["points"][team] - board["match"]["points"]['A' if team == 'B' else 'B']) >= 2:
            call_game_won = True

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
    if update_stats:
        try:
            serv_team, ret_team = board["serving"]["current"][0], "A" if board["serving"]["current"][0] == "B" else "B"
            if board["match"]["points"][ret_team] == 40:
                if match_specs["advantages"]:
                    if board["match"]["points"][serv_team] not in [40, "A"]:
                        board["live_stats"]["break_points"].append(ret_team)
                else:
                    board["live_stats"]["break_points"].append(ret_team)
            elif board["match"]["points"][ret_team] == "A":
                board["live_stats"]["break_points"].append(ret_team)
        except:
            print("No current server")

    # Call game_won / set_won functions if needed
    if call_game_won:
        game_won(board, team, update_stats, tie_break)
    elif call_set_won:
        set_won(board, team, update_stats)
    elif update_stats:
        # Check if it's a match point (the 1st point of a game/set cannot be a match point)
        board["live_stats"]["match_points"].append(check_match_point(board))

    # Add empty values in Live section
    if update_stats:
        for evt_type in board["live_stats"]:
            if (len(board["live_stats"][evt_type]) < len(board["live_stats"]["points_won"])) and not (evt_type in ["A1", "A2", "B1", "B2"] and board["follow_players_stats"]):
                board["live_stats"][evt_type].append(0)

def game_won(board, team, update_stats=True, is_tb=False):
    # Increment games
    board["match"]["games"][team] += 1
    # Reset points
    board["match"]["points"] = {"A": 0, "B": 0}
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
    # Check if the set is over
    if check_set_won(board):
        set_won(board, team, update_stats)

def set_won(board, team, update_stats=True):
    # Increment sets
    board["match"]["sets"][team] += 1
    if update_stats:
        # Update score
        if board["match"]["points"]["A"] == board["match"]["points"]["B"] == 0:
            board["match"]["score"].append({"A": board["match"]["games"]["A"], "B": board["match"]["games"]["B"]})
        else:
            board["match"]["score"].append({"A": board["match"]["points"]["A"], "B": board["match"]["points"]["B"]})
        # Reset servers
        board["serving"]["current"], board["serving"]["next"] = None, None
    # Reset games
    board["match"]["games"] = {"A": 0, "B": 0}
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