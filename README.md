# Read Me

### Instructions to run

**NOTE:** This program was tested on python 3.13.2

1. Clone the repository and navigate to its root directory
   ```bash
   git clone https://github.com/rblis/css-movie-query.git; cd css-movie-query;
   ```
2. Create a virtual environment
   ```bash
   python3 -m venv .venv
   ```
3. Activate the virtual environment
    ```bash
    source .venv/bin/activate
    ```
4. Install the required packages
   ```bash
   pip install -r requirements.txt
   ```
5. Deactivate the virtual environment when done
   ```bash
   deactivate
   ```


### To view operating instructions
   ```bash
   python movie_query.py --help
   ```
   
### Example Usages

1. To search for movies with the word 'rain' in the title and released after the year 2000

   ```bash
   python movie_query.py --title rain --year-after 2000
   ```
2. To search for movies with actor 'Brad Pitt' and find out statics about his movies by year

   ```bash
   python movie_query.py --actor 'Brad Pitt' --insights 'year'
   ```
   **NOTE:** You can omit the quotes around a value if it doesn't contain spaces


4. To search for the top ten highest grossing movies that are rated 'PG-13' and print the output to a file called top_ten_results.csv

   ```bash
   python movie_query.py --age-rating 'PG-13' --top-ten 'highest-rated' --output top_ten_results.csv
   ```
   **NOTE:** If you omit the --output flag, the results will be printed to the console.

### Design Notes

1. The program is designed to accept a file path as the first argument, if none is provided it defaults to the supplied data file in its root directory.
2. Flags are defined in a map that contains lambda functions to quickly generate the appropriate conditions for the specified flag. This reduces LOC and prevents the file from being cluttered by simple helper methods.
3. The output to the terminal omits several fields to preserve readability. However, output to files maintains all original fields of the model as it is meant to be imported into other programs.

**BONUS**

4. The flag system is desigend to use two cli arguments: --flag value. Thefore some of the bonus feature requirements have been altered to support the app's base architecture. The flag filter options have also been extended to include more fields from the original data model such as age-rating, meta-score, and votes. This flag map system allows for easy extension of additional flags.
5. The output system always requires a value for the filename, if no output flag is supplied, then the results are printed to the terminal.
6. The top ten lists flags work similar to the filter flag and returns a sorted result that is at most 10 items long.
7. The hidden gems bonus feature is implmented as a top ten list with a custom weight function to determine the rank. It calculates a custom weight by dividing the ratings of movies with its vote count to represent an inverse relationship.
8. Genre based insight bonus feature is extended to include groupings by years in order to follow the two arguments flag system. It can provide powerful insights when filtering on an actor or director. 