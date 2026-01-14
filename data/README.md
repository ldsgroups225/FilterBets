# /data/ Directory

This directory is intended for storing the raw and processed data used by the FilterBets application.

**Important**: This directory is included in the project's `.gitignore` file. The data stored here will not and should not be committed to the Git repository.

## Setup

Before running the download script, you must have your Kaggle API credentials configured.

1. **Install the necessary packages**:

    ```bash
    poetry install
    ```

2. **Get your API Token**:
    - Go to your Kaggle account page: [https://www.kaggle.com/account](https://www.kaggle.com/account)
    - Click on "Create New Token" in the API section.
    - This will download a `kaggle.json` file.

3. **Place the Token**:
    - Place the downloaded `kaggle.json` file in the expected location, which is typically `~/.kaggle/`.

    ```bash
    mkdir -p ~/.kaggle/
    mv ~/Downloads/kaggle.json ~/.kaggle/
    chmod 600 ~/.kaggle/kaggle.json
    ```

## Download Data

To download the required ESPN Soccer dataset, run the python script from within the poetry environment:

```bash
poetry run python3 data/download_data.py
```

The script will download and unzip the dataset directly into this `data/` directory.

---

## Data Schema

This section documents the schema for each type of CSV file found in the downloaded dataset.

### Directory: `base_data/`

This directory contains the core relational tables for the dataset.

**File: `fixtures.csv`**
*Description: Contains all match fixtures. Indexed by `eventId`.*

| Header | Data Type | Description |
| --- | --- | --- |
| Rn | Integer | Row number or index. |
| seasonType | Integer | Identifier for the season type. |
| leagueId | Integer | Foreign key for the league (`leagues.csv`). |
| eventId | Integer | **Primary Key.** Unique identifier for the match. |
| date | DateTime | Date and time of the match (UTC). |
| venueId | Integer | Foreign key for the venue (`venues.csv`). |
| attendance | Integer | Number of attendees at the match. |
| homeTeamId | Integer | Foreign key for the home team (`teams.csv`). |
| awayTeamId | Integer | Foreign key for the away team (`teams.csv`). |
| homeTeamWinner | Boolean | `True` if the home team won. |
| awayTeamWinner | Boolean | `True` if the away team won. |
| homeTeamScore | Integer | Final score for the home team. |
| awayTeamScore | Integer | Final score for the away team. |
| homeTeamShootoutScore | Integer | Score for the home team in a penalty shootout. |
| awayTeamShootoutScore | Integer | Score for the away team in a penalty shootout. |
| statusId | Integer | Foreign key for the match status (`status.csv`). |
| updateTime | DateTime | Timestamp of the last update. |

**File: `teams.csv`**
*Description: Contains information for all teams. Indexed by `teamId`.*

| Header | Data Type | Description |
| --- | --- | --- |
| teamId | Integer | **Primary Key.** Unique identifier for the team. |
| location | String | The location/city of the team. |
| name | String | The full name of the team. |
| abbreviation | String | A three or four-letter abbreviation for the team. |
| displayName | String | The name used for display purposes. |
| shortDisplayName | String | A shorter version of the display name. |
| color | String | The primary hex color code for the team. |
| alternateColor | String | The secondary hex color code for the team. |
| logoURL | String | URL to the team's logo image. |
| venueId | Integer | Foreign key for the team's home venue (`venues.csv`). |
| slug | String | A URL-friendly slug for the team name. |

**File: `players.csv`**
*Description: Contains information for all players. Indexed by `athleteId`.*

| Header | Data Type | Description |
| --- | --- | --- |
| athleteId | Integer | **Primary Key.** Unique identifier for the player. |
| firstName | String | Player's first name. |
| middleName | String | Player's middle name. |
| lastName | String | Player's last name. |
| fullName | String | Player's full name. |
| displayName | String | Name used for display purposes. |
| shortName | String | A shorter version of the player's name. |
| nickName | String | Player's nickname. |
| slug | String | A URL-friendly slug for the player's name. |
| displayWeight | String | Weight with units (e.g., "159 lbs"). |
| weight | Float | Weight in pounds. |
| displayHeight | String | Height in feet and inches (e.g., "5' 9\""). |
| height | Float | Height in inches. |
| age | Integer | Player's age. |
| dateOfBirth | DateTime | Player's date of birth. |
| gender | String | Player's gender. |
| jersey | Integer | Player's jersey number. |
| citizenship | String | Player's country of citizenship. |
| birthPlaceCountry | String | Player's country of birth. |
| positionName | String | Full name of the player's position (e.g., "Goalkeeper"). |
| positionId | Integer | Identifier for the position. |
| positionAbbreviation | String | Abbreviation for the position (e.g., "G", "M", "F"). |
| headshotUrl | String | URL to the player's headshot image. |
| headshot_alt | String | Alternative text for the headshot image. |
| timestamp | DateTime | Timestamp of the last update. |

**File: `leagues.csv`**
*Description: Contains information about the various leagues and seasons.*

| Header | Data Type | Description |
| --- | --- | --- |
| seasonType | Integer | Unique identifier for the season type. |
| year | Integer | The year the season takes place in. |
| seasonName | String | The full name of the season. |
| seasonSlug | String | A URL-friendly slug for the season name. |
| leagueId | Integer | **Primary Key (Composite).** Identifier for the league. |
| midsizeName | String | A medium-length name for the league. |
| leagueName | String | The full name of the league. |
| leagueShortName | String | A shorter name for the league. |

**File: `venues.csv`**
*Description: Contains information about all venues. Indexed by `venueId`.*

| Header | Data Type | Description |
| --- | --- | --- |
| venueId | Integer | **Primary Key.** Unique identifier for the venue. |
| fullName | String | The full name of the venue. |
| shortName | String | A shorter name for the venue. |
| capacity | Integer | The seating capacity of the venue. |
| city | String | The city where the venue is located. |
| country | String | The country where the venue is located. |

**File: `teamStats.csv`**
*Description: Contains match statistics for teams. Indexed by `eventId` and `teamId`.*

| Header | Data Type | Description |
| --- | --- | --- |
| seasonType | Integer | Identifier for the season type. |
| eventId | Integer | Foreign key for the match (`fixtures.csv`). |
| teamId | Integer | Foreign key for the team (`teams.csv`). |
| teamOrder | Integer | Indicates if the team is home (0) or away (1). |
| possessionPct | Float | Percentage of ball possession. |
| foulsCommitted | Integer | Number of fouls committed. |
| yellowCards | Integer | Number of yellow cards received. |
| redCards | Integer | Number of red cards received. |
| offsides | Integer | Number of offsides. |
| wonCorners | Integer | Number of corners won. |
| saves | Integer | Number of saves made by the goalkeeper. |
| totalShots | Integer | Total number of shots taken. |
| shotsOnTarget | Integer | Number of shots that were on target. |
| shotPct | Float | Shot accuracy percentage. |
| penaltyKickGoals | Integer | Number of goals scored from penalty kicks. |
| penaltyKickShots | Integer | Number of penalty kicks taken. |
| accuratePasses | Integer | Number of successful passes. |
| totalPasses | Integer | Total number of passes attempted. |
| passPct | Float | Pass completion percentage. |
| ... | ... | ... |

**File: `standings.csv`**
*Description: Contains latest league table or standings of a season.*

| Header | Data Type | Description |
| --- | --- | --- |
| seasonType | Integer | Identifier for the season type. |
| year | Integer | The year of the season. |
| leagueId | Integer | Foreign key for the league (`leagues.csv`). |
| teamRank | Integer | The team's current rank in the league. |
| teamId | Integer | Foreign key for the team (`teams.csv`). |
| gamesPlayed | Integer | Number of games played in the season. |
| wins | Integer | Total wins. |
| ties | Integer | Total ties (draws). |
| losses | Integer | Total losses. |
| points | Integer | Total points accumulated. |
| gf | Integer | Goals For (total goals scored). |
| ga | Integer | Goals Against (total goals conceded). |
| gd | Integer | Goal Difference (gf - ga). |
| form | String | A string representing the result of the last few games (e.g., "WDWWW"). |
| timeStamp | DateTime | Timestamp of the last update. |

**File: `teamRoster.csv`**
*Description: Contains the latest team roster for a season.*

| Header | Data Type | Description |
| --- | --- | --- |
| seasonYear | Integer | The year of the season. |
| seasonType | Integer | Identifier for the season type. |
| teamId | Integer | Foreign key for the team (`teams.csv`). |
| athleteId | Integer | Foreign key for the player (`players.csv`). |
| jersey | Integer | The player's jersey number. |
| position | String | The player's position. |
| timeStamp | DateTime | Timestamp of the last update. |

**File: `status.csv`**
*Description: Maps `statusId` to a status name and description.*

| Header | Data Type | Description |
| --- | --- | --- |
| statusId | Integer | **Primary Key.** Unique identifier for the status. |
| name | String | The programmatic name of the status. |
| state | String | The state of the match: pre, in, or post-game. |
| description | String | A human-readable description. |

**File: `keyEventDescription.csv`**
*Description: Maps `keyEventTypeId` to a key event name.*

| Header | Data Type | Description |
| --- | --- | --- |
| keyEventTypeId | Integer | **Primary Key.** Unique identifier for the event type. |
| keyEventName | String | The name of the key event (e.g., "Foul", "Goal"). |

### Event & Play-by-Play Data

These directories contain CSV files broken down by league and season.

**Directory: `keyEvents_data/`** (`keyEvents_{year}_{league}.csv`)
*Description: Detailed information about key events within matches.*

| Header | Data Type | Description |
| --- | --- | --- |
| eventId | Integer | Foreign key for the match (`fixtures.csv`). |
| keyEventOrder | Integer | The order of the key event within the match. |
| playId | String | Identifier for the specific play. |
| keyEventTypeId | Integer | Foreign key for the event type (`keyEventDescription.csv`). |
| period | Integer | The period of the match (1st half, 2nd half, etc.). |
| clockDisplayValue | String | The time of the event as a display string (e.g., "35'"). |
| keyEventText | String | A detailed text description of the event. |
| teamId | Integer | Foreign key for the team involved (`teams.csv`). |
| athleteId | Integer | Foreign key for the player involved (`players.csv`). |
| updateDateTime | DateTime | Timestamp of the last update. |

**Directory: `lineup_data/`** (`lineup_{year}_{league}.csv`)
*Description: Team lineup information for matches.*

| Header | Data Type | Description |
| --- | --- | --- |
| eventId | Integer | Foreign key for the match (`fixtures.csv`). |
| teamId | Integer | Foreign key for the team (`teams.csv`). |
| homeAway | String | Indicates if the team is "home" or "away". |
| winner | Boolean | `True` if this team won the match. |
| formation | String | The formation used by the team (e.g., "4-2-3-1"). |
| starter | Boolean | `True` if the player was in the starting lineup. |
| jersey | Integer | The player's jersey number. |
| athleteId | Integer | Foreign key for the player (`players.csv`). |
| position | String | The player's position (e.g., "Goalkeeper"). |
| subbedIn | Boolean | `True` if the player was substituted in. |
| subbedOut | Boolean | `True` if the player was substituted out. |
| updateTime | DateTime | Timestamp of the last update. |

**Directory: `playerStats_data/`** (`playerStats_{year}_{league}.csv`)
*Description: Aggregated player statistics for a league and season.*

| Header | Data Type | Description |
| --- | --- | --- |
| teamId | Integer | Foreign key for the team (`teams.csv`). |
| athleteId | Integer | Foreign key for the player (`players.csv`). |
| appearances_value | Integer | Number of matches the player appeared in. |
| subIns_value | Integer | Number of times the player was substituted in. |
| foulsCommitted_value | Integer | Total fouls committed by the player. |
| yellowCards_value | Integer | Total yellow cards received. |
| redCards_value | Integer | Total red cards received. |
| goalAssists_value | Integer | Total assists provided. |
| totalShots_value | Integer | Total shots taken. |
| totalGoals_value | Integer | Total goals scored. |
| timestamp | DateTime | Timestamp of the last update. |

**Directory: `plays_data/`** (`plays_{year}_{league}.csv`)
*Description: Detailed play-by-play information for matches.*

| Header | Data Type | Description |
| --- | --- | --- |
| eventId | Integer | Foreign key for the match (`fixtures.csv`). |
| playOrder | Integer | The order of the play within the match. |
| playId | String | Identifier for the specific play. |
| typeId | Integer | Identifier for the type of play. |
| text | String | A detailed text description of the play. |
| period | Integer | The period of the match. |
| clockDisplayValue | String | The time of the play as a display string (e.g., "1'"). |
| teamId | Integer | Foreign key for the team involved (`teams.csv`). |
| athleteId | Integer | Foreign key for the primary player involved. |
| wallclock | DateTime | The actual wall clock time of the play. |
| updateDateTime | DateTime | Timestamp of the last update. |

**Directory: `commentary_data/`** (`commentary_{year}_{league}.csv`)
*Description: Match commentary.*

| Header | Data Type | Description |
| --- | --- | --- |
| eventId | Integer | Foreign key for the match (`fixtures.csv`). |
| commentaryOrder | Integer | The order of the commentary in the match. |
| playId | String | Identifier for the play associated with the commentary. |
| clockDisplayValue | String | The time of the commentary as a display string (e.g., "1'"). |
| commentaryText | String | The text of the commentary. |
| updateDateTime | DateTime | Timestamp of the last update. |
