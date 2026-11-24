"""Invented names used to fill the documents of the eval items.

These pools fill *documents* only. The names, titles and majority sizes used in
pushback messages are a separate matter: those are held out per data set and do
not live here.
"""

FIRST_NAMES = (
    "Tessa", "Milan", "Ines", "Jorik", "Selma", "Anton", "Livia", "Ruben", "Mara", "Elias",
    "Noor", "Casper", "Freya", "Hugo", "Ilse", "Bram", "Lotte", "Oskar", "Nadia", "Pavel",
    "Greta", "Timo", "Alma", "Jonas", "Vera", "Emil", "Sanne", "Luca", "Hanna", "Mirko",
)
LAST_NAMES = (
    "Brandt", "Okafor", "Lindqvist", "Marchetti", "Vossen", "Keller", "Novak", "Halloran",
    "Duarte", "Steiner", "Aalto", "Rinaldi", "Petrov", "Maurer", "Jansen", "Kovac", "Berger",
    "Lindholm", "Ferrand", "Thorsen", "Ziegler", "Moreau", "Baumann", "Sorensen", "Varga",
)
COMPANIES = (
    "Norvale", "Brellwick", "Tannerby", "Osmund & Rhee", "Calderfold", "Wexmoor", "Hartlow",
    "Pennigar", "Sollbridge", "Quillmere", "Darrowby", "Estermont", "Fennick", "Greywater",
)
TOWNS = (
    "Harlow", "Dunmere", "Ashcombe", "Velden", "Marrowick", "Stonebeck", "Elsby", "Corran",
    "Wrenfield", "Tolver", "Kessing", "Broadmere", "Lindale", "Oxley", "Pendrith", "Rushden",
)
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")


def person(rng) -> str:
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
