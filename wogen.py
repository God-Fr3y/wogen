"""
Wordlist Generator Tool for a Single Target

Description:
    This tool is designed to generate a custom wordlist based on a single target's personal information.
    It gathers all available data from the target, such as name, middle name, last name, age, etc., 
    and creates combinations to use for password guessing or recovery purposes.

Example Data:
    - name
    - middle name
    - last name
    - age

Example Combinations:
    - namemiddlename
    - namelastname
    - nameage
    - middlenamename
    - middlenamelastname
    - middlenameage
    - lastnamename
    - lastnamemiddlename
    - lastnameage
    - agename
    - agemiddlename
    - agelastname

Output:
    - All generated combinations are saved into a file named `wordlist.txt`.

Note:
    - Wordlist generation time depends on the amount of data collected.
    - The more input data, the longer the generation process.

Author:
    - God-Fr3y
"""



# ------------------------------------------------------------
# Required Libraries
# ------------------------------------------------------------
# Ensure all required modules are installed before running the script.
# If a module is missing, install it using pip (e.g., pip install phonenumbers).

import os
import sys
import time
import re
import shutil
import datetime
import threading
import itertools
from itertools import product

# External library for phone number parsing and formatting
# Requires: pip install phonenumbers
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from phonenumbers import format_number as frmt_no
from phonenumbers import PhoneNumberFormat as CpNoFrmt


# ------------------------------------------------------------
# Terminal Display Settings
# ------------------------------------------------------------
# Get the width and height of the terminal for layout or formatting purposes
width, height = shutil.get_terminal_size()

# ANSI escape sequences for terminal font coloring
COLOR_GREEN = "\033[1;32;40m"   # Bright green text on black background
COLOR_RED = "\033[1;31;40m"     # Bright red text on black background
COLOR_BLUE = "\033[1;34;40m"  # Bright blue text on black background
COLOR_RESET = "\033[0;37;40m"   # Reset to default (light gray on black)



def count_time(func):
    """
    Decorator to measure and display the execution time of a function.

    Usage:
        Apply @count_time above any function to log how long it takes to run.
    """
    def wrapper(*args, **kwargs):
        # Start the timer
        timer_start = time.time()

        # Execute the decorated function
        return_value = func(*args, **kwargs)

        # End the timer
        timer_end = time.time()

        # Calculate and format the elapsed time
        elapsed_seconds = round(timer_end - timer_start)
        formatted_time = datetime.timedelta(seconds=elapsed_seconds)

        print(f"\nProgram finished in {formatted_time}.")

        return return_value

    return wrapper



