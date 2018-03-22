from nba_py import team, game
import pandas as pd
from datetime import datetime, timedelta
import time

#set game_id template, replace "@" with season year and "!" with the game number
template_game_id = '002@!'


#Note that the 2017-2018 season is represented by 2017
player_data = []
game_data = []
start_year = 2007
end_year = 2017

#Used to replace the team id's with their abbreviations
team_mappings = {
1610612737:'ATL',
1610612738:'BOS',
1610612751:'BKN',
1610612766:'CHA',
1610612741:'CHI',
1610612739:'CLE',
1610612742:'DAL',
1610612743:'DEN',
1610612765:'DET',
1610612744:'GSW',
1610612745:'HOU',
1610612754:'IND',
1610612746:'LAC',
1610612747:'LAL',
1610612763:'MEM',
1610612748:'MIA',
1610612749:'MIL',
1610612750:'MIN',
1610612740:'NOP',
1610612752:'NYK',
1610612760:'OKC',
1610612753:'ORL',
1610612755:'PHI',
1610612756:'PHX',
1610612757:'POR',
1610612758:'SAC',
1610612759:'SAS',
1610612761:'TOR',
1610612762:'UTA',
1610612764:'WAS'
}

for year in range(start_year, end_year+1):
    
    game_id_count = 1
    
    #Loop through the game_id's until the last game is reached, upon which a break is triggered
    while True:
        
        #Replace the game_id_temple with the proper variables
        game_id = template_game_id.replace('@', str(year)[2:4]).replace('!', str(game_id_count).rjust(5, '0'))
        print(game_id)

        #Call the API, if it fails, it means you hit the last game, move onto the next year
        try:
            boxscore_summary = game.Boxscore(game_id)
            game_summary = game.BoxscoreSummary(game_id)
        except:
            break

        #Get stats
        player_stats = boxscore_summary.player_stats()
        game_stats = game_summary.line_score()
        game_info = game_summary.game_summary()

        if player_stats.empty or game_stats.empty or game_info.empty:
            break

        #Wins and lossess are stored in the format: Wins-Losses, parse it and get the numeric values
        win_loss = game_summary.line_score()['TEAM_WINS_LOSSES']
        win_loss = win_loss.str.split('-')
        try:
            game_stats['WINS'] = [float(win_loss[0][0]), float(win_loss[1][0])]
            game_stats['LOSSES'] = [float(win_loss[0][1]),float(win_loss[1][1])]
        except:
            break

        #Get the date ranges and team ids
        end_date = datetime.strptime(game_info['GAME_DATE_EST'].iloc[0][:-9], '%Y-%m-%d') - timedelta(1)
        start_date = end_date - timedelta(31)
        team_one_id = game_stats['TEAM_ID'].iloc[0]
        team_two_id = game_stats['TEAM_ID'].iloc[1]
        
        #Get the average standard statistics for the past 30 days for each team
        team_one_stats = team.TeamYearOverYearSplits(team_id=team_one_id, date_from=start_date, date_to=end_date).by_year()
        team_two_stats = team.TeamYearOverYearSplits(team_id=team_two_id, date_from=start_date, date_to=end_date).by_year()
        
        #Add the team abbreviations instead of ids
        team_one_stats['TEAM_ABBREVIATION'] = team_mappings[team_one_id]
        team_two_stats['TEAM_ABBREVIATION'] = team_mappings[team_two_id]
        
        #Combine the different data sources
        overall_team_stats = team_one_stats.append(team_two_stats, ignore_index=True)
        game_data_temp = pd.merge(game_stats[['GAME_ID','TEAM_ABBREVIATION', 'PTS', 'WINS', 'LOSSES']], 
                                      game_info[['GAME_ID', 'HOME_TEAM_ID', 'VISITOR_TEAM_ID']], on='GAME_ID', how='inner')
        game_data_temp = pd.merge(game_data_temp,overall_team_stats, on='TEAM_ABBREVIATION',how='left')
        game_data_temp['HOME_TEAM_ID'].replace(team_mappings, inplace=True)
        game_data_temp['VISITOR_TEAM_ID'].replace(team_mappings, inplace=True)
        
        player_data.extend(player_stats[['GAME_ID','TEAM_ABBREVIATION', 'PLAYER_NAME']].values)
        game_data.extend(game_data_temp[['GAME_ID', 'TEAM_ABBREVIATION', 'PTS_x', 'WINS', 'LOSSES', 'HOME_TEAM_ID',
                                         'VISITOR_TEAM_ID','W_PCT', 'FGM', 'FGA','FG3M','FG3A','FTM','FTA','OREB', 'DREB', 
                                         'AST', 'TOV','STL', 'BLK','PF']].values)
        
        #Increment to the next game
        game_id_count = game_id_count + 1
        time.sleep(0.1)


#Save the data to a csv
player_data_pd = pd.DataFrame(player_data, columns=['game_id','team','player_name'])
game_data_pd = pd.DataFrame(game_data, columns=['game_id', 'team', 'pts', 'wins', 'losses', 'home_team', 'visitor_team','win_prcntg',
                                                'FGM', 'FGA','FG3M','FG3A','FTM','FTA','OREB', 'DREB', 'AST', 'TOV','STL', 'BLK','PF'])
player_data_pd.to_csv('player_data.csv', index=False)
game_data_pd.to_csv('game_data.csv', index=False)