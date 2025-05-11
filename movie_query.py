import sys
from typing import Optional

from pydantic import BaseModel, Field, field_validator

'''
Task: Create a Movie Data Query and Analysis CLI Tool
Description:

Build a CLI tool that processes a dataset of the provided IMDb Top 1000 movies dataset. The tool should enable users to query and filter data based on multiple criteria, output results in a specified format, and provide summary statistics for filtered results.

Note: Please use your best judgment if an instruction is unclear or fails to identify all possible scenarios. Explain your rationale for why you chose to implement your particular solution.
Data Structure:

Each entry in the dataset represents a movie and includes:

Title: Movie title
Year: Release year
Runtime: Duration in minutes
Genre: Main genre(s) (e.g., “Drama, Comedy”)
IMDb Rating: Rating on a scale of 1–10
Overview: Movie summary
Meta Score: Metascore rating
Director: Director’s name
Stars: Top-billed actors (4)
Votes: IMDb votes received
Gross: Gross revenue in USD
Requirements:

Data Input: 
Accepts a CSV file as input. Include error handling for missing or invalid files.

Query Options: 
Allow filtering by:
Year: Before/after a given year (e.g., --year-after 2000)
Genre: Movie genre (e.g., --genre "Action")
IMDb Rating: Above/below a specified rating (e.g., --rating-above 8)
Director: Movies by a specific director (e.g., --director "Christopher Nolan")
Actor: Movies starring a specific actor (e.g., --actor "Tom Hanks")
Runtime: Movies shorter or longer than a specified duration (e.g., --runtime-more-than 120)
Gross: Movies with gross revenue above/below a value (e.g., --gross-min 100000000)
Output:
Print filtered results to the terminal in readable plain-text table or list format. Maintain a sort of IMDb rating from highest rank to lowest.

Bonus Features (Optional):

Output:
Specify output format (json, csv, or plain text) and file name (default to “filtered_movies”).
Top 10 Lists and Recommendations:
Generate and display Top 10 lists based on criteria such as highest-rated, most popular (by vote count), or highest-grossing movies within filtered results.
Example: --top-10 "highest-rated" to see the top 10 highest-rated movies in the filtered set.
Genre-Based Insights:
Provide a breakdown of the average rating, gross revenue, and runtime by genre within filtered results. This could be helpful for users wanting a deeper look into specific genres.
Example: --genre-insights outputs statistics on each genre within the filtered set.
“Hidden Gems” Finder:
Identify “hidden gems” by highlighting highly-rated movies with lower vote counts. This could help users find underrated films they might not have otherwise noticed.
Example: --find-hidden-gems lists movies with high ratings and low vote counts.

'''


# Establishing sensible constraints based on problem description
class MovieMetric(BaseModel):
    series_title: str
    released_year: Optional[int]
    certificate: Optional[str]
    runtime: Optional[int] = Field(gt=0)
    genre: Optional[str]
    imdb_rating: Optional[float] = Field(ge=0, le=10)
    overview: Optional[str]
    meta_score: Optional[int] = Field(gt=0, le=100)
    director: Optional[str]
    star_1: Optional[str]
    star_2: Optional[str]
    star_3: Optional[str]
    star_4: Optional[str]
    no_of_votes: Optional[int] = Field(gt=0)  # cant have negative votes
    gross: Optional[int]

    @field_validator("runtime", mode="before")
    def extract_runtime(cls, value) -> Optional[int]:
        return int(value.split()[0]) if value else None

    @field_validator("gross", mode="before")
    def format_gross(cls, value) -> Optional[int]:
        return int(value.replace(',', '')) if value else None

    @field_validator("meta_score", mode="before")
    def format_meta_score(cls, value) -> Optional[int]:
        # Treat empty strings as None
        return int(value) if value and value.isnumeric() else None

    @field_validator("released_year", mode="before")
    def format_released_year(cls, value: str) -> Optional[int]:
        # Treat empty strings as None
        return int(value) if value and value.isnumeric() else None

    def row_vals(self):
        return f"{self.series_title} {self.released_year} {self.certificate} {self.runtime} {self.genre} {self.imdb_rating} {self.overview} {self.meta_score} {self.director} {self.star_1} {self.star_2} {self.star_3} {self.star_4} {self.no_of_votes} {self.gross}"

    def __repr__(self):
        return f"\n\n{self.series_title} ({self.released_year}) - IMDB: {self.imdb_rating} - {self.runtime} mins\nDirected by {self.director}\nStarring: {', '.join([self.star_1, self.star_2, self.star_3, self.star_4])}\n"