class Validator:
    """
    A utility class for validating user input.

    Purpose:
        Ensures that all user-provided data is properly formatted and safe to use,
        preventing runtime errors and improving the accuracy of generated results.

    Usage:
        Use Validator methods to sanitize, normalize, and verify input data
        before it is processed by the core wordlist generation logic.
    """



    def invalid(self):
        """
        Display a standardized invalid input message to the user.
        """
        print(f"{COLOR_RED}Invalid input. Please try again.{COLOR_RESET}")



    def name(self, data):
        """
        Prompt the user for a name-related input (e.g., first name, last name, nickname, or username).
        
        Validates the input to ensure it contains only alphabetic characters.
        - For 'username', accepts input as-is (no validation).
        - For other name types, spaces are stripped and alphabetic-only validation is enforced.
        - If invalid input is provided, the user is prompted again.
        
        Parameters:
            data (str): A label indicating the type of name input (e.g., 'First name: ', 'Username: ').

        Returns:
            str: A cleaned and validated name string.
        """
        if "username" in data.lower():
            # Skip validation for usernames
            return input(f"\n-》{data.capitalize()}: ")

        while True:
            name = input(f"\n-》{data.capitalize()}: ").strip()

            if not name:
                return ""  # Allow empty input if needed

            # Remove spaces and check if alphabetic
            name = name.replace(" ", "")
            if not name.isalpha():
                self.invalid()
                continue

            return name



    def age(self, data):
        """
        Prompt the user to input an age value.

        Validates the input to ensure it is a number within a realistic range (0–99).
        If the input is invalid (non-numeric or out of range), the user is prompted again.

        Parameters:
            data (str): A label or prompt for the input (e.g., "Age: ").

        Returns:
            int or None: The validated age as an integer, or None if the input was left empty.
        """
        while True:
            age = input(f"\n-》{data.capitalize()}: ").strip()

            if not age:
                return None  # Allow empty input

            try:
                age = int(age)
                if age < 0 or age > 99:
                    self.invalid()
                    continue
            except ValueError:
                self.invalid()
                continue

            return age



    def dob(self, data):
        """
        Prompt the user for a date of birth (DOB) and validate the format.

        Ensures the input matches the MM/DD/YYYY format and falls within a reasonable range.
        If the input is invalid, the user is prompted again.

        Parameters:
            data (str): A label or prompt for the input (e.g., "Date of Birth").

        Returns:
            str: The validated date of birth in MM/DD/YYYY format.
        """
        while True:
            dob = input(f"\n-》{data.capitalize()} (MM/DD/YYYY): ").strip()

            if not dob:
                break  # Allow empty input if needed

            # Regex pattern to validate MM/DD/YYYY format
            pattern = r"(0[1-9]|1[012])/(0[1-9]|[12]\d|3[01])/(19|20)\d\d"
            fullmatch = re.fullmatch(pattern, dob)

            if not fullmatch:
                self.invalid()
                continue

            # If the input matches the pattern, break the loop
            break

        return dob



    def email(self, data):
        """
        Prompt the user for an email address and validate it using basic regex pattern

        If the input is invalid, the user is prompted again.

        Parameters:
            data (str): A label or prompt for the input (e.g., "Email").

        Returns:
            str: The validated email address.
        """
        while True:
            email = input(f"\n-》{data.capitalize()}: ").strip()

            if not email:
                return None

            # Check email if match the basic pattern
            pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

            fullmatch = re.match(pattern, email)
            if fullmatch:
                return email
            else:
                self.invalid()



    def phone(self, data):
        """
        Prompt the user to enter a mobile number and validate it using the `phonenumbers` library.

        Ensures the number is in a valid international format (e.g., +639123456789) and converts
        it to a clean, national format. If invalid, the user is prompted to re-enter.

        Parameters:
            data (str): A label or prompt for the input (e.g., "Phone Number").

        Returns:
            str or None: The validated phone number in national format, or None if input is empty.
        """
        while True:
            cp_no = input(f"\n-》{data.capitalize()} (+639123456789): ").strip()

            if not cp_no:
                return None  # Allow empty input

            try:
                # Parse the input number using phonenumbers
                cp_no_parsed = phonenumbers.parse(cp_no, None)

                # Validate if it's a proper number
                if phonenumbers.is_valid_number(cp_no_parsed):
                    # Format it into national format and remove spaces
                    cp_no = frmt_no(cp_no_parsed, CpNoFrmt.NATIONAL).replace(" ", "")
                    break
                else:
                    self.invalid()

            except NumberParseException:
                print(COLOR_RED + "Invalid number. Please try again." + COLOR_RESET)

        return cp_no



    def symbols(self, data):
        """
        Prompt the user to enter symbols to enhance the strength of the wordlist.

        Displays a set of recommended symbols and validates if input contains non-alphanumeric characters.
        If valid, converts the input string into a list of individual symbols.

        Parameters:
            data (str): A label or prompt for the input (e.g., "Symbols").

        Returns:
            list or None: A list of symbols, or None if input is empty.
        """
        print("\n")
        msg = "Including symbols can make your wordlist stronger"
        syms = "@#$_&-+()/"
        print(msg.center(width))
        print(syms.center(width))

        while True:
            symbols = input(f"\n-》{data.capitalize()}: ").strip()
            if not symbols:
                break  # Allow empty input

            # Ensure the input contains at least one symbol (non-alphanumeric)
            if not re.search(r"\W", symbols):
                self.invalid()
                continue

            break  # Input is valid

        # Convert the string of symbols into a list of characters
        return list(symbols)



    def additional_words(self, data):
        """
        Prompt the user to enter additional words that may be relevant to the target.

        These words could include favorite foods, pet names, places, hobbies, etc.
        The function keeps collecting inputs until the user presses Enter without typing anything.

        Parameters:
            data (str): A label or prompt for the input (e.g., "Additional Words").

        Returns:
            list: A list of additional words provided by the user.
        """
        print("\n")
        prompts = [
            "Add some words that could be part of a possible password.",
            "Examples: favorite food, place, pet name, hobby, etc.",
            "Press Enter without typing anything to skip."
        ]

        for msg in prompts:
            print(msg.center(width))

        print("\n")

        words = []
        while True:
            word = input(f"\n-》{data.capitalize()}: ").strip()
            if word:
                word = word.replace(" ", "")  # Remove spaces for stronger permutations
                words.append(word)
            else:
                break

        return words





