# Dominion
complete Dominion game in python, text-only

Dominion is a popular deck-building game, for 2-4 players.  Each card in the deck gives a player points or money, or lets a player perform a certain action when played.  Each player tries to get the most points before the end of the game.  As of July 2016, I have only programmed the base version.

There are two versions of the game--one that uses a module and a main page, and one that includes all the code in one main page, useful for sharing with a friend who doesn't have python.  (It can be executed in an online REPL, hence the name.)

The list of players is hard-coded, so edit to play.  Add a * at the beginning of the name for a computer player.

The computer (currently) plays a very simple direct strategy.  Its main advantage is that is has a perfect memory of every transaction, and an accurate, dispassionate calculation of when the game is likely to end.