class MovieQuery:
    help_text = '''
    Movie Query Tool \n
    FORMAT: [movie_file_name] [--flag (value | 'value')] \n
        Available filter flags: 
            --year-before integer 
            --year-after integer
                filter movies released before or after a given year 
                example: --year-after 2000
            --rating-above number       
            --rating-below number       
                filter movies with an IMDB rating above or below a given range in [0.0 - 10.0] 
                example: --rating-above 8.3
            --runtime-above number 
            --runtime-below number
                filter movies with a runtime above or below a given time value in minutes 
                example: --runtime-above 120
            --gross-above number  
            --gross-below number
                filter movies with a gross revenue above or below a given dollar value
                example: --gross-above 100000000
            --score-above number
            --score-below number
                filter movies with a meta score above or below a given range in [0 - 100]
                example: --score-above 80
            --votes-above number
            --votes-below number
                filter movies with a number of votes above or below a given range
                example: --votes-above 1000000
            --title 'string'
            --director 'string'      
            --actor 'string'         
            --genre 'string'  
            --age-rating 'string'  
                filter movies by a specific director, actor, genre or age rating 
                example: --director 'Christopher Nolan' --age-rating 'PG-13'

        Available command flags:
            --top-ten 'highest-rated' | 'most-popular' | 'highest-grossing' | 'longest-runtime' | 'hidden-gems' 
                filter movies to get top 10 list of either highest ratings, most popular, highest-grossing, longest runtime 
                or hidden gems (highly rated with low votes) movies
            --insights 'genre' | 'year' 
                generate insights on the list of filtered/non-filtered movies
                average rating, gross and runtime by genre or year
            --output 'filename[.json | .csv | .txt]'
                specify filename with or without extension to save the query results

        '''

    def __init__(self):

        # flag mapping, skips over null values
        self.flag_map = {
            "--year-before": lambda movie, year: movie.released_year and movie.released_year < int(year),
            "--year-after": lambda movie, year: movie.released_year and movie.released_year > int(year),
            "--rating-above": lambda movie, rating: movie.imdb_rating and movie.imdb_rating > float(rating),
            "--rating-below": lambda movie, rating: movie.imdb_rating and movie.imdb_rating < float(rating),
            "--runtime-above": lambda movie, runtime: movie.runtime and movie.runtime > int(runtime),
            "--runtime-below": lambda movie, runtime: movie.runtime and movie.runtime < int(runtime),
            "--gross-above": lambda movie, gross: movie.gross and movie.gross > int(gross),
            "--gross-below": lambda movie, gross: movie.gross and movie.gross < int(gross),
            "--score-above": lambda movie, score: movie.meta_score and movie.meta_score > int(score),
            "--score-below": lambda movie, score: movie.meta_score and movie.meta_score < int(score),
            "--votes-above": lambda movie, votes: movie.no_of_votes and movie.no_of_votes > int(votes),
            "--votes-below": lambda movie, votes: movie.no_of_votes and movie.no_of_votes < int(votes),
            "--title": lambda movie, title:
            movie.series_title and title.lower() in movie.series_title.lower(),
            "--director": lambda movie, director:
            movie.director and director.lower() in movie.director.lower(),
            "--actor": lambda movie, actor:
            actor.lower() in (
                movie.star_1.lower(),
                movie.star_2.lower(),
                movie.star_3.lower(),
                movie.star_4.lower(),
            ),
            "--genre": lambda movie, genre:
            movie.genre and genre.lower() in movie.genre.lower().split(","),  # potential multi-match
            "--age-rating": lambda movie, certificate:
            movie.certificate and movie.certificate.lower() == certificate.lower(),
        }

        self.top_ten_map = {
            "highest-rated": lambda movies: sorted(movies, key=lambda movie: -movie.imdb_rating)[:10],
            "most-popular": lambda movies: sorted(movies, key=lambda movie: -movie.no_of_votes)[:10],
            "highest-grossing": lambda movies: sorted(movies, key=lambda movie: -movie.gross)[:10],
            "longest-runtime": lambda movies: sorted(movies, key=lambda movie: -movie.runtime)[:10],
            # Custom weight based on inverse relationship between rating and votes
            "hidden-gems": lambda movies:
                sorted(movies,key=lambda movie: (-movie.imdb_rating / movie.no_of_votes))[:10],
        }

        self.insights_map = {
            "genre": self.generate_genre_insights,
            "year": self.generate_year_insights
        }

        self.command_map = {
            "--top-ten": self.top_ten_map,
            "--output": self.print_output,
            "--insights": self.generate_genre_insights,
        }

    @staticmethod
    def generate_year_insights(movies: list[MovieMetric]) -> None:
        years = {movie.released_year for movie in movies}
        stats = []
        for year in years:
            stat = {"year": year}
            rating, gross, runtime, total = 0, 0, 0, 0
            for movie in movies:
                # Null values will mess up our average so we skip entire row
                if year == movie.released_year and movie.imdb_rating and movie.gross and movie.runtime:
                    rating += movie.imdb_rating
                    gross += movie.gross
                    runtime += movie.runtime
                    total += 1
            if total > 0:
                stat["average_rating"] = rating / total
                stat["average_gross"] = gross // total
                stat["average_runtime"] = runtime // total
                stats.append(stat)

        stats.sort(key=lambda s: -s["year"])
        print("Printing insights by year:")
        for stat in stats:
            print(
                f"Year: {stat['year']}, Average Rating: {round(stat['average_rating'], 2)}, Average Gross: ${stat['average_gross']}, Average Runtime: {stat['average_runtime']} mins")

    @staticmethod
    def generate_genre_insights(movies: list[MovieMetric]) -> None:
        genres = {movie.genre for movie in movies}
        stats = []
        for genre in genres:
            stat = {"genre": genre}
            rating, gross, runtime, total = 0, 0, 0, 0
            for movie in movies:
                # Null values will mess up our average so we skip entire row
                if genre in movie.genre.split(",") and movie.imdb_rating and movie.gross and movie.runtime:
                    rating += movie.imdb_rating
                    gross += movie.gross
                    runtime += movie.runtime
                    total += 1
            if total > 0:
                stat["average_rating"] = rating / total
                stat["average_gross"] = gross // total
                stat["average_runtime"] = runtime // total
                stats.append(stat)

        print("Printing insights by genre:")
        for stat in stats:
            print(
                f"Genre: {stat['genre']}, Average Rating: {round(stat['average_rating'], 2)}, Average Gross: ${stat['average_gross']}, Average Runtime: {stat['average_runtime']} mins")

    @staticmethod
    def print_output(movies: list[MovieMetric], filename: str):
        import json
        import csv

        file_format = filename.split(".")[-1]
        try:
            if file_format == "json":
                with open(filename, "w") as json_file:
                    data = [movie.model_dump() for movie in movies]
                    json.dump(data, json_file)
            elif file_format == "csv":
                with open(filename, "w") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=list(MovieMetric.model_fields.keys()))
                    writer.writeheader()
                    for movie in movies:
                        writer.writerow(movie.model_dump())
            else:
                with open(filename, "w") as text_file:
                    text_file.write(str(list(MovieMetric.model_fields.keys()))[1:-1] + "\n")
                    for movie in movies:
                        text_file.write(movie.row_vals() + "\n")

        except Exception as e:
            exit(f"Error writing to json file '{filename}': {e}")

    @staticmethod
    def load_movies(file_path: str) -> list[MovieMetric]:
        import csv
        movies = []
        try:
            with open(file_path, newline="") as data_file:
                reader = csv.DictReader(data_file)
                movies = [MovieMetric(**row) for row in reader]
        except FileNotFoundError:
            exit(f"Error: The csv file '{file_path}' was not found.")
        except OSError:
            exit(f"Error opening csv file '{file_path}'")
        movies.sort(key=lambda x: x.imdb_rating, reverse=True)
        return movies

    def collect_filters(self, args: list[str], index: int) -> tuple[dict[str, str], dict[str, str]]:
        filters = {}  # can't have duplicate flags
        commands = {}
        while index < len(args):
            flag = args[index]
            if flag.startswith("--"):
                if index + 1 < len(args) and not args[index + 1].startswith("--"):
                    if flag in self.flag_map:
                        filters[flag] = args[index + 1]
                    elif flag in self.command_map:
                        if flag in commands:
                            print(f"Duplicate action flag: {flag}. Ignoring.")
                        else:
                            commands[flag] = args[index + 1]
                    else:
                        exit(f"Unknown flag: {flag}")
                else:
                    exit(f"Missing argument value for flag: {flag}")
                index += 2
            else:
                exit("Invalid flag. Please start flags with '--' followed by an argument.")
        return filters, commands

    def filter_results(self, movies: list[MovieMetric], filters: dict[str, str]) -> list[MovieMetric]:
        results = []
        for movie in movies:
            match_all_filters = True
            abort = False
            for flag, value in filters.items():
                try:
                    match_all_filters = match_all_filters and self.flag_map[flag](movie, value)
                except ValueError:
                    print(f"Error: {value} is not a valid argument for flag {flag}.")
                    abort = True
            if abort:
                exit("Please fix the error and try again.")
            if match_all_filters:
                results.append(movie)
        return results

    def perform_commands(self, movies: list[MovieMetric], commands: dict[str, str]) -> None:

        if "--top-ten" in commands:
            value = commands["--top-ten"]
            if value in self.top_ten_map:
                movies = self.top_ten_map[value](movies)
            else:
                exit(f"Unknown value: {value}")
        if "--output" in commands:
            self.command_map["--output"](movies, commands["--output"])
            print(f"Printed {len(movies)} movies to file {commands['--output']}")
        else:
            print(movies)
            print(f"Printed {len(movies)} movies to terminal")
        # print insights last on the final filtered list
        if "--insights" in commands:
            value = commands["--insights"]
            if value in self.insights_map:
                self.insights_map[value](movies)
            else:
                exit(f"Unknown value: {value}")

    def run_movie_query(self, args: list[str]) -> None:
        movies, index = [], 0
        if args[0].startswith("--"):
            print("File Missing. Using default data file.")
            movies = self.load_movies("imdb_top_1000.csv")
        elif args[0].split(".")[-1] == "csv":
            movies = self.load_movies(args[0])
            index = 1
        else:
            print("Invalid file format. Using default data file.")
            movies = self.load_movies("imdb_top_1000.csv")

        filters, commands = self.collect_filters(args, index)

        results = movies
        if filters:
            results = self.filter_results(movies, filters)
            print(f"Found {len(results)} movies matching the filter flags")

        self.perform_commands(results, commands)


if __name__ == "__main__":
    # movies = []
    arguments = sys.argv[1:]
    if len(arguments) == 0:
        exit("No arguments provided. Use --help or -h for usage instructions.")
    if arguments[0] in ("--help", "-h"):
        exit(f"{MovieQuery.help_text}")

    app = MovieQuery()
    app.run_movie_query(arguments)