class WoGen(Validator):
    """
    WoGen (Wordlist Generator) is a custom tool designed for advanced wordlist creation,
    primarily for password guessing, testing, or recovery. It inherits data validation 
    features from the Validator class and combines user-provided personal information 
    into structured, permutated password candidates.

    Features:
    - Collects detailed target and partner information (names, dates, contact info, etc.)
    - Supports initials extraction and custom additional inputs (words, symbols)
    - Generates permutations with optional leetspeak variants
    - Allows customization of password length and data combinations
    - Displays real-time loading animation during generation
    - Outputs results to a plain-text file for further use in audits or testing
    """
    def __init__(self):
        # Control flag for the loading animation thread
        self.run_loading = False



    def loading(self):
        """Displays a spinning loading icon in the terminal while passwords are being generated."""
        for icon in itertools.cycle(["|", "/", "-", "\\", "-"]):
            if not self.run_loading:
                break
            sys.stdout.write(f"\rGenerating ... {icon}")
            sys.stdout.flush()
            time.sleep(0.1)



    def banner(self):
        """
        Clears the terminal and displays the WoGen ASCII banner.
        """
        # Clear terminal screen based on OS
        os.system("cls" if os.name == "nt" else "clear")

        banner = [
            "......................................................",
            "'##:::::'##::'#######:::'######:::'########:'##::: ##:",
            " ##:'##: ##:'##.... ##:'##... ##:: ##.....:: ###:: ##:",
            " ##: ##: ##: ##:::: ##: ##:::..::: ##::::::: ####: ##:",
            " ##: ##: ##: ##:::: ##: ##::'####: ######::: ## ## ##:",
            " ##: ##: ##: ##:::: ##: ##::: ##:: ##...:::: ##. ####:",
            " ##: ##: ##: ##:::: ##: ##::: ##:: ##::::::: ##:. ###:",
            ". ###. ###::. #######::. ######::: ########: ##::. ##:",
            ":...::...::::.......::::......::::........::..::::..::",
            "'''''''''''''’''''''''''''''''''''''''''''''''''''''''",
        ]

        for design in banner:
            print(COLOR_GREEN + design.center(width) + COLOR_RESET)

        print(COLOR_BLUE + "- GODFR3Y".center(width + 30) + COLOR_RESET)
        print("\n\n\n\n")



    def get_data(self):
        """
        Collect personal and partner data from the user.
        Validates each input using Validator methods.

        Returns:
            tuple: Cleaned and validated target data.
        """
        print("\n\n\n\nPlease provide all information when prompted.")
        print("Press Enter to skip any field\n")

        target_info = []

        # Collect target's personal information
        target_fields = ["firstname", "middlename", "lastname", "nickname", "username"]
        for field in target_fields:
            target_info.append(self.name(field))

        dob_orig = self.dob("dob")      # MM/DD/YYYY
        dob = dob_orig.replace("/", "")       # MMDDYYYY
        target_info.append(dob_orig)
        target_info.append(dob)
        target_info.append(dob[:2])     # Day
        target_info.append(dob[2:4])    # Month
        target_info.append(dob[4:])     # Year

        target_info.append(self.age("age"))
        target_info.append(self.phone("phonenumber"))
        target_info.append(self.email("email"))

        print("\n")
        for msg in [
            "Some additional information based on the",
            "target's life partner can be useful",
            "to enhance your wordlist"
        ]:
            print(msg.center(width))

        # Collect partner's personal information
        partner_fields = [
            "partner's firstname", "partner's middlename", "partner's lastname",
            "partner's nickname", "partner's username"
        ]
        for field in partner_fields:
            target_info.append(self.name(field))

        target_info.append(self.age("partner's age"))

        partner_dob_orig = self.dob("dob")
        partner_dob = partner_dob_orig.replace("/", "")
        target_info.append(partner_dob_orig)
        target_info.append(partner_dob)
        target_info.append(partner_dob[:2])
        target_info.append(partner_dob[2:4])
        target_info.append(partner_dob[4:])

        target_info.append(self.phone("partner's phonenumber"))
        target_info.append(self.email("partner's email"))

        # Important dates
        date_engaged = self.dob("date engaged").replace("/", "")
        target_info.append(date_engaged)
        target_info.append(date_engaged[:2])
        target_info.append(date_engaged[2:4])
        target_info.append(date_engaged[4:])

        # Additional inputs
        target_info.extend(self.additional_words("words"))
        target_info.extend(self.symbols("symbols"))

        # Clean and return data
        return tuple(str(item) for item in target_info if item)



    def min_pass_len(self):
        """
        Prompt the user for the minimum password length.

        Ensures that the input is a positive integer. Re-prompts if the input
        is invalid or less than or equal to zero.

        Returns:
            int: The validated minimum password length.
        """
        while True:
            try:
                min_char = int(input("\nMinimum password length: "))
                if min_char <= 0:
                    self.invalid()
                    continue
                return min_char # Exits both the loop and function if valid
            except ValueError:
                self.invalid()



    def max_pass_len(self, min_char):
        """
        Prompt the user to enter the maximum password length.
        
        Ensures the input is a valid positive integer and 
        greater than the given minimum length to avoid logical errors.
        """
        while True:
            try:
                max_char = int(input("\nMaximum password length: "))
                if max_char <= 0 or max_char <= min_char:
                    self.invalid()
                    continue
                return max_char  # Exits both the loop and function if valid
            except ValueError:
                self.invalid()



    def word_to_combine(self):
        """
        Prompt the user for the maximum number of elements to combine
        when generating password permutations.

        Displays an informative guide and warns that higher values increase processing time.
        """
        msgs = [
            "\n",
            "\b",
            "Data:  a b c d",
            "\n",
            "2       3       4",
            "ab      abc     abcd",
            "ac      abd     abdc",
            "ad      acb     acbd",
            "ba      acd     acdb",
        ]

        for msg in msgs:
            print(msg.center(width))

        print("\n\n" + "WARNING! The higher the number,")
        print("the longer it takes to create.".center(width))

        while True:
            try:
                num = int(input("\nUp to how many data to combine: "))
                return num  # Exits the loop and returns if input is valid
            except ValueError:
                self.invalid()
 


    def enable_leetspeak(self):
        """
        Ask the user whether to enable leetspeak transformation.

        Returns:
            bool: True if leetspeak is enabled, False otherwise.
        """
        while True:
            choice = input("\nEnable leet speak? [y|n]: ").strip().lower()
            if choice == "y":
                return True  # Return immediately if enabled
            elif choice == "n":
                return False  # Return immediately if disabled
            else:
                self.invalid()  # Handle invalid input

    
    def leetspeak_maxvariants(self):
        """
        Prompt the user to specify how many leetspeak variants to generate.

        Returns:
            int: The number of leetspeak variants specified by the user.
        """
        while True:
            try:
                variants = int(input("\nHow many leetspeak variants to be made?: "))
                break
            except ValueError:
                self.invalid()
                continue
        return variants 



    def leetspeak(self, word, max_variants):
        """
        Generate advanced leetspeak variants of a word using a comprehensive substitution map.

        Parameters:
            word (str): The input word to be converted into leetspeak.
            max_variants (int): The maximum number of leetspeak variants to generate.

        Returns:
            set: A set containing up to `max_variants` leetspeak variations of the input word.
        """

        # Full leetspeak substitution map for each character
        LEET_MAP = {
            'a': ['@', '4', '/\\', '^', 'α'],
            'b': ['8', 'ß', '|3', '13'],
            'c': ['<', '(', '{', '[', '¢'],
            'd': ['|)', 'cl', 'Ð'],
            'e': ['3', '€', '&'],
            'f': ['|=', 'ph', 'ƒ'],
            'g': ['6', '9', '&', '(_+'],
            'h': ['#', '|-|', ']-[', ')-(', '}{'],
            'i': ['1', '!', '|', 'eye', ']['],
            'j': ['_|', '_/'],
            'k': ['|<', '|{', 'X'],
            'l': ['1', '|', '£', '¬'],
            'm': ['|\\/|', '/\\/\\', '(V)', '^^'],
            'n': ['|\\|', '/\\/', '^/'],
            'o': ['0', '()', '*', '°'],
            'p': ['|*', '|o', '|>', '9'],
            'q': ['0_', 'kw', 'O,'],
            'r': ['|2', '®', '12'],
            's': ['$', '5', '§'],
            't': ['7', '+', '†'],
            'u': ['|_|', 'µ', '[_]'],
            'v': ['\\/', '|/', '\\|'],
            'w': ['\\/\\/', 'vv', '\\^/', '\\/\\/', 'uu'],
            'x': ['><', '}{', '×'],
            'y': ['`/', '¥', 'j'],
            'z': ['2', '≥', '"/_']
        }

        word = word.lower()  # Normalize the word to lowercase
        chars = []

        # Build a list of possible substitutions for each character
        for char in word:
            substitutions = [char] + LEET_MAP.get(char, [])  # Include the original character
            chars.append(substitutions)

        variants = set()

        # Generate all possible combinations using Cartesian product
        for combo in product(*chars):
            variant = ''.join(combo)
            variants.add(variant)
            if len(variants) >= max_variants:  # Stop when we reach the desired number of variants
                break

        return variants



    def extract_initials(self, data):
        """
        Extract the first alphabetical character from each string element in the list.

        Args:
            data (list): A list of strings to extract initials from.

        Returns:
            list: A list containing the first alphabetical character of each valid string.
        """
        return [d[0] for d in data if d and d[0].isalpha()]  # Ensure element is not empty and starts with a letter 



    def gen_pass(self, min_char, max_char, data, word_to_combine, is_leet, max_variants):
        """
        Generate passwords by combining words, applying capitalization styles,
        optionally adding leetspeak variants, and filtering by length.

        Args:
            min_char (int): Minimum allowed password length.
            max_char (int): Maximum allowed password length.
            data (list): List of base words/strings to combine.
            word_to_combine (int): Max number of elements to combine at once.
            is_leet (bool): Whether to generate leetspeak variants.
            max_variants (int): Max number of leetspeak variants per word.

        Yields:
            str: Unique password candidate.
        """
        seen = set()
        full_data = data.copy()

        # Extract and add initials to the data pool
        initials = self.extract_initials(data)
        full_data += initials

        for num in range(1, word_to_combine + 1):
            for combo in itertools.permutations(full_data, num):
                base = ''.join(combo)

                if min_char <= len(base) <= max_char:
                    # Generate capitalization variants
                    variants = {
                        base,
                        base.lower(),
                        base.upper(),
                        base.capitalize(),
                        ''.join([w.capitalize() for w in combo])  # TitleCase
                    }

                    # Generate leetspeak variants if enabled
                    if is_leet:
                        leet_variants = set()
                        for v in variants:
                            leet_variants.update(self.leetspeak(v, max_variants))
                        variants.update(leet_variants)

                    # Yield only unique passwords
                    for pwd in variants:
                        if pwd not in seen:
                            seen.add(pwd)
                            yield pwd



    def create(self, min_char, max_char, data, word_to_combine, is_leet=False, max_variants=0):
        """
        Create a wordlist of generated passwords and save them to a file.
        
        This method uses permutations of the provided data to generate passwords 
        within the specified character length range (min_char to max_char). It also 
        supports leetspeak variants and ensures no duplicate passwords are written 
        to the output file.
        
        Args:
            min_char (int): Minimum password length.
            max_char (int): Maximum password length.
            data (list): List of data elements (e.g., names, dates) to generate passwords from.
            word_to_combine (int): Maximum number of data items to combine for password creation.
            is_leet (bool): Flag to indicate whether to apply leetspeak transformations. Default is False.
            max_variants (int): Maximum number of variants for each password. Default is 0 (no limit).
        
        Writes:
            Wordlist.txt: A text file containing the generated passwords.
        """
        # Sort the data by length to start with shorter elements
        data = sorted(data, key=len)

        # Open the Wordlist.txt file in write mode
        with open("Wordlist.txt", "w+", encoding="utf-8") as wordlist:
            # Generate passwords using the gen_pass method and write them to the file
            for passw in self.gen_pass(min_char, max_char, data, word_to_combine, is_leet, max_variants):
                wordlist.write(passw + "\n")



    def count_line(self):
        """
        Count the number of createe passwords in the 'Wordlist.txt' file.
        """

        with open("Wordlist.txt", "r", encoding="utf-8") as wordlist:
            count = sum(1 for line in wordlist)

        print(f"""\n\n{COLOR_GREEN}{count:,} passwords have been successfully saved to
    {COLOR_RESET}'Wordlist.txt'{COLOR_GREEN} in the same directory.{COLOR_RESET}

    {COLOR_RED}The developer of this code is not responsible for any misuse of this tool.
    You have been warned!{COLOR_RESET}""")



    @count_time
    def main(self):
        """
        Main function to generate a wordlist based on user input.

        This function guides the user through the process of generating passwords
        by:
        - Collecting target data from the user.
        - Asking for minimum and maximum password lengths.
        - Determining how many data combinations to generate.
        - Allowing the option to enable leetspeak and configure the number of variants.
        - Asking whether to generate the wordlist or not.
        - Creating the wordlist file and displaying a motivational message during the process.
        - Showing the total number of passwords generated once the process is completed.

        Returns:
            None
        """

        # Step 1: Collect target data from the user
        data = self.get_data()

        # Step 2: Get the minimum password length from the user
        min_char = self.min_pass_len()

        # Step 3: Get the maximum password length from the user
        max_char = self.max_pass_len(min_char)

        # Step 4: Get the number of data combinations to generate
        word_to_combine = self.word_to_combine()

        # Step 5: Ask the user if they want to enable leetspeak
        is_leet = self.enable_leetspeak()

        # Step 6: If leetspeak is enabled, ask how many variants to generate
        if is_leet:
            max_variants = self.leetspeak_maxvariants()
        else:
            max_variants = 0

        # Step 7: Prompt the user to decide whether to generate the wordlist or not
        while True:
            generate = input("\n\nGenerate a wordlist? [Y|N]: ").upper()
            
            if generate == "Y":
                self.run_loading = True
                loading = threading.Thread(target=self.loading)
                loading.start()

                # Step 8: Create the wordlist based on the user's preferences
                if is_leet:
                    self.create(min_char, max_char, data, word_to_combine, is_leet, max_variants)
                else:
                    self.create(min_char, max_char, data, word_to_combine, is_leet=False, max_variants=0)

                self.run_loading = False
                break
            elif generate == "N":
                sys.exit()
            else:
                self.invalid()

        # Step 9: Count how many passwords were generated and saved
        self.count_line()   



if __name__ == "__main__":
    app = WoGen()
    app.banner()
    app.main()
