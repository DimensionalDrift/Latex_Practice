import os
import random

# Madlib Generator

# This is a version of a madlib generator that uses python to insert
# words into an existing latex template. The program reads in the latex
# document, looks for the keywords that are used as variables in the
# madlib and inserts the appropriate word into the story. Then a new
# latex document is saved and the latexmk command is run to generate a
# pdf of the madlib.

# The madlib and the list of random words were sourced from a COMP 101
# exercise that can be found here:
# https://www.cs.unc.edu/Courses/comp101-f14/labassigns/lab17.html


def replace_random(text, word, wordlist):
    """Function to replace a word with a random word from a given list

    Parameters
        ----------
        text : string
            A string of text that has words that need to be replaced.
        word : string
            A string that will be replaced in text.
        wordlist : list
            A list of strings to pick from at random to replace the
            keyword with.

    Returns
        ----------
        text : string
            A string with the words replaced.
    """

    # Number of times that the word occurs in the text
    num = text.count(word)

    # For each time the word occurs, replace the first instance of the
    # word with a random word from the list of words
    for i in range(num):
        new_word = random.choice(wordlist)
        text = text.replace(word, new_word, 1)

    # Return the text
    return text


def main():

    # List of exclamations
    exclamations = [
        "Zounds",
        "Egads",
        "Yikes",
        "Goodness",
        "Oh no",
        "Jeepers",
        "Oh my",
        "Argh",
        "Holy Moly",
    ]

    # List of adverbs
    adverbs = [
        "sadly",
        "rapidly",
        "happily",
        "hurriedly",
        "haphazardly",
        "madly",
        "slowly",
        "awkwardly",
        "fiercely",
        "fearlessly",
    ]

    # List of adjectives
    adjectives = [
        "scary",
        "frightening",
        "funny",
        "silly",
        "frightened",
        "bizarre",
        "terrifying",
        "horrid",
        "happy",
        "skinny",
    ]

    # List of verbs
    verbs = [
        "walk",
        "talk",
        "meander",
        "burn",
        "twirl",
        "frighten",
        "leap",
        "saunter",
        "totter",
        "twirl",
    ]

    # List of nouns
    nouns = [
        "witch",
        "monster",
        "ogre",
        "zombie",
        "pumpkin",
        "cat",
        "broom",
        "ghost",
        "grave",
        "devil",
    ]

    # Open the tex file and read it in as a string
    with open("madlib_template.tex", "r") as myfile:
        texfile = myfile.read()

    # Replace the exclamations
    texfile = replace_random(texfile, "<exclamation>", exclamations)

    # Replace the adverbs
    texfile = replace_random(texfile, "<adverb>", adverbs)

    # Replace the adjectives
    texfile = replace_random(texfile, "<adjective>", adjectives)

    # Replace the verbs
    texfile = replace_random(texfile, "<verb>", verbs)

    # Replace the nouns
    # Originally there was only one noun label but the story didn't
    # make a lot of sense if each noun was random so I amended the
    # variables to use the same noun for some parts of the story
    texfile = replace_random(texfile, "<noun>", nouns)
    texfile = texfile.replace("<noun_1>", random.choice(nouns))
    texfile = texfile.replace("<noun_2>", random.choice(nouns))

    # Create a new latex file and write the amended text to the file
    with open("madlib_gen.tex", "w+") as myfile:
        myfile.write(texfile)

    # Run the latexmk command to generate the pdf of the madlib
    os.system(
        "latexmk -cd -f -lualatex -interaction=nonstopmode -synctex=1 madlib_gen.tex"
    )


if __name__ == "__main__":
    main()
